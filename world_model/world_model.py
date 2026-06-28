"""
世界模型 - 物理世界的数字孪生
存储和管理物体、位置、空间关系
"""
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PhysicalObject:
    """物理物体"""
    object_id: str
    obj_type: str
    location: Dict
    orientation: Dict = field(default_factory=lambda: {"roll": 0, "pitch": 0, "yaw": 0})
    status: str = "static"
    properties: Dict = field(default_factory=dict)
    last_seen: float = 0.0
    confidence: float = 1.0


class WorldModel:
    """
    物理世界知识图谱
    
    职责：
    1. 维护当前环境中的物体清单
    2. 记录物体位置和状态变化
    3. 提供空间查询
    4. 与 MemoryBank 协同，记录长期空间记忆
    """
    
    def __init__(self):
        self.objects: Dict[str, PhysicalObject] = {}
        self.robot_position: Dict = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.robot_orientation: Dict = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        self.known_locations: Dict[str, Dict] = {
            "home": {"x": 0.0, "y": 0.0, "z": 0.0},
            "table": {"x": 1.0, "y": 0.5, "z": 0.0},
            "counter": {"x": 0.8, "y": -0.3, "z": 0.0},
            "door": {"x": 2.0, "y": 0.0, "z": 0.0},
            "window": {"x": -1.0, "y": 0.0, "z": 0.0},
            "bookshelf": {"x": 0.5, "y": 0.0, "z": 0.0},
        }
        logger.info("🌍 世界模型已初始化")
    
    # ===== 从硬件同步 =====
    def sync_from_hardware(self, known_objects: dict):
        """从硬件模拟器/真实机器人同步物体状态"""
        for obj_id, info in known_objects.items():
            self.add_object(
                object_id=obj_id,
                obj_type=info.get("type", "unknown"),
                location=info.get("position", {"x": 0, "y": 0, "z": 0}),
                properties=info.get("properties", {})
            )
        logger.info(f"  📡 从硬件同步了 {len(known_objects)} 个物体")
    
    # ===== 物体管理 =====
    def add_object(self, object_id: str, obj_type: str, location: Dict,
                   properties: Dict = None) -> PhysicalObject:
        """添加或更新物体"""
        obj = PhysicalObject(
            object_id=object_id,
            obj_type=obj_type,
            location=location,
            properties=properties or {},
            last_seen=time.time()
        )
        self.objects[object_id] = obj
        return obj
    
    def update_object(self, object_id: str, **kwargs) -> bool:
        """更新物体属性"""
        if object_id not in self.objects:
            return False
        obj = self.objects[object_id]
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        obj.last_seen = time.time()
        return True
    
    def remove_object(self, object_id: str) -> bool:
        """移除物体"""
        if object_id in self.objects:
            del self.objects[object_id]
            return True
        return False
    
    def get_object(self, object_id: str) -> Optional[PhysicalObject]:
        """查询物体"""
        return self.objects.get(object_id)
    
    # ===== 空间查询 =====
    def find_objects(self, obj_type: str = None, location: str = None,
                     status: str = None, limit: int = None) -> List[PhysicalObject]:
        """按条件查找物体"""
        results = list(self.objects.values())
        
        if obj_type:
            results = [o for o in results if o.obj_type == obj_type]
        if location:
            loc = self.known_locations.get(location)
            if loc:
                results = [o for o in results if self._distance(o.location, loc) < 0.5]
        if status:
            results = [o for o in results if o.status == status]
        
        return results[:limit] if limit else results
    
    def objects_at_location(self, location_name: str) -> List[PhysicalObject]:
        """查询指定位置上的所有物体"""
        return self.find_objects(location=location_name)
    
    def nearest_object(self, obj_type: str) -> Optional[PhysicalObject]:
        """找到最近指定类型的物体"""
        candidates = self.find_objects(obj_type=obj_type)
        if not candidates:
            return None
        return min(candidates, key=lambda o: self._distance(o.location, self.robot_position))
    
    # ===== 机器人状态 =====
    def update_robot_pose(self, position: Dict, orientation: Dict = None):
        """更新机器人位置"""
        self.robot_position = position
        if orientation:
            self.robot_orientation = orientation
    
    def get_robot_pose(self) -> Dict:
        return {
            "position": self.robot_position,
            "orientation": self.robot_orientation
        }
    
    # ===== 位置管理 =====
    def add_location(self, name: str, position: Dict):
        self.known_locations[name] = position
    
    def get_location(self, name: str) -> Optional[Dict]:
        return self.known_locations.get(name)
    
    # ===== 工具方法 =====
    def _distance(self, pos1: Dict, pos2: Dict) -> float:
        dx = pos1.get("x", 0) - pos2.get("x", 0)
        dy = pos1.get("y", 0) - pos2.get("y", 0)
        dz = pos1.get("z", 0) - pos2.get("z", 0)
        return (dx**2 + dy**2 + dz**2) ** 0.5
    
    def get_stale_objects(self, max_age_seconds: float = 300) -> List[str]:
        """获取超时未见的物体"""
        now = time.time()
        return [oid for oid, obj in self.objects.items() 
                if now - obj.last_seen > max_age_seconds]
    
    def summary(self) -> Dict:
        """世界模型摘要"""
        return {
            "total_objects": len(self.objects),
            "object_types": list(set(o.obj_type for o in self.objects.values())),
            "known_locations": list(self.known_locations.keys()),
            "robot_position": self.robot_position,
            "grasped": [oid for oid, o in self.objects.items() if o.status == "grasped"],
            "objects": {
                oid: {"type": o.obj_type, "location": o.location, "status": o.status}
                for oid, o in self.objects.items()
            }
        }


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    wm = WorldModel()
    
    print("=== 世界模型测试 ===\n")
    
    # 模拟从硬件同步
    mock_objects = {
        "cup_01": {"type": "cup", "position": {"x": 1.0, "y": 0.5, "z": 0.8}, "properties": {"color": "blue"}},
        "book_01": {"type": "book", "position": {"x": 0.5, "y": 0.2, "z": 0.3}, "properties": {"title": "AI导论"}},
        "bottle_01": {"type": "bottle", "position": {"x": 0.8, "y": -0.3, "z": 0.7}, "properties": {}},
    }
    wm.sync_from_hardware(mock_objects)
    wm.update_robot_pose({"x": 0.0, "y": 0.0, "z": 0.0})
    
    print(f"同步后物体数: {len(wm.objects)}")
    print(f"最近的杯子: {wm.nearest_object('cup').object_id}")
    print(f"桌子上的物体: {[o.object_id for o in wm.objects_at_location('table')]}")
    
    # 抓取
    wm.update_object("cup_01", status="grasped")
    print(f"\n抓取状态: {wm.summary()['grasped']}")
    
    print("\n✅ 世界模型正常")
