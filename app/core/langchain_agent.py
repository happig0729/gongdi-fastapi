"""
LangChain函数调用封装类

用于处理函数调用的LangChain代理封装
"""

from typing import Dict, List, Any, Callable, Optional, Type, Union
import inspect
from functools import wraps

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import FunctionMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool


class LangChainFunctionAgent:
    """LangChain函数调用封装类
    
    封装LangChain的函数调用逻辑，使其更易于使用
    """
    
    def __init__(self, llm: Any, system_message: str = "你是一个建筑工地智能助手"):
        """初始化LangChain函数调用代理

        Args:
            llm: 语言模型实例（需要支持OpenAI函数调用格式的模型，如Qwen3）
            system_message: 系统消息
        """
        self.llm = llm
        self.system_message = system_message
        self.tools: List[BaseTool] = []
        self.prompt = None
        self.agent = None
        self.agent_executor = None
        
    def add_tool(self, tool: BaseTool) -> None:
        """添加工具

        Args:
            tool: LangChain工具实例
        """
        self.tools.append(tool)
        
    def add_function(self, 
                    func: Callable, 
                    name: Optional[str] = None, 
                    description: Optional[str] = None) -> None:
        """将Python函数添加为工具

        Args:
            func: Python函数
            name: 函数名称（如果为None则使用函数本身的名称）
            description: 函数描述（如果为None则使用函数的文档字符串）
        """
        from langchain.tools import StructuredTool
        
        func_name = name or func.__name__
        func_description = description or func.__doc__ or f"{func_name}函数"
        
        tool = StructuredTool.from_function(
            func=func,
            name=func_name,
            description=func_description
        )
        
        self.add_tool(tool)
    
    def register(self, name: Optional[str] = None, description: Optional[str] = None):
        """装饰器：注册函数作为工具

        Args:
            name: 函数名称（如果为None则使用函数本身的名称）
            description: 函数描述（如果为None则使用函数的文档字符串）
        
        Returns:
            装饰器函数
        """
        def decorator(func):
            self.add_function(func, name, description)
            return func
        return decorator
    
    def build(self) -> None:
        """构建代理"""
        # 确保已经添加了工具
        if not self.tools:
            raise ValueError("至少需要添加一个工具才能构建代理")
        
        # 构建提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建LangChain代理
        llm_with_tools = self.llm.bind_functions(self.tools)
        
        # 构建代理执行链
        self.agent = (
            {
                "input": lambda x: x["input"] if isinstance(x, dict) else x,
                "chat_history": lambda x: x.get("chat_history", []) if isinstance(x, dict) else [],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"])
            }
            | self.prompt
            | llm_with_tools
            | OpenAIFunctionsAgentOutputParser()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            return_intermediate_steps=True,
        )
    
    def run(self, query: str, chat_history: Optional[List] = None) -> Dict[str, Any]:
        """运行代理处理查询

        Args:
            query: 用户查询
            chat_history: 聊天历史记录

        Returns:
            Dict[str, Any]: 包含输出和中间步骤的结果字典
        """
        if not self.agent_executor:
            self.build()
            
        history = chat_history or []
        
        return self.agent_executor.invoke({
            "input": query,
            "chat_history": history
        })
    
    def stream(self, query: str, chat_history: Optional[List] = None):
        """流式运行代理处理查询

        Args:
            query: 用户查询
            chat_history: 聊天历史记录

        Returns:
            迭代器，产生流式响应
        """
        if not self.agent_executor:
            self.build()
            
        history = chat_history or []
        
        return self.agent_executor.stream({
            "input": query, 
            "chat_history": history
        }) 