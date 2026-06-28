"""
任务规划器 - 将自然语言任务分解为动作原语序列
"""
import sys
import os
import logging
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, '/home/flybo/clawsjoy_v5')

from world_model.world_model import WorldModel
from bridge.ros2_bridge import ROS2Bridge

logger = logging.getLogger(__name__)

# 自然语言 → 物体类型映射
# 从配置文件加载（专业公司修改 config/object_aliases.yaml 即可）
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import get_object_aliases
OBJECT_ALIASES = get_object_aliases()


class TaskPlanner:
    """任务规划器 - 任务→动作序列→执行→监控"""
    
    def __init__(self, world_model: WorldModel = None, bridge: ROS2Bridge = None):
        self.world_model = world_model or WorldModel()
        self.bridge = bridge or ROS2Bridge(mock_mode=True)
        
        self.task_templates = {
            "收拾": self._plan_cleanup,
            "整理": self._plan_cleanup,
            "巡逻": self._plan_patrol,
            "介绍自己": self._plan_introduce,
            "自我介绍": self._plan_introduce,
        }
        
        logger.info("📋 任务规划器已初始化")
    
    def plan(self, task: str, params: Dict = None) -> Dict:
        """规划并执行任务"""
        params = params or {}
        
        # 特殊处理：拿X物体
        fetch_prefixes_with_action = ["帮我拿", "帮我取", "请帮我拿", "请帮我取"]
        fetch_prefixes_help = ["帮我", "请帮我"]
        fetch_keywords = ["拿", "取", "给我", "递给我", "拿来"]
        
        cleaned_task = task
        
        # 先匹配带动作的前缀（去掉后剩下的直接就是物体名）
        for prefix in fetch_prefixes_with_action:
            if cleaned_task.startswith(prefix):
                obj_name = cleaned_task[len(prefix):].strip()
                if obj_name:
                    return self._fetch_object(obj_name)
        
        # 再匹配纯帮助前缀（需要从剩余文本里找动作关键词）
        for prefix in fetch_prefixes_help:
            if cleaned_task.startswith(prefix):
                cleaned_task = cleaned_task[len(prefix):].strip()
                break
        
        # 从 cleaned_task 里找动作关键词 + 物体名
        for kw in fetch_keywords:
            if kw in cleaned_task:
                obj_name = cleaned_task.replace(kw, "").strip()
                if obj_name:
                    return self._fetch_object(obj_name)
        
        # 查找任务模板
        for key, func in self.task_templates.items():
            if key in task:
                return self.execute_plan(func(params))
        
        # 无模板
        return self.execute_plan(self._plan_generic(task, params))
    
    def _fetch_object(self, obj_name: str) -> Dict:
        """拿取物体的完整流程"""
        # 解析物体类型
        obj_type = OBJECT_ALIASES.get(obj_name, obj_name)
        
        # 查世界模型
        obj = self.world_model.nearest_object(obj_type)
        
        if obj:
            obj_id = obj.object_id
            location = obj.location
            logger.info(f"  找到 {obj_id} 在 {location}")
        else:
            # 世界模型里没有，假设在桌子上
            obj_id = f"{obj_type}_01"
            location = self.world_model.get_location("table") or {"x": 1.0, "y": 0.5, "z": 0.8}
            logger.info(f"  未找到 {obj_type}，假设位置: {location}")
        
        plan = [
            {"action": "look_at", "params": {"target": "table"}},
            {"action": "detect_objects", "params": {"object_types": [obj_type]}},
            {"action": "navigate_to", "params": {"target_location": "table"}},
            {"action": "move_arm", "params": {"target_pose": location}},
            {"action": "grasp", "params": {"object_id": obj_id}},
            {"action": "speak", "params": {"text": f"已拿到{obj_name}"}},
        ]
        
        return self.execute_plan(plan)
    
    def execute_plan(self, plan: List[Dict]) -> Dict:
        """执行动作序列"""
        results = []
        for step in plan:
            action = step["action"]
            params = step.get("params", {})
            
            logger.info(f"  ▶ {action}({params})")
            result = self.bridge.execute(action, params)
            results.append({"step": action, "result": result})
            
            if not result.get("success"):
                logger.error(f"  ✖ 失败于: {action}")
                return {
                    "success": False,
                    "failed_at": action,
                    "results": results,
                    "steps": len(results),
                    "error": result.get("error", "执行失败")
                }
            
            self._update_world_model(action, params, result)
        
        return {"success": True, "steps": len(results), "results": results}
    
    def _plan_cleanup(self, params: Dict) -> List[Dict]:
        return [
            {"action": "look_at", "params": {"target": "table"}},
            {"action": "detect_objects", "params": {}},
            {"action": "speak", "params": {"text": "开始收拾桌子"}},
            {"action": "grasp", "params": {"object_id": "cup_01"}},
            {"action": "navigate_to", "params": {"target_location": "counter"}},
            {"action": "release", "params": {"object_id": "cup_01"}},
            {"action": "speak", "params": {"text": "收拾完成"}},
        ]
    
    def _plan_patrol(self, params: Dict) -> List[Dict]:
        return [
            {"action": "navigate_to", "params": {"target_location": "door"}},
            {"action": "look_at", "params": {"target": "front"}},
            {"action": "speak", "params": {"text": "巡逻点1正常"}},
            {"action": "navigate_to", "params": {"target_location": "table"}},
            {"action": "look_at", "params": {"target": "left"}},
            {"action": "speak", "params": {"text": "巡逻点2正常"}},
        ]
    
    def _plan_introduce(self, params: Dict) -> List[Dict]:
        return [
            {"action": "play_gesture", "params": {"gesture_name": "wave"}},
            {"action": "speak", "params": {"text": "你好，我是ClawsJoy机器人，我能帮你拿东西、巡逻、收拾桌子"}},
        ]
    
    def _plan_generic(self, task: str, params: Dict) -> List[Dict]:
        logger.warning(f"无模板: {task}")
        return [
            {"action": "speak", "params": {"text": f"收到任务：{task}，但我不确定该怎么做"}},
        ]
    
    def _update_world_model(self, action: str, params: Dict, result: Dict):
        if action == "navigate_to":
            target = params.get("target_location", "")
            loc = self.world_model.get_location(target) or {"x": 0, "y": 0, "z": 0}
            self.world_model.update_robot_pose(loc)
        elif action == "grasp":
            obj_id = params.get("object_id", "")
            self.world_model.update_object(obj_id, status="grasped")
        elif action == "release":
            obj_id = params.get("object_id", "")
            self.world_model.update_object(obj_id, status="static",
                                           location=self.world_model.robot_position)


# ===== 测试 =====
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    wm = WorldModel()
    wm.add_object("cup_01", "cup", {"x": 1.0, "y": 0.5, "z": 0.8}, {"color": "blue"})
    wm.add_object("bottle_01", "bottle", {"x": 0.8, "y": -0.3, "z": 0.7})
    wm.update_robot_pose({"x": 0.0, "y": 0.0, "z": 0.0})
    
    planner = TaskPlanner(world_model=wm)
    
    print("=" * 50)
    print("任务规划器测试")
    print("=" * 50)
    
    print("\n--- 测试1: 拿水杯 ---")
    result = planner.plan("拿水杯")
    status = "✅" if result["success"] else "❌"
    print(f"\n{status} 完成 {result['steps']} 步")
    
    print("\n--- 测试2: 未知任务 ---")
    result = planner.plan("跳个舞")
    status = "⚠️ 预期无法执行" if not result["success"] else "✅"
    print(f"\n{status}")
    
    print("\n✅ 规划器正常")
