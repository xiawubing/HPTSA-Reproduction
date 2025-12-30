import os
from langchain.tools import tool
from playwright.sync_api import sync_playwright
from .browser_utils import clean_html

# keep global browser to keep the real-time status
playwright = sync_playwright().start()

browser = playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])

context = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

page = context.new_page()


@tool
def navigate_tool(url: str):
    """Navigates the browser to a specific URL and returns the simplified HTML."""
    try:
        # use global page object
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        content = page.content()
        return clean_html(content)
    except Exception as e:
        return f"Error exploring {url}: {str(e)}"

@tool
def click_tool(selector: str):
    """Clicks on an element specified by the CSS selector."""
    try:
        page.wait_for_selector(selector, state="visible", timeout=5000)
        page.click(selector)
        page.wait_for_load_state("networkidle")
        return clean_html(page.content())
    except Exception as e:
        return f"Error clicking {selector}: {str(e)}"

@tool
def fill_form_tool(selector: str, text: str):
    """Fills a form field (input/textarea) with text."""
    try:
        page.wait_for_selector(selector, state="visible", timeout=5000)
        page.fill(selector, text)
        return f"Filled {selector} successfully."
    except Exception as e:
        return f"Error filling form: {str(e)}"

@tool
def upload_file_tool(selector: str, file_path: str):
    """
    Uploads a file to an input element (type='file').
    
    Args:
        selector: CSS selector for the file input (e.g., 'input[name="image"]')
        file_path: Absolute path to the file on the machine.
    """
    try:
        if not os.path.exists(file_path):
             return f"Error: File not found at {file_path}. Please check the path."

        page.wait_for_selector(selector, state="attached", timeout=5000)
        
        page.set_input_files(selector, file_path)
        
        return f"Successfully uploaded {file_path} to {selector}"
    except Exception as e:
        return f"Error uploading file: {str(e)}"

@tool
def submit_form_tool(selector: str = "form"):
    """Submits a form specified by selector and returns the resulting HTML."""
    try:
        submit_btn = f"{selector} input[type='submit'], {selector} button[type='submit'], {selector} button"
        
        page.click(submit_btn)
        
        page.wait_for_load_state("networkidle")
        return clean_html(page.content())
    except Exception as e:
        return f"Error submitting form: {str(e)}"

@tool
def get_current_url() -> str:
    """Returns the current URL of the browser."""
    try:
        return page.url
    except Exception as e:
        return f"Error getting URL: {str(e)}"

@tool
def extract_forms() -> str:
    """Extracts all forms from the current page and returns their details."""
    try:
        forms = page.query_selector_all("form")
        form_details = []
        for i, form in enumerate(forms):
            action = form.get_attribute("action") or ""
            method = form.get_attribute("method") or "GET"
            
            inputs = form.query_selector_all("input, textarea, select")
            input_details = []
            for inp in inputs:
                input_type = inp.get_attribute("type") or "text"
                input_name = inp.get_attribute("name") or ""
                input_id = inp.get_attribute("id") or ""
                
                extra_info = ""
                if input_type == "file":
                    extra_info = " [Use upload_file_tool for this!]"
                
                input_details.append(f"  - {input_type}: name={input_name}, id={input_id}{extra_info}")
                
            form_details.append(f"Form {i+1}: action={action}, method={method}\n" + "\n".join(input_details))
            
        return "\n\n".join(form_details) if form_details else "No forms found"
    except Exception as e:
        return f"Error extracting forms: {str(e)}"