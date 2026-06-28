"""
硬件模拟器 - 无实体机器人时的开发测试工具
实现所有 motion_primitives 的模拟行为
"""
import time
import random
import logging

logger = logging.getLogger(__name__)


class MockHardware:
    """模拟机器人硬件，返回合理的假数据"""
    
    def __init__(self, known_objects: dict = None):
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.orientation = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        self.grasped_object = None
        
        # 默认物体库（模拟一个典型家庭环境）
        self.known_objects = known_objects or {
            "cup_01": {"type": "cup", "position": {"x": 1.0, "y": 0.5, "z": 0.8}, "properties": {"color": "blue"}},
            "cup_02": {"type": "cup", "position": {"x": 1.1, "y": 0.6, "z": 0.8}, "properties": {"color": "white"}},
            "bottle_01": {"type": "bottle", "position": {"x": 0.8, "y": -0.3, "z": 0.7}, "properties": {"full": True}},
            "book_01": {"type": "book", "position": {"x": 0.5, "y": 0.2, "z": 0.3}, "properties": {"title": "机器人学导论"}},
            "book_02": {"type": "book", "position": {"x": 0.6, "y": 0.1, "z": 0.3}, "properties": {"title": "ROS/2实战"}},
            "remote_01": {"type": "remote", "position": {"x": 1.5, "y": 0.8, "z": 0.5}, "properties": {"device": "TV"}},
            "phone_01": {"type": "phone", "position": {"x": 0.3, "y": -0.5, "z": 0.4}, "properties": {"brand": "iPhone"}},
            "box_01": {"type": "box", "position": {"x": -0.5, "y": 0.0, "z": 0.2}, "properties": {"weight_kg": 2.0}},
        }
        
        logger.info(f"🔧 模拟硬件已初始化 ({len(self.known_objects)} 个已知物体)")
    
    # ===== 移动类 =====
    def navigate_to(self, params):
        target = params.get("target_location", "unknown")
        logger.info(f"[Mock] 导航到: {target}")
        time.sleep(random.uniform(0.3, 0.8))
        
        # 模拟到达目标位置
        if target in self.known_objects:
            self.position = self.known_objects[target]["position"].copy()
            self.position["x"] -= 0.3  # 停在物体前方
        else:
            self.position = {"x": random.uniform(0, 2), "y": random.uniform(-1, 1), "z": 0.0}
        
        return {"success": True, "position_reached": target}
    
    def move_arm(self, params):
        pose = params.get("target_pose", {})
        logger.info(f"[Mock] 移动机械臂到: {pose}")
        time.sleep(0.3)
        return {"success": True, "current_pose": pose}
    
    def move_base(self, params):
        distance = params.get("linear", {}).get("x", 0)
        self.position["x"] += distance
        logger.info(f"[Mock] 底盘移动: {distance}m, 当前位置: {self.position}")
        time.sleep(0.3)
        return {"success": True}
    
    # ===== 操作类 =====
    def grasp(self, params):
        object_id = params.get("object_id", "")
        force = params.get("force", 1.0)
        
        if object_id in self.known_objects:
            self.grasped_object = object_id
            self.known_objects[object_id]["position"] = self.position.copy()
            logger.info(f"[Mock] 抓取: {object_id} (力={force}N)")
            time.sleep(0.5)
            return {"success": True, "grasped_object": object_id}
        
        # 未知物体：尝试抓取（模拟失败率）
        if random.random() < 0.3:
            logger.warning(f"[Mock] 抓取失败: {object_id} 不存在")
            return {"success": False, "grasped_object": None, "error": f"未找到物体: {object_id}"}
        
        # 动态添加到已知物体
        self.known_objects[object_id] = {
            "type": "unknown",
            "position": self.position.copy(),
            "properties": {}
        }
        self.grasped_object = object_id
        logger.info(f"[Mock] 抓取新物体: {object_id}")
        return {"success": True, "grasped_object": object_id}
    
    def release(self, params):
        obj = self.grasped_object
        drop_height = params.get("drop_height", 0.05)
        
        if obj and obj in self.known_objects:
            pos = self.position.copy()
            pos["z"] = drop_height
            self.known_objects[obj]["position"] = pos
        
        self.grasped_object = None
        logger.info(f"[Mock] 释放: {obj} (高度={drop_height}m)")
        time.sleep(0.2)
        return {"success": True}
    
    def push(self, params):
        obj_id = params.get("object_id", "")
        direction = params.get("direction", "forward")
        distance = params.get("distance_cm", 10.0) / 100
        
        if obj_id in self.known_objects:
            if direction == "forward":
                self.known_objects[obj_id]["position"]["x"] += distance
            elif direction == "backward":
                self.known_objects[obj_id]["position"]["x"] -= distance
            elif direction == "left":
                self.known_objects[obj_id]["position"]["y"] += distance
            elif direction == "right":
                self.known_objects[obj_id]["position"]["y"] -= distance
        
        logger.info(f"[Mock] 推动: {obj_id} → {direction} {distance}m")
        time.sleep(0.4)
        return {"success": True}
    
    # ===== 感知类 =====
    def look_at(self, params):
        target = params.get("target", "front")
        logger.info(f"[Mock] 看向: {target}")
        time.sleep(0.2)
        return {"success": True, "image_data": "mock_base64_image"}
    
    def detect_objects(self, params):
        types = params.get("object_types", [])
        min_conf = params.get("min_confidence", 0.5)
        
        objects = []
        for oid, info in self.known_objects.items():
            if types and info["type"] not in types:
                continue
            # 模拟：5% 概率检测失败
            if random.random() < 0.05:
                continue
            objects.append({
                "id": oid,
                "type": info["type"],
                "bbox": [random.randint(50, 200) for _ in range(4)],
                "confidence": random.uniform(min_conf, 0.99)
            })
        
        logger.info(f"[Mock] 检测到 {len(objects)} 个物体 (类型过滤: {types or '全部'})")
        time.sleep(0.3)
        return {"success": True, "objects": objects}
    
    def get_pose(self, params=None):
        return {
            "success": True,
            "position": self.position,
            "orientation": self.orientation
        }
    
    # ===== 交互类 =====
    def speak(self, params):
        text = params.get("text", "")
        speed = params.get("speed", 1.0)
        logger.info(f"[Mock] 语音播报 (速度={speed}x): {text}")
        time.sleep(min(len(text) * 0.03, 2.0))
        return {"success": True}
    
    def play_gesture(self, params):
        gesture = params.get("gesture_name", "wave")
        duration = params.get("duration_ms", 2000) / 1000
        logger.info(f"[Mock] 播放动作: {gesture} ({duration}s)")
        time.sleep(min(duration, 1.0))
        return {"success": True}
    
    # ===== 系统类 =====
    def wait(self, params):
        duration = params.get("duration_ms", 1000) / 1000
        logger.info(f"[Mock] 等待 {duration}s")
        time.sleep(min(duration, 2.0))
        return {"success": True}
    
    def emergency_stop(self, params=None):
        self.grasped_object = None
        logger.info("[Mock] ⚠️ 紧急停止 - 所有动作已中止")
        return {"success": True}
    
    def get_known_objects(self) -> dict:
        """导出当前物体状态（供 world_model 同步）"""
        return self.known_objects


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    hw = MockHardware()
    
    print("=== 硬件模拟器测试 ===\n")
    
    # 初始检测
    result = hw.detect_objects({})
    print(f"初始检测: {len(result['objects'])} 个物体")
    for obj in result['objects'][:3]:
        print(f"  📦 {obj['id']} ({obj['type']}) conf={obj['confidence']:.2f}")
    
    # 抓取 + 释放
    print(f"\n抓取: {hw.grasp({'object_id': 'book_01'})}")
    print(f"释放: {hw.release({'object_id': 'book_01'})}")
    
    # 未知物体
    print(f"\n未知物体: {hw.grasp({'object_id': 'unknown_thing'})}")
    
    # 紧急停止
    print(f"紧急停止: {hw.emergency_stop()}")
    
    print(f"\n✅ 模拟器正常 (物体数: {len(hw.known_objects)})")
