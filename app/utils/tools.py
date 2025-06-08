"""
工具函数模块
"""
import datetime
from typing import Dict, Any

def get_current_time() -> Dict[str, str]:
    """获取当前时间"""
    current_time = datetime.datetime.now()
    return {
        "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "date": current_time.strftime("%Y-%m-%d"),
        "time": current_time.strftime("%H:%M:%S"),
        "weekday": current_time.strftime("%A")
    }

def get_current_weather(location: str) -> Dict[str, str]:
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