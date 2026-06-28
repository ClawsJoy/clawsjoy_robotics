# ClawsJoy Robotics API 文档

## RoboticsAgentV4

### `__init__(user_id="default", mock_mode=True)`

创建机器人认知引擎实例。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| user_id | str | "default" | 多租户隔离标识 |
| mock_mode | bool | True | True=模拟模式 False=真实ROS/2 |

### `process(user_input: str, context=None) -> dict`

执行自然语言任务。

**输入**：
| 参数 | 类型 | 说明 |
|------|------|------|
| user_input | str | 自然语言任务，如"拿水杯"、"巡逻" |

**返回值**：
```json
{
  "success": true,
  "response": "✅ 完成任务，共执行 6 个动作",
  "steps": 6,
  "details": [
    {"step": "look_at", "result": {"success": true}},
    {"step": "detect_objects", "result": {"success": true, "objects": [...]}},
    ...
  ]
}
错误返回：

json
{
  "success": false,
  "response": "❌ 执行失败于: grasp",
  "error": "未找到物体: cup_01"
}
get_world_summary() -> dict
获取世界模型摘要。

返回值：

json
{
  "total_objects": 8,
  "object_types": ["cup", "book", "bottle"],
  "known_locations": ["home", "table", "counter"],
  "robot_position": {"x": 0.0, "y": 0.0, "z": 0.0},
  "grasped": ["cup_01"]
}
WorldModel
add_object(object_id, obj_type, location, properties=None)
添加物体到世界模型。

nearest_object(obj_type) -> PhysicalObject
找最近指定类型的物体。

objects_at_location(location_name) -> list
查指定位置上的所有物体。

update_object(object_id, **kwargs)
更新物体状态（位置、抓取状态等）。

sync_from_hardware(known_objects: dict)
从硬件同步物体列表。

ROS2Bridge
execute(primitive: str, params: dict) -> dict
执行单个标准动作。

支持的动作：navigate_to, move_arm, grasp, release, look_at, detect_objects, get_pose, speak, play_gesture, wait, emergency_stop

get_topic_mapping() -> dict
返回动作→ROS/2话题的完整映射。

get_checklist() -> str
返回对接检查清单。

配置文件
config/robot_config.yaml
机器人参数：机械臂型号、关节名、话题名、已知位置、初始物体。

config/object_aliases.yaml
自然语言→物体类型映射。

config/task_templates.yaml
任务模板：关键词→动作序列。
