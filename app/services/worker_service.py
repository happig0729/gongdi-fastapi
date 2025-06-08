"""
工人服务模块

提供与工地工人相关的数据和业务逻辑
"""
from typing import Dict, List, Any, Optional

class WorkerService:
    """工人服务类"""
    
    def __init__(self):
        # 模拟数据库
        self.workers_data = {
            "在场工人": [
                {"id": 1, "name": "张三", "position": "混凝土工", "status": "在岗"},
                {"id": 2, "name": "李四", "position": "钢筋工", "status": "在岗"},
                {"id": 3, "name": "王五", "position": "电工", "status": "在岗"},
                {"id": 4, "name": "赵六", "position": "木工", "status": "在岗"},
                {"id": 5, "name": "孙七", "position": "泥水工", "status": "在岗"},
            ],
            "请假工人": [
                {"id": 6, "name": "周八", "position": "搬运工", "status": "请假"},
                {"id": 7, "name": "吴九", "position": "焊接工", "status": "请假"},
            ],
            "离场工人": [
                {"id": 8, "name": "郑十", "position": "涂装工", "status": "已离场"},
            ]
        }
    
    def count_workers(self, status: str = "在岗") -> int:
        """统计指定状态的工人数量
        
        Args:
            status: 工人状态，可选值：在岗、请假、已离场、全部
            
        Returns:
            符合条件的工人数量
        """
        if status == "全部":
            return sum(len(workers) for workers in self.workers_data.values())
        
        status_mapping = {
            "在岗": "在场工人",
            "请假": "请假工人",
            "已离场": "离场工人"
        }
        
        if status not in status_mapping:
            return 0
            
        return len(self.workers_data[status_mapping[status]])
    
    def get_workers(self, status: str = "在岗") -> List[Dict[str, Any]]:
        """获取指定状态的工人列表
        
        Args:
            status: 工人状态，可选值：在岗、请假、已离场、全部
            
        Returns:
            符合条件的工人列表
        """
        if status == "全部":
            all_workers = []
            for workers in self.workers_data.values():
                all_workers.extend(workers)
            return all_workers
        
        status_mapping = {
            "在岗": "在场工人",
            "请假": "请假工人",
            "已离场": "离场工人"
        }
        
        if status not in status_mapping:
            return []
            
        return self.workers_data[status_mapping[status]] 