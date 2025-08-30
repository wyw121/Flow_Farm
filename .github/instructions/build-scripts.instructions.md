---
applyTo: "scripts/**/*.py"
---

# 构建和部署脚本开发指令

## 适用范围
本指令适用于 `scripts/` 目录下的所有构建、部署和工具脚本，包括多模块项目的构建流程。

## 三模块构建策略

### 1. 服务器后端构建
- FastAPI应用打包
- 数据库迁移脚本
- Docker容器化构建
- 生产环境配置

### 2. 服务器前端构建
- Vue.js应用构建优化
- 静态资源压缩
- CDN部署准备
- 多环境配置管理

### 3. 员工客户端构建
- PyInstaller打包配置
- 代码加密和混淆
- 依赖库打包
- 安装包生成

## 构建脚本规范

### 环境检查脚本
```python
import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        raise Exception(f"需要Python 3.8+，当前版本: {version.major}.{version.minor}")

def check_node_version():
    """检查Node.js版本"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        version = result.stdout.strip()
        if not version.startswith('v18') and not version.startswith('v19'):
            print(f"警告: 推荐使用Node.js 18+，当前版本: {version}")
    except FileNotFoundError:
        raise Exception("未找到Node.js，请先安装")
```

### 多模块构建脚本
```python
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class ProjectBuilder:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.build_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def build_backend(self, mode: str = "development"):
        """构建服务器后端"""
        backend_path = self.root_path / "server-backend"
        
        # 激活虚拟环境
        venv_python = backend_path / "venv" / "Scripts" / "python.exe"
        
        # 安装依赖
        subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"],
                      cwd=backend_path, check=True)
        
        # 运行测试
        subprocess.run([str(venv_python), "-m", "pytest", "tests/"],
                      cwd=backend_path, check=True)
        
        # 构建Docker镜像（生产模式）
        if mode == "production":
            subprocess.run(["docker", "build", "-t", f"flow-farm-backend:{self.build_time}", "."],
                          cwd=backend_path, check=True)
    
    def build_client(self, mode: str = "development", encrypt: bool = False):
        """构建员工客户端"""
        client_path = self.root_path / "employee-client"
        
        # PyInstaller配置
        pyinstaller_args = [
            "python", "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            f"--name=FlowFarm_Employee_{self.build_time}",
            "src/main.py"
        ]
        
        if encrypt:
            pyinstaller_args.extend(["--key", self._generate_encryption_key()])
        
        subprocess.run(pyinstaller_args, cwd=client_path, check=True)
```

## 加密和安全
- 使用PyInstaller进行Python代码打包
- 实现多层加密保护：代码混淆 + 文件加密
- 添加反调试和反逆向工程机制
- 支持授权验证和使用期限控制

## 重要提醒
- 构建前必须运行所有测试
- 生产构建必须进行安全检查
- 记录详细的构建日志
- 实现构建失败回滚机制
- 验证所有环境变量配置
- 确保构建过程可重复执行
```

## 版本管理

- 自动生成版本号
- 记录构建时间和环境信息
- 支持增量更新机制
- 维护版本变更日志

## 分发包结构

```
Flow_Farm_Release/
├── flow_farm.exe          # 主程序
├── config/                # 配置文件目录
├── drivers/               # 设备驱动
├── docs/                  # 用户文档
├── install.bat           # 安装脚本
├── uninstall.bat         # 卸载脚本
└── README.txt            # 使用说明
```

## 授权验证机制

- 硬件指纹绑定
- 在线授权验证
- 使用期限控制
- 功能模块授权
