# 工地智能助手 - FastAPI 服务

这是一个基于 FastAPI 和阿里云千问大模型的智能助手服务，专为建筑工地场景设计。项目集成了 LangChain 函数调用功能，支持多轮对话和工具函数调用。

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
├── app.py                      # FastAPI 主应用
├── example.py                  # LangChain函数调用示例
├── requirements.txt            # 项目依赖
├── setup.py                    # 包安装配置
└── README.md                   # 项目说明
```

## 功能特点

- 基于 FastAPI 构建的 RESTful API 服务
- 集成阿里云千问大模型 API
- 支持 LangChain 函数调用（Function Calling）
- 支持多轮对话和上下文管理
- 内置常用工具函数（时间查询、天气查询等）
- 支持同步调用和流式响应
- 完整的 API 文档（Swagger UI）

## 环境配置

1. 创建 Python 虚拟环境（推荐使用 uv）
```bash
uv venv
uv venv activate
```

2. 安装依赖
```bash
uv pip install -r requirements.txt
```

3. 配置环境变量
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="您的阿里云DashScope_API密钥"

# 或创建 .env 文件
DASHSCOPE_API_KEY=您的阿里云DashScope_API密钥
```

## 运行服务

```bash
uvicorn app:app --reload
```

服务将在 http://localhost:8000 上运行。

## API 接口

### 基础信息

- API 文档: http://localhost:8000/docs
- 健康检查: GET http://localhost:8000/

### 主要接口

1. 简单聊天
```bash
POST /api/chat
{
  "prompt": "你好，请介绍一下你自己",
  "system_message": "你是一个建筑工地智能助手"
}
```

2. 函数调用
```bash
POST /api/function_call
{
  "query": "现在几点了？"
}
```

3. 完整函数调用流程
```bash
POST /api/complete_function_call
{
  "query": "今天杭州的天气怎么样？"
}
```

4. 多轮对话
```bash
POST /api/multi_turn_chat
{
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
}
```

## 开发指南

### 添加新的工具函数

1. 在 `app/services` 目录下创建新的服务模块
2. 使用装饰器注册函数：

```python
from app.core.langchain_agent import register_function

@register_function
def get_weather(location: str) -> str:
    """获取指定城市的天气信息"""
    # 实现函数逻辑
    return weather_info
```

### 错误处理

服务使用统一的错误处理机制：
- 400: 请求参数错误
- 401: 认证失败
- 500: 服务器内部错误

## 性能优化

- 使用异步处理提高并发性能
- 实现请求限流和缓存机制
- 支持流式响应减少等待时间

## 部署建议

1. 使用 Gunicorn 作为生产环境服务器
```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. 配置 Nginx 反向代理
3. 使用 Supervisor 管理进程
4. 配置日志轮转

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 