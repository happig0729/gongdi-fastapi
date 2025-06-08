"""
配置管理模块
"""
import os
from typing import Optional

# 环境变量配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-baf39aa1386f4a4395cc5642defebc0f")

# 调试模式配置
DEBUG_MODE = True
TEST_MODE = False

# 日志配置
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "gongdi_api.log")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# API配置
API_TITLE = "千问API服务"
API_DESCRIPTION = "阿里云千问大模型API封装服务"
API_VERSION = "1.0.0"

# CORS配置
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"] 