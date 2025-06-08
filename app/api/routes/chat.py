"""
聊天相关路由
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatHistoryRequest
from app.core.dashscope_client import DashscopeClient
from app.core.config import TEST_MODE
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    """简单聊天API"""
    try:
        if TEST_MODE:
            # 测试模式
            response = mock_response(request.prompt)
        else:
            # 正常调用API
            client = DashscopeClient()
            messages = client.format_messages(
                prompt=request.prompt,
                system_message=request.system_message
            )
            response = client.chat(messages)
        
        return {
            "status_code": response['status_code'],
            "request_id": response['request_id'],
            "answer": response['choices'][0]['message']['content']
        }
    except Exception as e:
        logger.error(f"聊天请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"聊天请求失败: {str(e)}")

@router.post("/multi_turn_chat")
async def multi_turn_chat(request: ChatHistoryRequest):
    """多轮对话API"""
    try:
        if TEST_MODE:
            # 测试模式
            response = mock_response(request.prompt)
        else:
            # 正常调用API
            client = DashscopeClient()
            messages = client.format_messages(
                prompt=request.prompt,
                system_message=request.system_message,
                history=request.history
            )
            response = client.chat(messages)
        
        return {
            "status_code": response['status_code'],
            "request_id": response['request_id'],
            "answer": response['choices'][0]['message']['content']
        }
    except Exception as e:
        logger.error(f"多轮对话请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"多轮对话请求失败: {str(e)}") 