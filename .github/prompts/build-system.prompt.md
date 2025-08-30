# 全项目构建脚本

为Flow Farm项目创建一个完整的构建系统，支持三个模块的独立和联合构建。

## 构建脚本功能

### 主构建脚本 (scripts/build_all.py)
- 检查所有环境依赖
- 按顺序构建三个模块
- 生成统一的发布包
- 验证构建完整性

### 模块化构建
1. **服务器后端**: Docker镜像 + API文档
2. **服务器前端**: 静态文件 + 资源优化
3. **员工客户端**: 加密可执行文件 + 安装包

## 使用方法

```bash
# 构建所有模块 (开发版本)
python scripts/build_all.py --mode development

# 构建所有模块 (生产版本)
python scripts/build_all.py --mode production --encrypt

# 构建特定模块
python scripts/build_all.py --modules backend,frontend --mode production

# 仅验证环境
python scripts/build_all.py --check-only
```

## 参考文件
- #file:scripts/build.py
- #file:scripts/validate_build.py  
- #file:server-backend/Dockerfile
- #file:server-frontend/vite.config.ts
- #file:employee-client/pyinstaller.spec
