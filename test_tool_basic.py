from tools.sqlmap_wrapper import _run_sqlmap_impl as run_sqlmap  # 使用原始函数进行测试

def test_basic():
    # 这里填你 Docker 靶场的首页地址
    target_url = "http://localhost:8082/write-journal.php" 
    
    print(f"[*] 开始扫描目标: {target_url}")
    print("[*] 这可能需要 1-2 分钟，请耐心等待...")
    
    # 我们只用 level=1 来快速测试，避免跑太久
    result = run_sqlmap(url=target_url, options="--level=1 --batch")
    
    print("-" * 30)
    print("【工具返回结果】")
    print(result)
    print("-" * 30)

if __name__ == "__main__":
    test_basic()