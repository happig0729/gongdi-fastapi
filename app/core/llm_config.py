"""
大模型配置

用于配置阿里云千问大模型的相关设置
"""

import os

# 大模型配置
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")  # 阿里云DashScope API密钥

# 默认使用的模型
DEFAULT_MODEL = "qwen-turbo"  # 可选模型请参考：https://help.aliyun.com/zh/model-studio/getting-started/models

# 默认参数
DEFAULT_TEMPERATURE = 0  # 温度参数，控制输出的随机性
DEFAULT_MAX_TOKENS = 2048  # 最大生成token数量

# 工具配置
DEFAULT_TOOLS = [
    # 示例工具配置
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
            "parameters": {}  # 因为获取当前时间无需输入参数，因此parameters为空字典
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {  
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                    }
                },
                "required": ["location"]
            }
        }
    }
] 