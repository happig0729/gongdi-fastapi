"""
阿里云千问API FastAPI服务

将dashscope_demo封装为RESTful API服务
"""

import os
import sys
import json
import datetime
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

# 设置日志配置
log_file = os.path.join(log_dir, "gongdi_api.log")

# 配置根日志器
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        RotatingFileHandler(  # 文件输出
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,  # 保留5个备份
            encoding='utf-8'
        )
    ]
)
logger = logging.getLogger("gongdi-api")
logger.info(f"日志文件路径: {log_file}")

# 确保可以导入应用模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 手动设置环境变量
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY", "sk-baf39aa1386f4a4395cc5642defebc0f")

# 调试模式设置
DEBUG_MODE = True  # 设置为True启用调试模式
TEST_MODE = False  # 强制使用测试模式进行演示

try:
    from app.core.dashscope_client import DashscopeClient
    from app.core.llm_config import DEFAULT_TOOLS
except ImportError:
    from dashscope_demo import DashscopeClient, DEFAULT_TOOLS, mock_response, mock_function_call, mock_tool_response

# 创建FastAPI应用
app = FastAPI(
    title="千问API服务",
    description="阿里云千问大模型API封装服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 工具函数处理器
def get_current_time():
    """获取当前时间"""
    current_time = datetime.datetime.now()
    return {
        "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "date": current_time.strftime("%Y-%m-%d"),
        "time": current_time.strftime("%H:%M:%S"),
        "weekday": current_time.strftime("%A")
    }

def get_current_weather(location):
    """获取指定位置的天气
    
    这里使用的是模拟数据，真实场景应该调用天气API
    """
    # 在实际应用中，这里应该调用天气API获取实时数据
    weather_data = {
        "北京": {"temp": "22°C", "condition": "晴", "humidity": "40%", "wind": "东北风 3级"},
        "上海": {"temp": "25°C", "condition": "多云", "humidity": "65%", "wind": "东风 2级"},
        "广州": {"temp": "28°C", "condition": "小雨", "humidity": "80%", "wind": "南风 2级"},
        "深圳": {"temp": "27°C", "condition": "阴", "humidity": "75%", "wind": "东南风 3级"},
        "杭州": {"temp": "24°C", "condition": "晴", "humidity": "50%", "wind": "西北风 1级"},
    }
    
    # 默认返回数据
    default_weather = {"temp": "20°C", "condition": "晴", "humidity": "60%", "wind": "微风"}
    
    return weather_data.get(location, default_weather)

# 工具函数映射表
TOOL_HANDLERS = {
    "get_current_time": get_current_time,
    "get_current_weather": get_current_weather
}

# 数据模型
class ChatRequest(BaseModel):
    prompt: str
    system_message: Optional[str] = "你是一个建筑工地智能助手，会简洁明了地回答问题。"

class FunctionCallRequest(BaseModel):
    query: str
    tools: Optional[List[Dict[str, Any]]] = None

class MessageItem(BaseModel):
    role: str
    content: str

class ChatHistoryRequest(BaseModel):
    prompt: str
    system_message: Optional[str] = "你是一个建筑工地智能助手，会简洁明了地回答问题。"
    history: List[MessageItem] = []

# API端点
@app.get("/")
async def read_root():
    return {"message": "千问API服务已启动", "status": "running"}

@app.get("/api/debug")
async def debug_status():
    """获取或设置调试状态"""
    return {
        "debug_mode": DEBUG_MODE,
        "test_mode": TEST_MODE,
        "log_level": logging.getLevelName(logger.level),
        "api_status": "running"
    }

@app.post("/api/debug")
async def set_debug(
    debug_mode: Optional[bool] = None, 
    test_mode: Optional[bool] = None,
    log_level: Optional[str] = None
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

@app.post("/api/chat")
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
        raise HTTPException(status_code=500, detail=f"聊天请求失败: {str(e)}")

@app.post("/api/function_call")
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
        
        # 验证每个工具都有必要的字段
        for i, tool in enumerate(tools):
            # 跳过空对象
            if not tool:
                tools[i] = {
                    'type': 'function',
                    'function': {
                        'name': f'default_tool_{i}',
                        'description': '默认工具'
                    }
                }
                if DEBUG_MODE:
                    logger.debug(f"替换空工具为默认工具: {tools[i]}")
                continue
                
            if 'type' not in tool:
                tool['type'] = 'function'  # 添加默认type字段
                if DEBUG_MODE:
                    logger.debug(f"为工具添加默认type字段: {tool}")
            
            if 'function' not in tool and isinstance(tool, dict):
                # 如果工具是没有function字段的字典，假设整个工具就是function定义
                function_def = {k: v for k, v in tool.items() if k != 'type'}
                if 'name' not in function_def:
                    function_def['name'] = f"tool_{i}"  # 添加默认name
                    if DEBUG_MODE:
                        logger.debug(f"为工具添加默认name字段: {function_def}")
                
                tools[i] = {
                    'type': 'function',
                    'function': function_def
                }
                if DEBUG_MODE:
                    logger.debug(f"重构工具格式: {tools[i]}")
            elif 'function' in tool and isinstance(tool['function'], dict):
                # 确保function对象有name属性
                if 'name' not in tool['function']:
                    tool['function']['name'] = f"tool_{i}"  # 添加默认name
                    if DEBUG_MODE:
                        logger.debug(f"为function对象添加默认name: {tool}")
        
        if TEST_MODE:
            # 测试模式
            if DEBUG_MODE:
                logger.debug("使用测试模式处理请求")
            response = mock_function_call(request.query, tools)
        else:
            # 正常调用API
            if DEBUG_MODE:
                logger.debug(f"调用DashscopeClient处理请求，query: {request.query}")
            client = DashscopeClient()
            messages = [{"role": "user", "content": request.query}]
            response = client.function_call(messages, tools)
        
        if DEBUG_MODE:
            logger.debug(f"API响应: {response}")
            
        message = response['choices'][0]['message']
        result = {
            "status_code": response['status_code'],
            "request_id": response['request_id'],
            "message": message
        }
        
        # 如果没有工具调用，直接返回
        if 'tool_calls' not in message:
            if DEBUG_MODE:
                logger.debug("响应中没有工具调用")
            return message
        
        # 添加工具调用信息和执行结果
        tool_calls_info = []
        executed_results = []
        tool_results = []  # 用于将结果返回给模型的格式
        
        for tool_call in message['tool_calls']:
            if tool_call['type'] == 'function':
                function_name = tool_call['function']['name']
                arguments_str = tool_call['function']['arguments']
                arguments = json.loads(arguments_str) if arguments_str else {}
                
                tool_call_info = {
                    "id": tool_call['id'],
                    "function_name": function_name,
                    "arguments": arguments
                }
                tool_calls_info.append(tool_call_info)
                
                if DEBUG_MODE:
                    logger.debug(f"工具调用信息: {tool_call_info}")
                
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
                        
                        # 准备用于返回给模型的格式（包含错误信息）
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
                    
                    # 准备用于返回给模型的格式（包含错误信息）
                    tool_results.append({
                        "tool_call_id": tool_call['id'],
                        "role": "tool",
                        "content": json.dumps({"error": error_message})
                    })
                
                executed_results.append(executed_result)
        
        result["tool_calls"] = tool_calls_info
        result["executed_results"] = executed_results
        
        # 将函数调用结果返回给模型处理
        if DEBUG_MODE:
            logger.debug("将函数调用结果返回给模型处理")
            
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
        
        # 添加模型最终回答到结果中
        final_content = final_response['choices'][0]['message']['content']
        result["final_answer"] = final_content
        
        if DEBUG_MODE:
            logger.debug(f"最终返回结果: {result}")
            
        return final_content
    except Exception as e:
        # 记录详细错误信息
        error_detail = f"函数调用请求失败: {str(e)}"
        logger.error(error_detail)
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/complete_function_call")
async def complete_function_call(request: FunctionCallRequest):
    """完整的函数调用流程API"""
    try:
        # 如果传入的tools为空列表或包含空对象，则使用默认工具
        if not request.tools or (len(request.tools) == 1 and not request.tools[0]):
            tools = DEFAULT_TOOLS
        else:
            tools = request.tools
        
        # 验证每个工具都有必要的字段
        for i, tool in enumerate(tools):
            # 跳过空对象
            if not tool:
                tools[i] = {
                    'type': 'function',
                    'function': {
                        'name': f'default_tool_{i}',
                        'description': '默认工具'
                    }
                }
                continue
                
            if 'type' not in tool:
                tool['type'] = 'function'  # 添加默认type字段
            
            if 'function' not in tool and isinstance(tool, dict):
                # 如果工具是没有function字段的字典，假设整个工具就是function定义
                function_def = {k: v for k, v in tool.items() if k != 'type'}
                if 'name' not in function_def:
                    function_def['name'] = f"tool_{i}"  # 添加默认name
                
                tools[i] = {
                    'type': 'function',
                    'function': function_def
                }
            elif 'function' in tool and isinstance(tool['function'], dict):
                # 确保function对象有name属性
                if 'name' not in tool['function']:
                    tool['function']['name'] = f"tool_{i}"  # 添加默认name
        
        # 步骤1：发送用户问题，模型决定调用工具
        if TEST_MODE:
            # 测试模式
            response = mock_function_call(request.query, tools)
        else:
            # 正常调用API
            client = DashscopeClient()
            messages = [{"role": "user", "content": request.query}]
            response = client.function_call(messages, tools)
        
        message = response['choices'][0]['message']
        
        # 没有工具调用，直接返回
        if 'tool_calls' not in message:
            return {
                "status": "completed",
                "answer": message.get('content', '无内容'),
                "used_tools": False
            }
        
        # 步骤2：执行工具调用
        tool_results = []
        executed_tools = []
        
        for tool_call in message['tool_calls']:
            if tool_call['type'] == 'function':
                function_name = tool_call['function']['name']
                arguments_str = tool_call['function']['arguments']
                arguments = json.loads(arguments_str) if arguments_str else {}
                
                executed_tool = {
                    "function_name": function_name,
                    "arguments": arguments
                }
                
                # 执行函数
                if function_name in TOOL_HANDLERS:
                    handler = TOOL_HANDLERS[function_name]
                    try:
                        if arguments:
                            result = handler(**arguments)
                        else:
                            result = handler()
                        
                        executed_tool["result"] = result
                        executed_tool["success"] = True
                        
                        # 记录工具调用结果
                        tool_results.append({
                            "tool_call_id": tool_call['id'],
                            "role": "tool",
                            "content": json.dumps(result)
                        })
                    except Exception as e:
                        error_message = f"函数执行错误: {str(e)}"
                        executed_tool["error"] = error_message
                        executed_tool["success"] = False
                        
                        tool_results.append({
                            "tool_call_id": tool_call['id'],
                            "role": "tool",
                            "content": json.dumps({"error": error_message})
                        })
                else:
                    error_message = f"未找到处理函数 '{function_name}'"
                    executed_tool["error"] = error_message
                    executed_tool["success"] = False
                    
                    tool_results.append({
                        "tool_call_id": tool_call['id'],
                        "role": "tool",
                        "content": json.dumps({"error": error_message})
                    })
                
                executed_tools.append(executed_tool)
        
        # 步骤3：将工具调用结果返回给模型
        # 构建新的消息列表，包含原始问题、模型的工具调用和工具结果
        new_messages = [
            {"role": "user", "content": request.query},
            message,  # 模型的工具调用消息
        ]
        
        # 添加工具调用结果
        new_messages.extend(tool_results)
        
        # 调用模型处理工具结果
        if TEST_MODE:
            # 测试模式
            final_response = mock_tool_response(new_messages)
        else:
            # 正常调用API
            client = DashscopeClient()
            final_response = client.chat(new_messages)
        
        # 步骤4：输出最终结果
        final_content = final_response['choices'][0]['message']['content']
        
        return {
            "status": "completed",
            "answer": final_content,
            "used_tools": True,
            "executed_tools": executed_tools
        }
    except Exception as e:
        # 记录详细错误信息
        error_detail = f"完整函数调用请求失败: {str(e)}"
        print(f"ERROR: {error_detail}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/multi_turn_chat")
async def multi_turn_chat(request: ChatHistoryRequest):
    """多轮对话API"""
    try:
        if TEST_MODE:
            # 测试模式 - 简化处理
            response = mock_response(request.prompt)
            assistant_message = response['choices'][0]['message']['content']
        else:
            # 正常调用API
            client = DashscopeClient()
            
            # 转换历史记录格式
            history = []
            for item in request.history:
                history.append({"role": item.role, "content": item.content})
            
            messages = client.format_messages(
                prompt=request.prompt,
                system_message=request.system_message,
                history=history
            )
            
            response = client.chat(messages)
            assistant_message = response['choices'][0]['message']['content']
        
        return {
            "status_code": response['status_code'],
            "request_id": response['request_id'],
            "answer": assistant_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多轮对话请求失败: {str(e)}")

@app.get("/api/logs")
async def get_logs(lines: int = 100):
    """获取最近的日志内容
    
    Args:
        lines: 要获取的最新日志行数，默认100行
    """
    try:
        if not os.path.exists(log_file):
            return {"error": "日志文件不存在", "file": log_file}
        
        # 读取日志文件的最后N行
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.readlines()
            total_lines = len(log_content)
            start_line = max(0, total_lines - lines)
            recent_logs = log_content[start_line:]
        
        return {
            "log_file": log_file,
            "total_lines": total_lines,
            "showing_lines": len(recent_logs),
            "content": recent_logs
        }
    except Exception as e:
        logger.error(f"获取日志出错: {str(e)}")
        return {"error": f"获取日志失败: {str(e)}", "file": log_file}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 