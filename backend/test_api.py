# test_api_integration.py
import unittest
import json
import time
from app import app, chat_sessions

class TestChatAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        chat_sessions.clear()  # 每次测试前清空会话

    def test_01_session_management(self):
        """测试会话创建和基本流程"""
        # 创建新会话
        response = self.client.post('/start-session')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('session_id', data)
        session_id = data['session_id']
        
        # 验证会话数据结构
        self.assertIn(session_id, chat_sessions)
        self.assertIsNone(chat_sessions[session_id]['system_prompt'])
        self.assertEqual(chat_sessions[session_id]['messages'], [])

    def test_02_system_prompt_flow(self):
        """测试系统提示设置和对话集成"""
        # 创建会话
        session_id = self.client.post('/start-session').get_json()['session_id']
        
        # 设置系统提示
        prompt_data = {
            'session_id': session_id,
            'system_prompt': '你是一个数学家，用中文回答，只回答数学问题'
        }
        response = self.client.post('/set-system-prompt', json=prompt_data)
        self.assertEqual(response.status_code, 200)
        
        # 验证提示设置
        self.assertEqual(chat_sessions[session_id]['system_prompt'], prompt_data['system_prompt'])
        
        # 发送数学问题
        math_question = {
            'session_id': session_id,
            'messages': [{'role': 'user', 'content': '2+2等于多少？'}]
        }
        start_time = time.time()
        response = self.client.post('/chat', json=math_question)
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        response_data = response.get_json()
        self.assertIn('choices', response_data)
        self.assertTrue(len(response_data['choices']) > 0)
        assistant_message = response_data['choices'][0]['message']
        self.assertIn('content', assistant_message)
        
        # 验证响应内容
        content = assistant_message['content'].lower()
        self.assertIn('4', content)  # 确保数学回答正确
        self.assertIn('等于', content)  # 验证中文回复
        
        # 验证历史记录
        session_data = chat_sessions[session_id]
        self.assertEqual(len(session_data['messages']), 2)  # 用户消息 + 助手回复
        self.assertEqual(session_data['messages'][0]['role'], 'user')
        self.assertEqual(session_data['messages'][1]['role'], 'assistant')

    def test_03_context_maintenance(self):
        """测试多轮对话上下文维护"""
        session_id = self.client.post('/start-session').get_json()['session_id']
        
        # 第一轮对话
        first_msg = {
            'session_id': session_id,
            'messages': [{'role': 'user', 'content': '中国的首都是哪里？'}]
        }
        response = self.client.post('/chat', json=first_msg)
        first_reply = response.get_json()['choices'][0]['message']['content']
        self.assertIn('北京', first_reply)
        
        # 第二轮对话（需要包含上下文）
        second_msg = {
            'session_id': session_id,
            'messages': [{'role': 'user', 'content': '那里有多少人口？'}]
        }
        response = self.client.post('/chat', json=second_msg)
        second_reply = response.get_json()['choices'][0]['message']['content']
        
        # 验证上下文理解
        self.assertIn('北京', second_reply)
        self.assertRegex(second_reply, r'\d+万|\d+百万')  # 匹配人口数字

    def test_04_error_handling(self):
        """测试异常情况处理"""
        # 无效会话ID
        invalid_request = {
            'session_id': 'invalid_id',
            'messages': [{'role': 'user', 'content': '测试'}]
        }
        response = self.client.post('/chat', json=invalid_request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('无效的会话ID', response.get_json()['error'])
        
        # 空消息列表
        session_id = self.client.post('/start-session').get_json()['session_id']
        empty_msg = {'session_id': session_id, 'messages': []}
        response = self.client.post('/chat', json=empty_msg)
        self.assertEqual(response.status_code, 400)
        self.assertIn('不能为空', response.get_json()['error'])
        
        # 错误的消息格式
        bad_format = {
            'session_id': session_id,
            'messages': '这不是列表'
        }
        response = self.client.post('/chat', json=bad_format)
        self.assertEqual(response.status_code, 400)
        self.assertIn('必须为列表', response.get_json()['error'])

    def test_05_system_prompt_integration(self):
        """测试系统提示集成到对话"""
        session_id = self.client.post('/start-session').get_json()['session_id']
        
        # 设置角色提示
        self.client.post('/set-system-prompt', json={
            'session_id': session_id,
            'system_prompt': '你是一本百科全书，用中文回答，只说事实'
        })
        
        # 发送测试问题
        response = self.client.post('/chat', json={
            'session_id': session_id,
            'messages': [{'role': 'user', 'content': '请讲一个故事'}]
        })
        content = response.get_json()['choices'][0]['message']['content']
        
        # 验证系统提示生效
        self.assertNotIn('故事', content)  # 根据提示应该拒绝讲故事
        self.assertIn('事实', content)  # 应该返回事实性内容

if __name__ == '__main__':
    unittest.main(verbosity=2)