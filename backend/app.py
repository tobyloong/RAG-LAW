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
    #     'is_law_mode': False  # 新增：是否为法律助手模式
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
        is_law_mode = data.get('is_law_mode', False)  # 新增：是否为法律助手模式
        
        if not session_id or session_id not in chat_sessions:
            return jsonify({'error': '无效的会话ID'}), 400
            
        chat_sessions[session_id]['system_prompt'] = system_prompt
        chat_sessions[session_id]['is_law_mode'] = is_law_mode  # 保存模式状态
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('session_id')
        messages = data.get('messages', [])
        deep_thinking = data.get('deep_thinking', False)  # 获取深度思考标志
        
        if not session_id or session_id not in chat_sessions:
            return jsonify({'error': '无效的会话ID'}), 400
            
        print(f"处理会话 {session_id} 的消息: {messages}")
        print(f"深度思考模式: {deep_thinking}")
        
        # 获取该会话的system prompt和模式
        system_prompt = chat_sessions[session_id]['system_prompt']
        is_law_mode = chat_sessions[session_id]['is_law_mode']
        
        # 初始化相关案例列表
        relevant_cases = []
        
        # 如果是法律助手模式且开启了深度思考，使用RAG增强用户的最新问题
        if is_law_mode and deep_thinking and messages:
            latest_user_message = None
            for msg in reversed(messages):
                if msg['role'] == 'user':
                    latest_user_message = msg
                    break
            
            if latest_user_message:
                # 获取相关案例
                relevant_cases = data_processor.find_relevant_cases(latest_user_message['content'])
                
                # 构建增强的提示词
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
            # 根据深度思考模式选择不同的系统提示词
            if deep_thinking:
                full_messages.append({
                    "role": "system",
                    "content": "你是一个乐于助人的人工智能助手，负责分析法律文件及相关内容。在回复时，请遵循以下准则：\n1. 在提供的搜索结果中，每份文件的格式为 [文件 X 开始]...[文件 X 结束]，其中 X 代表每份文件的数字索引。\n2. 引用文件时使用 [citation:X] 格式，其中 X 是文件编号，将引用直接放在相关信息之后。\n3. 在你的回复中要始终包含引用，而不是仅在结尾处。\n4. 如果信息来自多个文件，使用多个引用，例如 [citation:1][citation:2]。\n5. 并非所有的搜索结果都可能相关 —— 评估并仅使用相关信息。\n6. 对于较长的回复，要将其组织成清晰的段落或部分，以提高可读性。\n7. 如果你在提供的文件中找不到答案，请如实说明 —— 不要编造信息。\n8. 有些文件可能是非正式的讨论或百度知道的帖子 —— 相应地调整你的解读。\n9. 在你的回复中尽可能多地使用引用。"
                })
            else:
                full_messages.append({
                    "role": "system",
                    "content": "你是一个专业的法律顾问，请为用户提供简洁、准确的法律建议。"
                })
        
        full_messages.extend(messages)
        
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