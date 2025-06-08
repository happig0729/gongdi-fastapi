"""
阿里云千问API使用示例

展示如何直接使用阿里云千问API客户端
"""

import os
import sys
from dotenv import load_dotenv
import json

# 确保可以导入应用模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

from app.core.dashscope_client import DashscopeClient
from app.core.llm_config import DEFAULT_TOOLS

def chat_demo():
    """普通聊天演示"""
    print("\n--- 普通聊天示例 ---")
    client = DashscopeClient()
    
    # 创建消息
    messages = client.format_messages(
        prompt="今天杭州天气怎么样？",
        system_message="你是一个建筑工地智能助手，会简洁明了地回答问题。"
    )
    
    # 发送聊天请求
    print("发送请求...")
    response = client.chat(messages)
    
    # 打印结果
    print(f"状态码: {response['status_code']}")
    print(f"请求ID: {response['request_id']}")
    print(f"问题: 今天杭州天气怎么样？")
    print(f"回答: {response['choices'][0]['message']['content']}")

def function_call_demo():
    """函数调用演示"""
    print("\n--- 函数调用示例 ---")
    client = DashscopeClient()
    
    # 使用默认工具配置
    tools = DEFAULT_TOOLS
    
    # 创建消息
    messages = [{"role": "user", "content": "杭州天气怎么样"}]
    
    # 发送函数调用请求
    print("发送请求...")
    response = client.function_call(messages, tools)
    
    # 打印结果
    print(f"状态码: {response['status_code']}")
    print(f"请求ID: {response['request_id']}")
    print(f"问题: 杭州天气怎么样")
    print("工具调用结果:")
    print(json.dumps(response['choices'][0]['message'], ensure_ascii=False, indent=2))

def multi_turn_demo():
    """多轮对话演示"""
    print("\n--- 多轮对话示例 ---")
    client = DashscopeClient()
    
    # 初始化对话
    history = []
    system_message = "你是一个建筑工地智能助手，会简洁明了地回答问题。"
    
    # 第一轮对话
    messages = client.format_messages(
        prompt="我们工地上有多少工人？",
        system_message=system_message,
        history=history
    )
    
    print("发送第一轮问题...")
    response = client.chat(messages)
    assistant_message = response['choices'][0]['message']['content']
    
    print(f"问题 1: 我们工地上有多少工人？")
    print(f"回答 1: {assistant_message}")
    
    # 更新历史
    history.append({"role": "user", "content": "我们工地上有多少工人？"})
    history.append({"role": "assistant", "content": assistant_message})
    
    # 第二轮对话
    messages = client.format_messages(
        prompt="这些工人都在干什么工作？",
        history=history  # 不需要重复系统消息
    )
    
    print("\n发送第二轮问题...")
    response = client.chat(messages)
    assistant_message = response['choices'][0]['message']['content']
    
    print(f"问题 2: 这些工人都在干什么工作？")
    print(f"回答 2: {assistant_message}")

if __name__ == "__main__":
    # 运行示例
    try:
        chat_demo()
        function_call_demo()
        multi_turn_demo()
    except Exception as e:
        print(f"示例运行失败: {str(e)}")
        import traceback
        traceback.print_exc() 