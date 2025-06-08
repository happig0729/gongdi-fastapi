"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    CORS_ORIGINS,
    CORS_CREDENTIALS,
    CORS_METHODS,
    CORS_HEADERS
)
from app.core.logging import setup_logging
from app.api.routes import chat, debug, tools

# 设置日志
logger = setup_logging()

# 创建FastAPI应用
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# 注册路由
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(debug.router, prefix="/api", tags=["debug"])
app.include_router(tools.router, prefix="/api", tags=["tools"])

@app.get("/")
async def read_root():
    """根路由"""
    return {"message": "千问API服务已启动", "status": "running"} 