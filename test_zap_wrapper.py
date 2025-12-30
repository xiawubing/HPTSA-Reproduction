"""
测试 ZAP Wrapper 是否能正确连接到 ZAP API
"""
import requests
import time
from tools.zap_wrapper import ZAP_API_URL, get_zap_alerts, start_zap_scan

def test_zap_connection():
    """步骤 1: 测试基础连接 - 检查 ZAP 是否运行"""
    print("=" * 60)
    print("步骤 1: 测试 ZAP API 基础连接")
    print("=" * 60)
    
    try:
        # 测试最简单的 API - 获取版本信息
        response = requests.get(f"{ZAP_API_URL}/JSON/core/view/version/", timeout=5)
        
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ ZAP API 连接成功！")
            print(f"   ZAP 版本: {version_info.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ ZAP API 返回错误状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 ZAP API")
        print("   请确保 ZAP 容器正在运行:")
        print("   docker ps | grep zap")
        print("   或者启动 ZAP 容器:")
        print("   cd sandbox && docker-compose up -d zap")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {str(e)}")
        return False

def test_get_alerts():
    """步骤 2: 测试 get_zap_alerts 函数"""
    print("\n" + "=" * 60)
    print("步骤 2: 测试 get_zap_alerts() 函数")
    print("=" * 60)
    
    try:
        print("📋 调用 get_zap_alerts()...")
        result = get_zap_alerts.invoke({})  # LangChain tool 调用方式
        
        print("✅ get_zap_alerts() 调用成功！")
        print(f"   返回结果长度: {len(result)} 字符")
        print(f"   结果预览:\n{result[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ get_zap_alerts() 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_spider_scan():
    """步骤 3: 测试 spider scan（快速测试）"""
    print("\n" + "=" * 60)
    print("步骤 3: 测试 spider scan（爬虫扫描）")
    print("=" * 60)
    
    # 使用一个简单的测试 URL
    test_url = "http://localhost:8082"  # 你的目标应用
    
    print(f"🎯 目标 URL: {test_url}")
    print("⏳ 开始 spider scan（这可能需要 10-30 秒）...")
    
    try:
        result = start_zap_scan.invoke({"url": test_url, "scan_type": "spider"})
        
        print("✅ spider scan 完成！")
        print(f"   返回结果长度: {len(result)} 字符")
        print(f"   结果预览:\n{result[:300]}...")
        return True
        
    except Exception as e:
        print(f"❌ spider scan 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_api_call():
    """步骤 0: 直接测试 ZAP API（不使用 wrapper）"""
    print("=" * 60)
    print("步骤 0: 直接测试 ZAP API（不使用 wrapper）")
    print("=" * 60)
    
    # 测试几个关键的 API 端点
    test_endpoints = [
        "/JSON/core/view/version/",
        "/JSON/core/view/alerts/",
        "/JSON/spider/view/scans/",
    ]
    
    for endpoint in test_endpoints:
        try:
            url = f"{ZAP_API_URL}{endpoint}"
            print(f"\n📡 测试端点: {endpoint}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ 成功 (状态码: {response.status_code})")
                data = response.json()
                print(f"   响应键: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            else:
                print(f"   ⚠️  状态码: {response.status_code}")
                print(f"   响应: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ 失败: {str(e)}")

def main():
    """运行所有测试"""
    print("\n" + "🔍 ZAP Wrapper 测试套件" + "\n")
    
    # 步骤 0: 直接测试 API
    test_direct_api_call()
    
    # 步骤 1: 测试连接
    if not test_zap_connection():
        print("\n❌ 基础连接失败，停止测试")
        return
    
    # 步骤 2: 测试 get_alerts
    test_get_alerts()
    
    # 步骤 3: 测试 spider scan（可选，需要时间）
    print("\n" + "=" * 60)
    user_input = input("是否运行 spider scan 测试？(需要 10-30 秒) [y/N]: ")
    if user_input.lower() == 'y':
        test_spider_scan()
    else:
        print("⏭️  跳过 spider scan 测试")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()