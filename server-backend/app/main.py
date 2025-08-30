"""
Flow Farm 服务器后端 - FastAPI应用程序
管理员用于记录和管理员工工作信息的后端服务
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, billing, devices, kpi, reports, users
from .config import settings
from .database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表已创建")

    yield

    # 关闭时清理资源
    print("🔄 应用程序正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title="Flow Farm 服务器后端",
    description="员工工作量管理和KPI统计系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(kpi.router, prefix="/api/v1/kpi", tags=["KPI统计"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["计费管理"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["设备管理"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["数据报表"])


@app.get("/")
async def root():
    """根路径 - 健康检查"""
    return {
        "message": "Flow Farm 服务器后端正在运行",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
