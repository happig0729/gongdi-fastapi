# LangChain函数调用封装 - 阿里云千问版

这个项目演示了如何使用LangChain实现函数调用的Python类封装，适用于建筑工地智能助手等场景。项目现已支持阿里云千问大模型API。

## 项目结构

```
.
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── langchain_agent.py  # LangChain函数调用封装类
│   │   ├── dashscope_client.py # 阿里云千问API客户端
│   │   └── llm_config.py       # 大模型配置
│   ├── services/
│   │   ├── __init__.py
│   │   └── worker_service.py   # 工人服务模块示例
│   └── __init__.py
├── examples/
│   └── dashscope_demo.py       # 千问API使用示例
├── dashscope_demo.py           # 根目录示例脚本
├── example.py                  # LangChain函数调用示例
├── requirements.txt            # 项目依赖
├── setup.py                    # 包安装配置
└── README.md                   # 项目说明
```

## 功能特点

- 使用LangChain实现函数调用（Function Calling）的统一封装
- 支持直接添加函数或使用装饰器方式注册函数
- 自动处理函数文档字符串作为描述
- 支持同步调用和流式调用
- 内置聊天历史处理
- **新增**: 支持阿里云千问模型API

## 环境配置

1. 创建Python虚拟环境
```bash
uv venv
```

2. 安装依赖
```bash
uv pip install -r requirements.txt
```

3. 设置API密钥
```python
# 在代码中设置
os.environ["DASHSCOPE_API_KEY"] = "您的阿里云DashScope_API密钥"
```

## 使用方法 - 直接API调用

使用千问API客户端：

```python
from app.core.dashscope_client import DashscopeClient

# 创建千问API客户端
client = DashscopeClient()

# 创建消息
messages = client.format_messages(
    prompt="今天杭州天气怎么样？",
    system_message="你是一个建筑工地智能助手。"
)

# 发送聊天请求
response = client.chat(messages)
print(response['choices'][0]['message']['content'])

# 函数调用示例
tools = [...]  # 定义工具
response = client.function_call(messages, tools)
```

## 使用方法 - LangChain集成

使用千问大模型的LangChain封装示例：

```python
from langchain_dashscope import ChatDashscope
from app.core.langchain_agent import LangChainFunctionAgent

# 创建千问模型实例
llm = ChatDashscope(
    model="qwen-plus",  # 使用千问模型
    dashscope_api_key=os.environ.get("DASHSCOPE_API_KEY"),
    temperature=0,
)

# 创建LangChain函数调用代理
agent = LangChainFunctionAgent(
    llm=llm,
    system_message="你是一个建筑工地智能助手，可以回答关于工地情况的问题。"
)

# 添加函数...
# 构建代理...
# 使用方式与OpenAI模式相同
```

## 运行示例

运行千问API直接调用示例：
```bash
python dashscope_demo.py
```

运行LangChain函数调用示例：
```bash
python example.py
```

## 千问模型说明

目前项目支持的千问系列模型包括：
- qwen-plus: 通用对话模型，支持Function Calling
- qwen-max: 高级对话模型，支持更复杂的Function Calling
- qwen-turbo: 轻量级对话模型

更多模型参考：[阿里云模型列表](https://help.aliyun.com/zh/model-studio/getting-started/models)

## 故障排除

如果遇到问题，请检查：

1. API密钥是否正确设置
2. 网络连接是否正常
3. 是否安装了正确版本的依赖库

## 开发注意事项

- 使用 `dashscope` 库的 `Generation.call()` 方法调用千问API
- 注意处理API响应结果的格式
- 在测试时可以使用测试模式，避免频繁调用API

# 千问API服务

这是一个使用FastAPI封装阿里云千问大模型API的服务。

## 功能特性

- 支持简单聊天接口
- 支持函数调用
- 支持完整的函数调用流程
- 支持多轮对话
- 集成了常用工具函数（时间查询、天气查询）

## 安装

### 使用uv（推荐）

```bash
uv venv
uv venv activate
uv pip install -r requirements.txt
```

### 使用传统方式

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 运行服务

```bash
uvicorn app:app --reload
```

服务将在 http://localhost:8000 上运行。

## API接口

### 基础信息

- 接口文档: http://localhost:8000/docs
- 基础健康检查: GET http://localhost:8000/

### 聊天接口

- 简单聊天: POST http://localhost:8000/api/chat
- 函数调用: POST http://localhost:8000/api/function_call
- 完整函数调用流程: POST http://localhost:8000/api/complete_function_call
- 多轮对话: POST http://localhost:8000/api/multi_turn_chat

## 示例请求

### 简单聊天

```bash
curl -X 'POST' \
  'http://localhost:8000/api/chat' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "你好，请介绍一下你自己",
  "system_message": "你是一个建筑工地智能助手"
}'
```

### 函数调用

```bash
curl -X 'POST' \
  'http://localhost:8000/api/function_call' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "现在几点了？"
}'
```

### 完整函数调用流程

```bash
curl -X 'POST' \
  'http://localhost:8000/api/complete_function_call' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "今天杭州的天气怎么样？"
}'
```

### 多轮对话

```bash
curl -X 'POST' \
  'http://localhost:8000/api/multi_turn_chat' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "工地上的安全措施有哪些？",
  "history": [
    {
      "role": "user",
      "content": "我们工地上有多少工人？"
    },
    {
      "role": "assistant", 
      "content": "根据系统记录，目前工地上有120名工人在岗。"
    }
  ]
}'
```

## 环境变量

在生产环境中，请设置以下环境变量：

```
DASHSCOPE_API_KEY=你的阿里云API密钥
```

## 测试模式

在`app.py`中，可以设置`TEST_MODE = True`来启用测试模式，不需要真实的API调用。 