# 项目重启指南

本指南将帮助您在新机器上重新启动项目。由于一些大型文件和环境配置没有包含在代码仓库中，您需要手动设置这些内容。

## 1. 环境配置文件

### 前端环境 (.env)
在项目根目录创建 `.env` 文件：
```bash
REACT_APP_API_URL=http://localhost:5000
```

### 后端环境 (backend/.env)
在 `backend/` 目录下创建 `.env` 文件：
```bash
DEEPSEEK_API_KEY=your_api_key_here
```

## 2. 安装依赖

### 前端依赖
```bash
# 使用 yarn 安装依赖
yarn install

# 或者使用 npm
npm install
```

### 后端依赖
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt
```

## 3. 数据文件设置

### 下载必要的数据文件
1. 从以下链接下载数据文件：
   - [law_data_3k.csv](your_data_source_link)
   - [law_QA.csv](your_data_source_link)

2. 将文件放置在 `backend/` 目录下

### 模型文件
1. 下载 modelscope 模型：
```python
from modelscope.hub.snapshot_download import snapshot_download
model_dir = snapshot_download('damo/nlp_corom_sentence-embedding_chinese-base', cache_dir='./models')
```

## 4. 目录结构确认
确保以下目录和文件存在：
```
project_root/
├── backend/
│   ├── law_data_3k.csv
│   ├── law_QA.csv
│   └── .env
├── models/
│   └── damo/
│       └── nlp_corom_sentence-embedding_chinese-base/
├── .env
└── [其他代码文件]
```

## 5. 启动服务

### 启动后端
```bash
# 在 backend/ 目录下
python app.py
```

### 启动前端
```bash
# 在项目根目录下
yarn start
# 或
npm start
```

## 6. 验证

1. 访问 http://localhost:3000 确认前端运行正常
2. 确认 http://localhost:5000 后端服务可访问
3. 尝试发送一条测试消息，确认整个系统工作正常

## 注意事项

1. 确保您有足够的磁盘空间（至少 2GB）用于存储模型和数据文件
2. 如果遇到 CUDA 相关错误，请确保已安装正确版本的 CUDA 工具包
3. 如果在生产环境部署，请相应修改 `.env` 文件中的配置
4. 建议使用 Python 3.9 或更高版本
5. 确保网络连接正常，因为需要下载模型文件

## 常见问题

1. 如果遇到模型下载失败，可以手动下载并放置在对应目录
2. 如果遇到内存不足，可以调整 `backend/app.py` 中的批处理大小
3. 如果前端显示"无法连接到服务器"，请检查后端服务是否正常运行
4. 如果遇到 CORS 错误，请确认 `.env` 中的 API 地址配置是否正确 