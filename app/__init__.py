"""
应用包初始化文件
""" 

import sys
import os

# 把上层目录添加到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接从上层目录的app.py导入FastAPI实例
from sys import modules
if 'app' in modules and hasattr(modules['app'], 'app'):
    app = modules['app'].app
else:
    # 如果app.py尚未被导入，则手动导入
    import importlib.util
    spec = importlib.util.spec_from_file_location("app_module", 
                                                  os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"))
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    app = app_module.app 