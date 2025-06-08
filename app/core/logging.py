"""
日志配置模块
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from .config import LOG_DIR, LOG_FILE, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT

def setup_logging():
    """配置日志系统"""
    # 创建日志目录
    os.makedirs(LOG_DIR, exist_ok=True)

    # 配置根日志器
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),  # 控制台输出
            RotatingFileHandler(  # 文件输出
                filename=LOG_FILE,
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
        ]
    )

    # 创建应用日志器
    logger = logging.getLogger("gongdi-api")
    logger.info(f"日志文件路径: {LOG_FILE}")
    
    return logger 