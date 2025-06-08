"""
调试相关路由
"""
import logging
from fastapi import APIRouter
from app.core.config import DEBUG_MODE, TEST_MODE
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()

@router.get("/debug")
async def debug_status():
    """获取调试状态"""
    return {
        "debug_mode": DEBUG_MODE,
        "test_mode": TEST_MODE,
        "log_level": logging.getLevelName(logger.level),
        "api_status": "running"
    }

@router.post("/debug")
async def set_debug(
    debug_mode: bool = None, 
    test_mode: bool = None,
    log_level: str = None
):
    """设置调试状态"""
    global DEBUG_MODE, TEST_MODE
    
    result = {"updated": False, "settings": {}}
    
    if debug_mode is not None:
        DEBUG_MODE = debug_mode
        result["updated"] = True
        result["settings"]["debug_mode"] = DEBUG_MODE
    
    if test_mode is not None:
        TEST_MODE = test_mode
        result["updated"] = True
        result["settings"]["test_mode"] = TEST_MODE
    
    if log_level is not None:
        try:
            level = getattr(logging, log_level.upper())
            logger.setLevel(level)
            result["updated"] = True
            result["settings"]["log_level"] = log_level.upper()
        except AttributeError:
            result["error"] = f"无效的日志级别: {log_level}"
    
    if not result["updated"]:
        result["message"] = "没有提供任何需要更新的设置"
    
    return result

@router.get("/logs")
async def get_logs(lines: int = 100):
    """获取最近的日志"""
    try:
        with open(logger.handlers[1].baseFilename, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()
            return {"logs": log_lines[-lines:]}
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return {"error": f"获取日志失败: {str(e)}"} 