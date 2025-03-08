from flask import Flask, request, jsonify, session
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import uuid

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 设置session密钥
CORS(app, supports_credentials=True)  # 启用跨域支持credentials

# 修改用户会话的数据结构
chat_sessions = {
    # session_id: {
    #     'messages': [],
    #     'system_prompt': None
    # }
}

# 初始化OpenAI客户端
client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# 添加一个测试路由
@app.route('/')
def home():
    return "Chat API is running!"

@app.route('/start-session', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = {
        'messages': [],
        'system_prompt': None
    }
    return jsonify({"session_id": session_id})

@app.route('/set-system-prompt', methods=['POST'])
def set_system_prompt():
    try:
        data = request.json
        session_id = data.get('session_id')
        system_prompt = data.get('system_prompt')
        
        if not session_id or session_id not in chat_sessions:
            return jsonify({'error': '无效的会话ID'}), 400
            
        chat_sessions[session_id]['system_prompt'] = system_prompt
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('session_id')
        messages = data.get('messages', [])
        
        if not session_id or session_id not in chat_sessions:
            return jsonify({'error': '无效的会话ID'}), 400
            
        print(f"处理会话 {session_id} 的消息: {messages}")
        
        # 获取该会话的system prompt
        system_prompt = chat_sessions[session_id]['system_prompt']
        
        # 构建完整的消息列表
        full_messages = []
        if system_prompt:
            full_messages.append({
                "role": "system",
                "content": system_prompt
            })
        full_messages.extend(messages)
        
        # 更新会话历史
        chat_sessions[session_id]['messages'] = messages
        
        start_time = time.time()
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=full_messages,
                stream=False,
                timeout=60
            )
            print(f"API响应时间: {time.time() - start_time}秒")
            
            assistant_message = {
                "role": "assistant",
                "content": response.choices[0].message.content
            }
            chat_sessions[session_id]['messages'].append(assistant_message)
            
            return jsonify({
                "choices": [{
                    "message": assistant_message
                }]
            })
            
        except Exception as e:
            print(f"API调用错误: {str(e)}")
            return jsonify({'error': f"API调用失败: {str(e)}"}), 500
            
    except Exception as e:
        print(f"服务器错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 修改监听地址和端口
    app.run(
        host='0.0.0.0',  # 允许所有IP访问
        port=5000,
        debug=True
    ) 