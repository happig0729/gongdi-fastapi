"""
工具函数相关路由
"""
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from app.models.schemas import FunctionCallRequest
from app.core.dashscope_client import DashscopeClient
from app.core.config import TEST_MODE, DEBUG_MODE
from app.core.logging import setup_logging
from app.utils.tools import TOOL_HANDLERS
from app.core.llm_config import DEFAULT_TOOLS
import json

logger = setup_logging()
router = APIRouter()

@router.post("/function_call")
async def function_call(request: FunctionCallRequest):
    """函数调用API"""
    try:
        if DEBUG_MODE:
            logger.debug(f"接收到函数调用请求: {request.dict()}")
        
                # 如果传入的tools为空列表或包含空对象，则使用默认工具
        if not request.tools or (len(request.tools) == 1 and not request.tools[0]):
            tools = DEFAULT_TOOLS
            if DEBUG_MODE:
                logger.debug(f"使用默认工具: {tools}")
        else:
            tools = request.tools
            if DEBUG_MODE:
                logger.debug(f"使用自定义工具: {tools}")
                
        if TEST_MODE:
            # 测试模式
            response = mock_function_call(request.query)
        else:
            # 如果tools为空，则使用默认工具
# 先格式化消息
            messages = DashscopeClient.format_messages(
                prompt=request.query,
                system_message=getattr(request, "system_message", None)
            )
            client = DashscopeClient()
            response = client.function_call(
                messages=messages,
                tools=tools
            )
        
        message = response['choices'][0]['message']
        
        # 如果没有工具调用，直接返回
        if 'tool_calls' not in message:
            return message
        
        # 执行工具调用
        tool_results = []
        executed_results = []
        
        for tool_call in message['tool_calls']:
            if tool_call['type'] == 'function':
                function_name = tool_call['function']['name']
                arguments_str = tool_call['function']['arguments']
                arguments = json.loads(arguments_str) if arguments_str else {}
                
                # 执行工具调用
                if function_name in TOOL_HANDLERS:
                    handler = TOOL_HANDLERS[function_name]
                    try:
                        if DEBUG_MODE:
                            logger.debug(f"执行函数: {function_name}, 参数: {arguments}")
                        
                        if arguments:
                            result_value = handler(**arguments)
                        else:
                            result_value = handler()
                        
                        if DEBUG_MODE:
                            logger.debug(f"函数执行结果: {result_value}")
                        
                        executed_result = {
                            "id": tool_call['id'],
                            "function_name": function_name,
                            "success": True,
                            "result": result_value
                        }
                        
                        # 准备用于返回给模型的格式
                        tool_results.append({
                            "tool_call_id": tool_call['id'],
                            "role": "tool",
                            "content": json.dumps(result_value)
                        })
                    except Exception as e:
                        error_message = f"函数执行错误: {str(e)}"
                        logger.error(error_message)
                        
                        executed_result = {
                            "id": tool_call['id'],
                            "function_name": function_name,
                            "success": False,
                            "error": error_message
                        }
                        
                        tool_results.append({
                            "tool_call_id": tool_call['id'],
                            "role": "tool",
                            "content": json.dumps({"error": error_message})
                        })
                else:
                    error_message = f"未找到处理函数: {function_name}"
                    logger.warning(error_message)
                    
                    executed_result = {
                        "id": tool_call['id'],
                        "function_name": function_name,
                        "success": False,
                        "error": error_message
                    }
                    
                    tool_results.append({
                        "tool_call_id": tool_call['id'],
                        "role": "tool",
                        "content": json.dumps({"error": error_message})
                    })
                
                executed_results.append(executed_result)
        
        # 构建新的消息列表
        new_messages = [
            {"role": "user", "content": request.query},
            message,  # 模型的工具调用消息
        ]
        
        # 添加工具调用结果
        new_messages.extend(tool_results)
        
        if DEBUG_MODE:
            logger.debug(f"发送给模型的完整消息: {json.dumps(new_messages, ensure_ascii=False)}")
        
        # 调用模型处理工具结果
        if TEST_MODE:
            # 测试模式
            final_response = mock_tool_response(new_messages)
        else:
            # 正常调用API
            client = DashscopeClient()
            final_response = client.chat(new_messages)
        
        if DEBUG_MODE:
            logger.debug(f"模型最终响应: {final_response}")
        
        # 返回最终结果
        return {
            "status_code": final_response['status_code'],
            "request_id": final_response['request_id'],
            "answer": final_response['choices'][0]['message']['content'],
            "tool_calls": executed_results
        }
        
    except Exception as e:
        logger.error(f"函数调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"函数调用失败: {str(e)}")

@router.post("/complete_function_call")
async def complete_function_call(request: FunctionCallRequest):
    """完成函数调用API"""
    try:
        if DEBUG_MODE:
            logger.debug(f"接收到完成函数调用请求: {request.dict()}")
        
        if TEST_MODE:
            # 测试模式
            response = mock_tool_response(request.query)
        else:
            # 正常调用API
            client = DashscopeClient()
            response = client.complete_function_call(
                query=request.query,
                tools=request.tools
            )
        
        return jsonable_encoder(response)
    except Exception as e:
        logger.error(f"完成函数调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"完成函数调用失败: {str(e)}") 