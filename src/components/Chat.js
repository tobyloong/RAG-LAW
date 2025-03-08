import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

// 获取当前环境的API地址
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://47.95.196.212:5000';

// 更新默认背景图片为小清新风格
const DEFAULT_BG = 'https://source.unsplash.com/1920x1080/?pastel,minimal,nature';

// 定义主题色
const THEME = {
  primary: 'bg-teal-400 hover:bg-teal-500',    // 主要按钮颜色
  secondary: 'bg-teal-300 hover:bg-teal-400',   // 次要按钮颜色（替换原来的粉色）
  text: 'text-teal-600',                        // 主文字颜色
  subtext: 'text-teal-500',                     // 副标题文字颜色
};

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [isInitialSetup, setIsInitialSetup] = useState(true);
  const messagesEndRef = useRef(null);
  const [backgroundImage, setBackgroundImage] = useState(DEFAULT_BG);
  const [isCustomizingBg, setIsCustomizingBg] = useState(false);
  const fileInputRef = useRef(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const [retryCount, setRetryCount] = useState(0);

  // 修改初始化会话函数
  useEffect(() => {
    const initSession = async () => {
      setIsConnecting(true);
      setError(null);
      
      try {
        const response = await axios.post(`${API_BASE_URL}/start-session`);
        setSessionId(response.data.session_id);
        setIsConnecting(false);
      } catch (error) {
        console.error('Session creation error:', error);
        setError(
          `无法连接到服务器 (${error.message})。请确保：\n` +
          '1. 服务器已启动\n' +
          '2. 设备与服务器在同一网络下\n' +
          '3. 使用正确的服务器地址'
        );
        setIsConnecting(false);
      }
    };

    initSession();
  }, [retryCount]); // 添加retryCount依赖，用于手动重试

  // 添加重试功能
  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  const handleSystemPromptSubmit = async (e) => {
    e.preventDefault();
    if (!systemPrompt.trim() || !sessionId) return;

    try {
      await axios.post(`${API_BASE_URL}/set-system-prompt`, {
        session_id: sessionId,
        system_prompt: systemPrompt
      });
      setIsInitialSetup(false);
    } catch (error) {
      setError('设置系统提示词失败');
      console.error('System prompt setup error:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !sessionId) return;

    const userMessage = {
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      console.log('发送请求到后端，消息内容:', [...messages, userMessage]);
      
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        session_id: sessionId,
        messages: [...messages, userMessage]
      }, {
        timeout: 120000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('收到后端响应:', response.data);

      if (!response.data || !response.data.choices || !response.data.choices[0]) {
        throw new Error('后端返回数据格式不正确');
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.data.choices[0].message.content
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('详细错误信息:', error);
      console.error('错误响应:', error.response?.data);
      
      setError(error.message || '未知错误');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `发生错误：${error.response?.data?.error || error.message || '与服务器通信时出错'}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackgroundChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setBackgroundImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const resetBackground = () => {
    setBackgroundImage(DEFAULT_BG);
  };

  // 添加特殊祝福处理函数
   const handleSpecialGreeting = async () => {
    const specialPrompt = '你是一只可爱的小浣熊，你现在要祝你的女朋友三八妇女节快乐，请称呼她为"蛙蛙"，并自称"熊熊"';
    setSystemPrompt(specialPrompt);
    
    try {
      // 设置系统提示词
      await axios.post(`${API_BASE_URL}/set-system-prompt`, {
        session_id: sessionId,
        system_prompt: specialPrompt
      });
      
      // 直接触发一条问候消息
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        session_id: sessionId,
        messages: [{
          role: "user",
          content: "请开始你的节日祝福"
        }]
      });

      if (response.data && response.data.choices && response.data.choices[0]) {
        setMessages([{
          role: 'assistant',
          content: response.data.choices[0].message.content
        }]);
      }
      
      setIsInitialSetup(false);
    } catch (error) {
      setError('设置特殊祝福失败');
      console.error('Special greeting error:', error);
    }
   };

  // 背景设置面板
  const BackgroundSettings = () => (
    <div className="absolute top-16 right-4 bg-white rounded-lg shadow-lg p-4 z-10">
      <div className="space-y-4">
        <button
          onClick={() => fileInputRef.current.click()}
          className={`w-full px-4 py-2 ${THEME.primary} text-white rounded hover:bg-teal-500 transition-all transform hover:scale-105`}
        >
          选择图片
        </button>
        <button
          onClick={resetBackground}
          className="w-full px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          恢复默认
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleBackgroundChange}
          className="hidden"
        />
      </div>
    </div>
  );

  if (isInitialSetup) {
    return (
      <div 
        className="flex flex-col h-screen bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url(${backgroundImage})`,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backgroundBlendMode: 'overlay'
        }}
      >
        <div className="bg-white/80 shadow-sm p-4 backdrop-blur-sm">
          <h1 className="text-2xl font-bold text-center text-teal-600" 
              style={{ 
                fontFamily: "'AlibabaPuHuiTi', system-ui, sans-serif",
                letterSpacing: '1px'
              }}>
            AI 助手
            <div className={`text-sm mt-1 ${THEME.subtext} font-bold tracking-wider`}
                 style={{ 
                   fontFamily: "'AlibabaPuHuiTi', system-ui, sans-serif",
                 }}>
              小浣熊制作
            </div>
          </h1>
        </div>
        <div className="flex-1 flex items-center justify-center p-4">
          {isConnecting ? (
            <div className="text-center bg-white/90 backdrop-blur-sm p-6 rounded-lg shadow-md">
              <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p>正在连接服务器...</p>
            </div>
          ) : error ? (
            <div className="bg-white/90 backdrop-blur-sm p-6 rounded-lg shadow-md max-w-lg">
              <div className="text-red-500 mb-4 whitespace-pre-line">{error}</div>
              <button
                onClick={handleRetry}
                className={`w-full px-4 py-2 ${THEME.secondary} text-white rounded hover:bg-teal-400 transition-all transform hover:scale-105`}
              >
                重试连接
              </button>
              <div className="mt-4 text-sm text-gray-600">
                <p className="font-semibold">技术信息：</p>
                <p className="font-mono break-all">{API_BASE_URL}</p>
              </div>
            </div>
          ) : (
            <div className="w-full max-w-lg">
              <form onSubmit={handleSystemPromptSubmit} className="mb-4">
                <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-md p-6">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    请设置AI助手的角色定位：
                  </label>
                  <textarea
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 min-h-[150px]"
                    placeholder="例如：你是一位经验丰富的心理咨询师，善于倾听和提供建议..."
                  />
                  {error && (
                    <div className="text-red-500 text-sm mt-2">
                      {error}
                    </div>
                  )}
                  <button
                    type="submit"
                    className={`mt-4 w-full px-6 py-3 ${THEME.primary} text-white rounded-lg transition-all duration-200 transform hover:scale-105`}
                  >
                    开始对话
                  </button>
                </div>
              </form>
              
              {/* 添加特殊祝福按钮 */}
              <button
                onClick={handleSpecialGreeting}
                className="w-full px-6 py-4 bg-gradient-to-r from-teal-400 to-teal-500 text-white rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
                style={{ 
                  fontFamily: "'AlibabaPuHuiTi', system-ui, sans-serif",
                  letterSpacing: '2px'
                }}
              >
                <span className="flex items-center justify-center">
                  <span className="mr-2">🎀</span>
                  给蛙蛙的小惊喜
                  <span className="ml-2">💝</span>
                </span>
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div 
      className="flex flex-col h-screen bg-cover bg-center bg-no-repeat"
      style={{
        backgroundImage: `url(${backgroundImage})`,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        backgroundBlendMode: 'overlay'
      }}
    >
      {/* 头部 */}
      <div className="bg-white/80 shadow-sm p-4 backdrop-blur-sm relative">
        <h1 className="text-2xl font-bold text-center text-teal-600" 
            style={{ 
              fontFamily: "'AlibabaPuHuiTi', system-ui, sans-serif",
              letterSpacing: '1px'
            }}>
          AI 助手
          <div className={`text-sm mt-1 ${THEME.subtext} font-bold tracking-wider`}
               style={{ 
                 fontFamily: "'AlibabaPuHuiTi', system-ui, sans-serif",
               }}>
            小浣熊制作
          </div>
        </h1>
        <button
          onClick={() => setIsCustomizingBg(!isCustomizingBg)}
          className="absolute right-4 top-4 text-gray-600 hover:text-gray-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
        {isCustomizingBg && <BackgroundSettings />}
        {error && (
          <div className="mt-2 text-red-500 text-sm text-center">
            {error}
          </div>
        )}
      </div>

      {/* 消息区域 */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 bg-white/80 backdrop-blur-sm p-6 rounded-lg">
              <p className="text-xl mb-2">👋 欢迎使用 AI 助手</p>
              <p>输入消息开始对话吧！</p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 ${
                message.role === 'user' ? 'text-right' : 'text-left'
              }`}
            >
              <div
                className={`inline-block message-bubble ${
                  message.role === 'user'
                    ? 'message-bubble-user'
                    : 'message-bubble-assistant'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="text-left">
            <div className="inline-block p-4 rounded-lg bg-white/90 backdrop-blur-sm shadow">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <form onSubmit={handleSubmit} className="p-4 bg-white/80 backdrop-blur-sm border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 input-cute bg-white/90"
            placeholder="输入你的问题..."
          />
          <button
            type="submit"
            disabled={isLoading}
            className={`px-6 py-3 ${THEME.primary} text-white rounded-lg disabled:bg-gray-300 transition-all transform hover:scale-105`}
          >
            {isLoading ? '发送中...' : '发送'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat;
