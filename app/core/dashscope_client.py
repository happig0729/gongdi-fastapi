"""
阿里云千问API直接调用客户端

提供直接调用阿里云千问API的功能
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
import json

from dashscope import Generation

from app.core.llm_config import (
    DASHSCOPE_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOOLS
)

# 获取logger
logger = logging.getLogger("gongdi-api.dashscope")

class DashscopeClient:
    """阿里云千问API客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """初始化阿里云千问API客户端

        Args:
            api_key: API密钥，默认从环境变量获取
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数量
        """
        self.api_key = api_key or DASHSCOPE_API_KEY
        self.model = model or DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens or DEFAULT_MAX_TOKENS
        
        # 记录初始化信息
        logger.debug(f"DashscopeClient初始化: model={self.model}, temperature={self.temperature}, max_tokens={self.max_tokens}")
        
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict:
        """发送聊天请求

        Args:
            messages: 聊天消息列表
            tools: 工具列表
            temperature: 温度参数
            max_tokens: 最大生成token数量

        Returns:
            API响应结果
        """
        params = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature if temperature is not None else self.temperature,
            'max_tokens': max_tokens or self.max_tokens,
            'result_format': 'message',
            'api_key': self.api_key
        }
        
        # 如果有工具，添加到参数中
        if tools:
            params['tools'] = tools
        
        # 调用千问API
        response = Generation.call(**params)
        
        # 处理响应
        if response.status_code == 200:
            # 检查是否有tool_calls
            if ('choices' in response.output and 
                'message' in response.output['choices'][0] and 
                'tool_calls' in response.output['choices'][0]['message']):
                # 返回包含工具调用的完整响应
                return {
                    'status_code': response.status_code,
                    'request_id': response.request_id,
                    'choices': [{
                        'message': response.output['choices'][0]['message']
                    }],
                    'usage': response.output.get('usage', {})
                }
            else:
                # 返回普通响应
                return {
                    'status_code': response.status_code,
                    'request_id': response.request_id,
                    'choices': [{
                        'message': {
                            'content': response.output['choices'][0]['message'].get('content', ''),
                            'role': response.output['choices'][0]['message'].get('role', 'assistant')
                        }
                    }],
                    'usage': response.output.get('usage', {})
                }
        else:
            raise Exception(f"API调用失败: {response.code} - {response.message}")
    
    def function_call(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict:
        """发送工具调用请求

        Args:
            messages: 聊天消息列表
            tools: 工具列表，如果为None则使用默认工具
            temperature: 温度参数
            max_tokens: 最大生成token数量

        Returns:
            工具调用结果
        """
        logger.debug(f"接收function_call请求: messages={messages}")
        
        # 确保工具格式正确
        tools_to_use = tools or DEFAULT_TOOLS
        logger.debug(f"原始工具列表: {tools_to_use}")
        
        formatted_tools = []
        
        for i, tool in enumerate(tools_to_use):
            # 处理空对象或None
            if not tool:
                formatted_tool = {
                    'type': 'function',
                    'function': {
                        'name': f'default_tool_{i}',
                        'description': '默认工具'
                    }
                }
                logger.debug(f"替换空工具为默认工具: {formatted_tool}")
                formatted_tools.append(formatted_tool)
                continue
                
            if isinstance(tool, dict):
                if 'type' not in tool:
                    formatted_tool = {'type': 'function'}
                    logger.debug(f"添加默认type字段: function")
                else:
                    formatted_tool = {'type': tool['type']}
                
                if 'function' in tool:
                    formatted_tool['function'] = tool['function']
                    # 确保function对象有name属性
                    if 'name' not in formatted_tool['function']:
                        # 如果没有name，尝试找到一个可能的name
                        if isinstance(formatted_tool['function'], dict) and formatted_tool['function'].get('description'):
                            # 从描述中提取一个简短的名称
                            desc = formatted_tool['function']['description']
                            suggested_name = desc.split()[0].lower() if desc else "unknown_tool"
                            formatted_tool['function']['name'] = suggested_name
                            logger.debug(f"从描述中提取工具名称: {suggested_name}")
                        else:
                            # 使用默认名称
                            formatted_tool['function']['name'] = f"tool_{i}"
                            logger.debug(f"使用默认工具名称: tool_{i}")
                elif not any(k == 'function' for k in tool.keys()):
                    # 假设整个工具是function定义
                    func_def = {k: v for k, v in tool.items() if k != 'type'}
                    # 确保function对象有name属性
                    if 'name' not in func_def:
                        if 'description' in func_def:
                            # 从描述中提取一个简短的名称
                            desc = func_def['description']
                            suggested_name = desc.split()[0].lower() if desc else "unknown_tool"
                            func_def['name'] = suggested_name
                            logger.debug(f"从描述中提取工具名称: {suggested_name}")
                        else:
                            # 使用默认名称
                            func_def['name'] = f"tool_{i}"
                            logger.debug(f"使用默认工具名称: tool_{i}")
                    formatted_tool['function'] = func_def
                
                formatted_tools.append(formatted_tool)
        
        logger.debug(f"格式化后的工具列表: {formatted_tools}")
        
        try:
            params = {
                'model': self.model,
                'messages': messages,
                'tools': formatted_tools,
                'temperature': temperature if temperature is not None else self.temperature,
                'max_tokens': max_tokens or self.max_tokens,
                'result_format': 'message',
                'api_key': self.api_key
            }
            
            logger.debug(f"调用DashScope API参数: model={params['model']}, temperature={params['temperature']}, max_tokens={params['max_tokens']}")
            
            # 调用千问API
            logger.debug("开始调用DashScope API...")
            response = Generation.call(**params)
            logger.debug(f"DashScope API响应状态码: {response.status_code}")
            
            # 处理响应
            if response.status_code == 200:
                result = {
                    'status_code': response.status_code,
                    'request_id': response.request_id,
                    'choices': [{
                        'message': response.output['choices'][0]['message']
                    }],
                    'usage': response.output.get('usage', {})
                }
                logger.debug(f"成功处理响应: request_id={result['request_id']}")
                return result
            else:
                error_msg = f"API调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            # 记录详细错误信息
            logger.error(f"DashscopeClient.function_call错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # 继续抛出异常
            raise
    
    def process_tool_results(
        self, 
        messages: List[Dict[str, Any]], 
        tool_results: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict:
        """处理工具调用结果，并发送给模型处理
        
        Args:
            messages: 聊天历史消息
            tool_results: 工具调用结果
            temperature: 温度参数
            max_tokens: 最大生成token数量
            
        Returns:
            模型处理结果
        """
        # 构建完整的消息列表
        full_messages = list(messages)  # 复制原始消息
        
        # 添加工具调用结果
        full_messages.extend(tool_results)
        
        # 调用模型处理
        return self.chat(
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
    @staticmethod
    def format_messages(
        prompt: str, 
        system_message: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """格式化消息

        Args:
            prompt: 用户输入的提示
            system_message: 系统消息
            history: 历史消息

        Returns:
            格式化后的消息列表
        """
        messages = []
        
        # 添加系统消息
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        # 添加历史消息
        if history:
            messages.extend(history)
            
        # 添加用户消息
        messages.append({"role": "user", "content": prompt})
        
        return messages 