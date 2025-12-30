# tools/browser_session.py
import asyncio
from playwright.async_api import async_playwright 
from langchain_core.tools import StructuredTool
from .browser_utils import clean_html

class BrowserSession:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.captured_alerts = []
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        print("[*] Starting new browser session (Async)...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=500, 
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.page = await self.context.new_page()
        self.page.on("dialog", self._handle_dialog)
        
        self.page.on("response", lambda response: self._log_response(response))

    def _log_response(self, response):
        if response.request.resource_type in ["document", "xhr", "fetch"]:
            status = response.status
            url = response.url
            if status >= 400:
                print(f"[NETWORK ERROR] {status} {response.request.method} {url}")
            elif "add-journal.php" in url:
                print(f"[NETWORK SUBMIT] {status} {response.request.method} {url}")

    async def stop(self):
        print("[*] Closing browser session...")
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()

    async def _handle_dialog(self, dialog):
        message = dialog.message
        print(f"[*] CAPTURED DIALOG: {message}") 
        self.captured_alerts.append(message)
        try:
            await dialog.accept()
        except Exception as e:
            print(f"Error handling dialog: {e}")

    async def _navigate(self, url: str) -> str:
        async with self.lock:
            try:
                await self.page.goto(url, timeout=50000)
                await self.page.wait_for_load_state("networkidle")
                print("[*] Waiting 2s for potential XSS alerts...")
                await self.page.wait_for_timeout(2000)
                content = await self.page.content()
                return clean_html(content)
            except Exception as e:
                return f"Error navigating to {url}: {str(e)}"

    async def _click(self, selector: str) -> str:
        async with self.lock:
            try:
                await self.page.wait_for_selector(selector, state="visible", timeout=5000)
                
                if "submit" in selector.lower() or "btn" in selector.lower():
                    print(f"[*] Attempting Form Submission via {selector}...")
                    
                    try:
                        async with self.page.expect_navigation(timeout=10000):
                            await self.page.click(selector)
                        print("[*] Navigation detected after submit.")
                    except Exception:
                        print("[*] Warning: No navigation detected after submit (AJAX or validation error).")
                        await self.page.wait_for_load_state("networkidle", timeout=3000)
                else:
                    await self.page.click(selector)
                    await self.page.wait_for_load_state("networkidle")
                
                content = await self.page.content()
                
                if "<body></body>" in content.replace(" ", ""):
                    return "Error: Server returned empty body (Blank Page). Check Network Logs above for 500 Errors."
                    
                return clean_html(content)
            except Exception as e:
                return f"Error clicking {selector}: {str(e)}"

    async def _fill(self, selector: str, text: str) -> str:
        async with self.lock:
            try:
                await self.page.wait_for_selector(selector, state="visible", timeout=5000)
                input_type = await self.page.evaluate(
                    "(sel) => document.querySelector(sel).type", 
                    selector
                )

                if input_type == 'date':
                    await self.page.evaluate(
                        "([sel, val]) => { document.querySelector(sel).value = val; }", 
                        [selector, text]
                    )
                    await self.page.evaluate(
                        "(sel) => { document.querySelector(sel).dispatchEvent(new Event('input', {bubbles: true})); }",
                        selector
                    )
                    return f"Filled date field {selector} via JS assignment."

                await self.page.click(selector)
                
                is_mac = await self.page.evaluate("navigator.platform.toUpperCase().indexOf('MAC') >= 0")
                modifier = "Meta" if is_mac else "Control"
                
                await self.page.keyboard.press(f"{modifier}+A")
                await self.page.wait_for_timeout(50) 
                await self.page.keyboard.press("Backspace")
                await self.page.keyboard.type(text, delay=50)
                
                await self.page.evaluate(
                    "(sel) => { document.querySelector(sel).dispatchEvent(new Event('blur', {bubbles: true})); }",
                    selector
                )
                
                return f"Filled {selector} successfully."
                
            except Exception as e:
                print(f"[DEBUG ERROR] Failed to fill {selector}: {str(e)}")
                return f"Error filling {selector}: {str(e)}"

    async def _get_url(self) -> str:
        return self.page.url

    async def _extract_forms(self) -> str:
        async with self.lock:
            try:
                forms_info = await self.page.evaluate("""() => {
                    const forms = Array.from(document.querySelectorAll('form'));
                    return forms.map((f, i) => {
                        const inputs = Array.from(f.querySelectorAll('input, textarea, select'));
                        const inputDetails = inputs.map(inp => 
                            `Type: ${inp.type || 'text'}, Name: ${inp.name || 'Unnamed'}, ID: ${inp.id || 'NoID'}`
                        ).join('\\n    ');
                        return `Form ${i+1}: Action=${f.getAttribute('action') || ''}, Method=${f.getAttribute('method') || 'GET'}\\n    ${inputDetails}`;
                    });
                }""")
                return "\n\n".join(forms_info) if forms_info else "No forms found"
            except Exception as e:
                return f"Error extracting forms: {str(e)}"

    async def _upload_file(self, selector: str, file_path: str) -> str:
        async with self.lock:
            import os
            if not os.path.isabs(file_path):
                real_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
            else:
                real_path = file_path
                
            if not os.path.exists(real_path):
                fallback = os.path.abspath(os.path.join(os.getcwd(), "sandbox", "test.jpg"))
                if os.path.exists(fallback):
                   real_path = fallback

            if not os.path.exists(real_path):
                return f"Error: File not found at {real_path}"
                
            try:
                await self.page.wait_for_selector(selector, state="attached", timeout=5000)
                await self.page.set_input_files(selector, real_path)
                return f"Successfully uploaded {real_path} to {selector}"
            except Exception as e:
                return f"Error uploading file: {str(e)}"

    async def _check_alerts(self) -> str:
        if not self.captured_alerts:
            return "No alerts/dialogs triggered so far."
        return f"CAPTURED ALERTS (XSS PROOF): {str(self.captured_alerts)}"

    def get_tools(self):
        return [
            StructuredTool.from_function(coroutine=self._navigate, name="navigate_tool", description="Navigates the browser to a specific URL."),
            StructuredTool.from_function(coroutine=self._click, name="click_tool", description="Clicks on an element specified by the CSS selector."),
            StructuredTool.from_function(coroutine=self._fill, name="fill_form_tool", description="Fills a form field. For Date fields, use YYYY-MM-DD format."),
            StructuredTool.from_function(coroutine=self._get_url, name="get_current_url", description="Returns the current URL."),
            StructuredTool.from_function(coroutine=self._extract_forms, name="extract_forms", description="Extracts forms from the current page."),
            StructuredTool.from_function(coroutine=self._upload_file, name="upload_file_tool", description="Uploads a file to an input element."),
            StructuredTool.from_function(coroutine=self._check_alerts, name="check_alerts_tool", description="Checks for JavaScript alert popups."),
        ]