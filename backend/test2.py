# test_start_session.py
import requests

# 替换为你的后端地址
API_BASE_URL = 'http://localhost:5000'  # 确保地址和端口正确

def test_start_session():
    try:
        # 打印完整的请求 URL
        print(f"Testing endpoint: {API_BASE_URL}/start-session")

        # 发送 POST 请求
        response = requests.post(f"{API_BASE_URL}/start-session")

        # 打印响应状态码和数据
        print(f"Response status code: {response.status_code}")
        print(f"Response data: {response.json()}")

        # 检查响应是否符合预期
        if response.status_code == 200 and response.json().get('session_id'):
            print(f"✅ Test passed: session_id is {response.json()['session_id']}")
        else:
            print("❌ Test failed: response does not contain session_id or status code is not 200")
    except requests.exceptions.RequestException as e:
        # 捕获并打印错误
        print("❌ Test failed with error:")
        if e.response:
            # 服务器返回了错误响应
            print(f"Status code: {e.response.status_code}")
            print(f"Error data: {e.response.text}")
        else:
            # 其他错误（如网络问题）
            print(f"Error: {e}")

if __name__ == "__main__":
    test_start_session()
