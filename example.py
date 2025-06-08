"""
LangChain函数调用示例

展示如何使用自定义的LangChain函数调用封装类
"""

import os
from dotenv import load_dotenv
# 修改导入，使用阿里云千问大模型的 LangChain 集成
from langchain_dashscope import ChatDashscope
from langchain_core.messages import HumanMessage, AIMessage

from app.core.langchain_agent import LangChainFunctionAgent
from app.services.worker_service import WorkerService

# 加载环境变量
load_dotenv()

# 创建服务实例
worker_service = WorkerService()

def setup_agent():
    """设置并返回LangChain代理"""
    # 创建语言模型（使用阿里云百炼API的Qwen）
    llm = ChatDashscope(
        model="qwen-plus",  # 使用千问模型
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),  # 从环境变量获取API密钥
        temperature=0,
    )
    
    # 创建LangChain函数调用代理
    agent = LangChainFunctionAgent(
        llm=llm,
        system_message="你是一个建筑工地智能助手，可以回答关于工地情况的问题。"
    )
    
    # 方式一：直接添加函数
    agent.add_function(
        func=worker_service.count_workers,
        name="count_workers",
        description="统计工地上特定状态的工人数量，status参数可选值: 在岗、请假、已离场、全部"
    )
    
    # 方式二：使用装饰器添加函数
    @agent.register(
        name="get_workers_info",
        description="获取工地上特定状态的工人详细信息，status参数可选值: 在岗、请假、已离场、全部"
    )
    def get_workers_info(status: str = "在岗"):
        """获取工地上特定状态的工人详细信息
        
        Args:
            status: 工人状态，可选值：在岗、请假、已离场、全部
            
        Returns:
            工人详细信息的字典
        """
        workers = worker_service.get_workers(status)
        return {
            "count": len(workers),
            "status": status,
            "workers": workers
        }
    
    # 构建代理
    agent.build()
    
    return agent

def demo():
    """运行示例演示"""
    agent = setup_agent()
    
    # 测试查询
    queries = [
        "工地上有多少工人在场?",
        "目前有哪些工人请假了?",
        "统计一下工地上所有的工人情况",
    ]
    
    # 模拟对话历史
    chat_history = []
    
    for query in queries:
        print(f"\n用户: {query}")
        
        # 运行代理
        response = agent.run(query, chat_history)
        
        # 打印结果
        print(f"助手: {response['output']}")
        
        # 更新对话历史
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=response["output"]))

if __name__ == "__main__":
    demo() 