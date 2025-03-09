from flask import Flask, request, jsonify, session
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import time
import uuid
from data_processor import get_data_processor

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 设置session密钥
app.config['JSON_AS_ASCII'] = False  # 确保JSON响应中的中文正确显示
CORS(app, supports_credentials=True)  # 启用跨域支持credentials

# 修改用户会话的数据结构
chat_sessions = {
    # session_id: {
    #     'messages': [],
    #     'system_prompt': None,
    #     'is_law_mode': False,  # 是否为法律助手模式
    #     'law_cases_count': 3,  # 法条检索数量
    #     'qa_cases_count': 3    # 问答检索数量
    # }
}

# 配置OpenAI
openai.api_key = os.getenv('DEEPSEEK_API_KEY')
openai.api_base = "https://api.deepseek.com/v1"

# 初始化数据处理器
print("正在初始化数据处理器...")
data_processor = get_data_processor()
print("数据处理器初始化完成")

# 添加一个测试路由
@app.route('/')
def home():
    return "Chat API is running!"

@app.route('/start-session', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = {
        'messages': [],
        'system_prompt': None,
        'is_law_mode': False
    }
    return jsonify({"session_id": session_id})

@app.route('/set-system-prompt', methods=['POST'])
def set_system_prompt():
    try:
        data = request.json
        session_id = data.get('session_id')
        system_prompt = data.get('system_prompt')
        is_law_mode = data.get('is_law_mode', False)
        law_cases_count = data.get('law_cases_count', 3)
        qa_cases_count = data.get('qa_cases_count', 3)
        
        if not session_id or session_id not in chat_sessions:
            return jsonify({'error': '无效的会话ID'}), 400
            
        chat_sessions[session_id].update({
            'system_prompt': system_prompt,
            'is_law_mode': is_law_mode,
            'law_cases_count': law_cases_count,
            'qa_cases_count': qa_cases_count
        })
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('session_id')
        messages = data.get('messages', [])
        deep_thinking = data.get('deep_thinking', False)
        
        if not session_id or session_id not in chat_sessions:
            return jsonify({'error': '无效的会话ID'}), 400
            
        session = chat_sessions[session_id]
        system_prompt = session['system_prompt']
        is_law_mode = session['is_law_mode']
        law_cases_count = session.get('law_cases_count', 3)
        qa_cases_count = session.get('qa_cases_count', 3)
        
        relevant_cases = []
        
        if is_law_mode and deep_thinking and messages:
            latest_user_message = None
            for msg in reversed(messages):
                if msg['role'] == 'user':
                    latest_user_message = msg
                    break
            
            if latest_user_message:
                relevant_cases = data_processor.find_relevant_cases(
                    latest_user_message['content'],
                    law_top_k=law_cases_count,
                    qa_top_k=qa_cases_count
                )
                
                context = "搜索结果：\n\n"
                for i, case in enumerate(relevant_cases, 1):
                    context += f"[文件 {i} 开始]\n{case}\n[文件 {i} 结束]\n\n"
                
                enhanced_prompt = f"""用户问题: {latest_user_message['content']}\n\n{context}\n请根据以上搜索结果回答问题。记住：
1. 引用文件时使用 [citation:X] 格式
2. 在回答中始终包含引用
3. 如果信息来自多个文件，使用多个引用
4. 仅使用相关的搜索结果
5. 将回答组织成清晰的段落
6. 如果在提供的文件中找不到答案，请如实说明

请先在 <think> 标签之间解释你的思考过程，然后给出最终答案。"""

                # 替换最后一条用户消息
                messages_before = messages[:-1]
                messages = messages_before + [{
                    "role": "user",
                    "content": enhanced_prompt
                }]
        
        # 构建完整的消息列表
        full_messages = []
        if system_prompt:
            full_messages.append({
                "role": "system",
                "content": system_prompt  # 使用会话中保存的system prompt
            })
        
        # 只添加用户和助手的消息，不要重复添加system消息
        for msg in messages:
            if msg['role'] != 'system':  # 跳过消息列表中的system消息
                full_messages.append(msg)
        
        # 更新会话历史
        chat_sessions[session_id]['messages'] = messages
        
        start_time = time.time()
        
        try:
            # 打印完整的请求内容
            print("\n=== 发送给Deepseek API的请求内容 ===")
            print("系统提示词:", full_messages[0] if full_messages and full_messages[0]['role'] == 'system' else "无")
            print("\n用户最新消息:", messages[-1] if messages else "无")
            print("\n相关案例:", relevant_cases)
            print("\n完整消息列表:", full_messages)
            print("================================\n")
            
            response = openai.ChatCompletion.create(
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
            
            # 返回响应时包含相关案例
            return jsonify({
                "choices": [{
                    "message": assistant_message
                }],
                "related_cases": relevant_cases if is_law_mode else []
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