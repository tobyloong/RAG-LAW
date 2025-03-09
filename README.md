# AI 智能对话助手

一个基于 React 和 Flask 的智能对话系统，支持通用对话和专业法律咨询两种模式。项目特色是优雅的界面设计和完善的检索增强生成（RAG）功能。

## ✨ 功能特点

### 🤖 双模式支持
- **通用模式（绿色主题）**
  - 完全自定义的角色设定
  - 用户主导的对话流程
  - 清新自然的界面风格

- **法律模式（红色主题）**
  - 专业的法律知识检索
  - 支持法条和案例引用
  - 深度思考模式选项

### 📚 智能检索系统
- 支持法条和问答双重检索
- 可调节检索数量（1-10条）
- 引用内容智能分类（法条/问答/案例）
- 点击引用快速定位原文

### 💡 交互体验
- 思维链可视化展示
- 代码块一键复制
- 数学公式渲染支持
- 引用内容高亮显示

### 🎨 个性化设置
- 自定义背景图片
- 响应式面板设计
- 优雅的动画过渡
- 面板互斥自动处理

## 🛠️ 技术栈

### 前端
- React 18
- Tailwind CSS
- Axios
- React Markdown
- KaTeX
- React Syntax Highlighter

### 后端
- Flask
- ModelScope
- Deepseek API
- RAG 检索增强生成

## 🚀 快速开始

1. 克隆项目
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2. 安装依赖
```bash
# 前端依赖
yarn install

# 后端依赖
cd backend
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 前端 (.env)
REACT_APP_API_URL=http://localhost:5000

# 后端 (backend/.env)
DEEPSEEK_API_KEY=your_api_key_here
```

4. 启动服务
```bash
# 启动后端
cd backend
python app.py

# 启动前端（新终端）
cd ..
yarn start
```

## 📖 使用说明

### 通用模式
1. 设置 AI 助手的角色定位
2. 开始自由对话
3. 可以随时调整背景图片

### 法律模式
1. 点击"法律助手专业版"按钮
2. 可选择开启深度思考模式
3. 调整检索设置（法条/问答数量）
4. 提出法律问题，获取专业建议

## 🔧 开发说明

### 项目结构
```
project_root/
├── src/
│   ├── components/
│   │   ├── Chat.js          # 主对话组件
│   │   └── MarkdownRenderer.js  # Markdown渲染
│   └── index.js
├── backend/
│   ├── app.py              # Flask后端
│   └── data_processor.py   # 数据处理
└── public/
```

### 自定义开发
- 修改主题色：编辑 `Chat.js` 中的 `DEFAULT_THEME` 和 `LAW_THEME`
- 添加新功能：扩展 `MarkdownRenderer.js` 的渲染组件
- 调整检索逻辑：修改 `data_processor.py` 中的相关参数

## 📝 注意事项

1. 确保后端服务器正常运行
2. 检查 API 密钥配置
3. 建议使用 Node.js 16+ 和 Python 3.9+
4. 留意浏览器控制台的错误信息

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！在提交代码前，请确保：
1. 代码风格符合项目规范
2. 新功能有完整的测试
3. 文档已经更新

## 📄 许可证

MIT License

## ⚠️ 免责声明

本项目提供的法律建议仅供参考，不构成正式的法律意见。请在实际法律事务中咨询专业律师。
