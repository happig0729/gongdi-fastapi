"""
数据模型定义
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MessageItem(BaseModel):
    """消息项模型"""
    role: str
    content: str

class ChatRequest(BaseModel):
    """聊天请求模型"""
    prompt: str
    system_message: Optional[str] = "你是一个建筑工地智能助手，会简洁明了地回答问题。"

class FunctionCallRequest(BaseModel):
    """函数调用请求模型"""
    query: str
    tools: Optional[List[Dict[str, Any]]] = None

class ChatHistoryRequest(BaseModel):
    """带历史记录的聊天请求模型"""
    prompt: str
    system_message: Optional[str] = "你是一个建筑工地智能助手，会简洁明了地回答问题。"
    history: List[MessageItem] = [] 