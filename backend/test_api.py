import requests
import json
import time

def test_chat_api():
    url = "http://localhost:5000/chat"
    # 假设这里是有效的会话ID，需要替换为实际的值
    session_id = "your_valid_session_id"
    # 测试消息
    payload = {
        "session_id": session_id,
        "messages": [
            {
                "role": "user",
                "content": "你好，请做个自我介绍"
            }
        ]
    }

    print("\n=== 开始测试 ===")
    print(f"发送请求到: {url}")
    print(f"请求内容: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        elapsed_time = time.time() - start_time

        print(f"\n请求耗时: {elapsed_time:.2f} 秒")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("\n响应内容:")
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        else:
            print("\n错误响应:")
            print(response.text)

    except requests.exceptions.Timeout:
        print("\n错误: 请求超时")
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"\n错误: {str(e)}")

if __name__ == "__main__":
    # 首先测试服务器是否在运行
    try:
        health_check = requests.get("http://localhost:5000/")
        if health_check.status_code == 200:
            print("后端服务正在运行")
            test_chat_api()
        else:
            print("后端服务返回异常状态码:", health_check.status_code)
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到后端服务，请确保服务器正在运行")