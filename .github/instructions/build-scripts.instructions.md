---
applyTo: "scripts/**/*.py"
---

# 构建和加密脚本开发指令

## 加密打包标准

- 使用PyInstaller进行Python代码打包
- 实现多层加密保护：代码混淆 + 文件加密
- 添加反调试和反逆向工程机制
- 支持授权验证和使用期限控制

## 构建脚本规范

```python
import PyInstaller.__main__
import os
import shutil
from cryptography.fernet import Fernet

class ProjectBuilder:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.build_dir = os.path.join(self.project_root, "build")
        self.dist_dir = os.path.join(self.project_root, "dist")
    
    def clean_build(self):
        """清理构建目录"""
        for dir_path in [self.build_dir, self.dist_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
    
    def build_executable(self):
        """构建可执行文件"""
        PyInstaller.__main__.run([
            '--name=flow_farm',
            '--onefile',
            '--windowed',
            '--add-data=config;config',
            '--hidden-import=appium',
            'src/main.py'
        ])
    
    def encrypt_files(self):
        """加密敏感文件"""
        key = Fernet.generate_key()
        fernet = Fernet(key)
        # 实现文件加密逻辑
        pass
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
