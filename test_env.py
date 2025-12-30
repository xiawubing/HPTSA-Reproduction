import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    print("🚀 正在启动 Playwright (WSL)...")
    async with async_playwright() as p:
        # headless=True 表示不显示界面，速度快
        # headless=False 可以在 Windows 上弹窗看到浏览器 (需要 WSLg 支持)
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()
        
        print("🌐 正在访问示例网站...")
        await page.goto("https://example.com")
        
        # 获取 HTML
        content = await page.content()
        print(f"✅ 成功获取 HTML，长度: {len(content)}")
        
        # 测试 HTML 清洗 (复现论文 3.3 节)
        soup = BeautifulSoup(content, 'html.parser')
        clean_text = soup.body.get_text(strip=True)
        print(f"🧹 清洗后内容: {clean_text}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())