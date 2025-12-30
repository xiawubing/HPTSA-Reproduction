import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- 这是核心的清洗函数 (以后 Agent 也会用这个) ---
def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. 移除对 AI 理解网页逻辑无用的标签
    # script/style: JS和CSS代码，AI 不需要看源码，只需要看结构
    # svg/img/video: AI 目前不处理视觉图像
    # meta/link: 网页元数据，通常不包含攻击面
    for tag in soup(['script', 'style', 'svg', 'img', 'video', 'iframe', 'meta', 'link', 'noscript']):
        tag.decompose()
    
    # 2. 移除注释 (防止注释里的干扰信息)
    for element in soup(text=lambda text: isinstance(text,  type(soup.new_string("").__class__)) and "Comment" in str(type(text))):
        element.extract()

    # 3. 获取 Body 内容 (如果网页有 body 的话)
    content = soup.body if soup.body else soup

    # 4. 使用 prettify() 让输出格式化，方便人类检查结构
    return content.prettify()

def main():
    target_url = "http://localhost:8082/"
    
    print(f"[*] 正在尝试访问: {target_url}")
    print("[*] 启动 Headless 浏览器...")

    with sync_playwright() as p:
        # headless=True 表示不显示浏览器窗口 (后台运行)
        # 调试时可以改成 headless=False 看着浏览器打开
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 访问目标网页
            response = page.goto(target_url)
            
            # 等待网页加载完成 (networkidle 表示网络空闲了，通常意味着加载完了)
            page.wait_for_load_state("networkidle")
            
            # 获取网页标题
            title = page.title()
            print(f"[+] 网页标题: {title}")
            
            # 获取原始 HTML
            raw_html = page.content()
            
            # 进行清洗
            cleaned_html = clean_html(raw_html)
            
            print("-" * 30)
            print("【Agent 将看到的最终 HTML 视图】")
            print("-" * 30)
            print(cleaned_html)
            print("-" * 30)
            
            # 简单的自动检查
            if "<form" in cleaned_html or "<input" in cleaned_html:
                print("✅ 测试通过：在 HTML 中发现了表单或输入框，Agent 可以尝试注入。")
            else:
                print("⚠️ 警告：未发现明显的表单交互元素，可能是页面为空或加载失败。")
                
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            print("提示：请检查 Docker 容器是否正在运行，以及端口是否真的是 8082。")
            
        finally:
            browser.close()

if __name__ == "__main__":
    main()