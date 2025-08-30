# 项目初始化和环境配置

## 任务描述
为Flow Farm项目配置开发环境，包括三个主要模块的初始化：
1. 服务器后端 (FastAPI)
2. 服务器前端 (Vue.js 3)
3. 员工客户端 (Python GUI)

## 环境要求
- Python 3.8+ （后端和客户端）
- Node.js 18+ （前端）
- Git（版本控制）
- VS Code（推荐IDE）

## 初始化步骤

### 1. 服务器后端初始化
```bash
cd server-backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic python-jose bcrypt
pip freeze > requirements.txt
```

### 2. 服务器前端初始化
```bash
cd server-frontend
npm init vue@latest . -- --typescript --router --pinia
npm install
npm install element-plus axios
```

### 3. 员工客户端初始化
```bash
cd employee-client
python -m venv venv
venv\Scripts\activate
pip install tkinter adb-shell uiautomator2 requests pyinstaller
pip freeze > requirements.txt
```

## 配置文件创建
- 为每个模块创建配置文件
- 设置环境变量
- 配置数据库连接
- 设置日志记录

## 参考文件
- #file:server-backend/app/main.py
- #file:server-frontend/src/main.ts  
- #file:employee-client/src/main.py
- #file:config/app_config.json
