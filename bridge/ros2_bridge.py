"""
ROS/2 桥接器 v2.0 - 标准接口定义
专业机器人公司根据这个接口对接他们的硬件/仿真
"""
import logging
from typing import Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class JointNames:
    """标准 6 轴机械臂关节名（可配置）"""
    SHOULDER_PAN = "shoulder_pan_joint"
    SHOULDER_LIFT = "shoulder_lift_joint"
    ELBOW = "elbow_joint"
    WRIST_1 = "wrist_1_joint"
    WRIST_2 = "wrist_2_joint"
    WRIST_3 = "wrist_3_joint"
    
    @classmethod
    def all_joints(cls) -> list:
        return [cls.SHOULDER_PAN, cls.SHOULDER_LIFT, cls.ELBOW,
                cls.WRIST_1, cls.WRIST_2, cls.WRIST_3]


class ROS2Topics:
    """
    ClawsJoy 使用的标准 ROS/2 话题接口
    
    专业公司需要确保他们的机器人发布/订阅这些话题：
    """
    # 机械臂控制（发布）
    JOINT_TRAJECTORY = "/arm/joint_trajectory"      # trajectory_msgs/JointTrajectory
    
    # 夹爪控制（发布）
    GRIPPER_COMMAND = "/gripper/command"            # std_msgs/Float32 (0=闭 1=开)
    
    # 底盘控制（发布）
    CMD_VEL = "/base/cmd_vel"                       # geometry_msgs/Twist
    
    # 状态反馈（订阅）
    JOINT_STATES = "/arm/joint_states"              # sensor_msgs/JointState
    GRIPPER_STATE = "/gripper/state"                # std_msgs/Float32
    ODOMETRY = "/base/odom"                         # nav_msgs/Odometry
    
    # 感知（订阅）
    RGB_IMAGE = "/camera/rgb"                        # sensor_msgs/Image
    DEPTH_IMAGE = "/camera/depth"                    # sensor_msgs/Image
    OBJECT_DETECTIONS = "/perception/objects"        # vision_msgs/Detection3DArray
    
    # 语音（发布）
    TTS = "/speech/tts"                             # std_msgs/String
    
    # 紧急停止（发布）
    EMERGENCY_STOP = "/safety/estop"                # std_msgs/Bool


# ============================================================
#  动作 → ROS/2 消息映射表（专业公司根据此表实现驱动）
# ============================================================
MOTION_PRIMITIVE_TO_ROS2 = {
    # 移动类
    "navigate_to": {
        "topic": ROS2Topics.CMD_VEL,
        "msg_type": "geometry_msgs/Twist",
        "description": "根据目标位置计算速度指令，驱动底盘"
    },
    "move_arm": {
        "topic": ROS2Topics.JOINT_TRAJECTORY,
        "msg_type": "trajectory_msgs/JointTrajectory",
        "description": "将 target_pose 逆运动学解算为关节轨迹，发送到机械臂"
    },
    "move_base": {
        "topic": ROS2Topics.CMD_VEL,
        "msg_type": "geometry_msgs/Twist",
        "description": "直接速度控制"
    },
    
    # 操作类
    "grasp": {
        "topic": ROS2Topics.GRIPPER_COMMAND,
        "msg_type": "std_msgs/Float32",
        "params_map": {"force": "effort"},
        "description": "闭合夹爪，force 参数映射为夹持力"
    },
    "release": {
        "topic": ROS2Topics.GRIPPER_COMMAND,
        "msg_type": "std_msgs/Float32", 
        "value": 1.0,
        "description": "打开夹爪"
    },
    "push": {
        "topic": ROS2Topics.CMD_VEL,
        "msg_type": "geometry_msgs/Twist",
        "description": "短距离速度控制"
    },
    
    # 感知类
    "look_at": {
        "topic": None,
        "action": "move_head",
        "description": "控制云台/头部关节看向目标"
    },
    "detect_objects": {
        "subscribe": ROS2Topics.OBJECT_DETECTIONS,
        "msg_type": "vision_msgs/Detection3DArray",
        "description": "读取物体检测结果"
    },
    "get_pose": {
        "subscribe": [ROS2Topics.ODOMETRY, ROS2Topics.JOINT_STATES],
        "description": "读取里程计+关节状态，计算末端位姿"
    },
    
    # 交互类
    "speak": {
        "topic": ROS2Topics.TTS,
        "msg_type": "std_msgs/String",
        "description": "TTS 语音合成播放"
    },
    "play_gesture": {
        "topic": ROS2Topics.JOINT_TRAJECTORY,
        "msg_type": "trajectory_msgs/JointTrajectory",
        "description": "播放预定义的关节轨迹（挥手/点头等）"
    },
    
    # 系统类
    "wait": {
        "description": "纯延时，不发送 ROS/2 消息"
    },
    "emergency_stop": {
        "topic": ROS2Topics.EMERGENCY_STOP,
        "msg_type": "std_msgs/Bool",
        "value": True,
        "description": "紧急停止所有电机"
    },
}


# ============================================================
#  对接检查清单（给专业公司的文档）
# ============================================================
CHECKLIST = """
ClawsJoy Robotics 对接检查清单
================================

□ 1. 机械臂
    - 话题: {JOINT_TRAJECTORY} (发布)
    - 话题: {JOINT_STATES} (订阅)
    - 关节名: {JOINT_NAMES}

□ 2. 夹爪
    - 话题: {GRIPPER_COMMAND} (发布, Float32, 0=闭 1=开)
    - 话题: {GRIPPER_STATE} (订阅)

□ 3. 底盘
    - 话题: {CMD_VEL} (发布)
    - 话题: {ODOMETRY} (订阅)

□ 4. 摄像头
    - 话题: {RGB_IMAGE} (订阅)
    - 话题: {DEPTH_IMAGE} (订阅)

□ 5. 物体检测
    - 话题: {OBJECT_DETECTIONS} (订阅)

□ 6. 语音
    - 话题: {TTS} (发布)

□ 7. 安全
    - 话题: {EMERGENCY_STOP} (发布)

完成以上话题对接后，将 ClawsJoy Robotics 的 ros2_bridge.py 
中 mock_mode 设为 False，启动系统即可。
""".format(
    JOINT_TRAJECTORY=ROS2Topics.JOINT_TRAJECTORY,
    JOINT_STATES=ROS2Topics.JOINT_STATES,
    JOINT_NAMES=JointNames.all_joints(),
    GRIPPER_COMMAND=ROS2Topics.GRIPPER_COMMAND,
    GRIPPER_STATE=ROS2Topics.GRIPPER_STATE,
    CMD_VEL=ROS2Topics.CMD_VEL,
    ODOMETRY=ROS2Topics.ODOMETRY,
    RGB_IMAGE=ROS2Topics.RGB_IMAGE,
    DEPTH_IMAGE=ROS2Topics.DEPTH_IMAGE,
    OBJECT_DETECTIONS=ROS2Topics.OBJECT_DETECTIONS,
    TTS=ROS2Topics.TTS,
    EMERGENCY_STOP=ROS2Topics.EMERGENCY_STOP,
)


class ROS2Bridge:
    """ClawsJoy ←→ ROS/2 双向通信桥"""
    
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        
        if mock_mode:
            import sys, os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from mock_hardware import MockHardware
            self.hardware = MockHardware()
            logger.info("🔧 ROS/2 桥接器: 模拟模式")
        else:
            self._check_real_hardware()
            logger.info("🔌 ROS/2 桥接器: 真实模式")
    
    def _check_real_hardware(self):
        """检查真实硬件话题是否可用"""
        try:
            import rclpy
            rclpy.init()
            self.node = rclpy.create_node('clawsjoy_bridge')
            logger.info("   ROS/2 节点已创建")
        except Exception as e:
            logger.error(f"   ROS/2 初始化失败: {e}")
            raise
    
    def execute(self, primitive: str, params: Dict = None) -> Dict:
        params = params or {}
        
        if self.mock_mode:
            return self._execute_mock(primitive, params)
        else:
            return self._execute_real(primitive, params)
    
    def _execute_mock(self, primitive: str, params: Dict) -> Dict:
        method = getattr(self.hardware, primitive, None)
        if method is None:
            return {"success": False, "error": f"未知动作: {primitive}"}
        try:
            return method(params)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_real(self, primitive: str, params: Dict) -> Dict:
        """
        真实 ROS/2 执行
        
        专业公司在此实现：
        1. 查 MOTION_PRIMITIVE_TO_ROS2 获取话题和消息类型
        2. 将 params 转换为对应的 ROS/2 消息
        3. 发布消息
        4. 等待反馈
        5. 返回执行结果
        """
        mapping = MOTION_PRIMITIVE_TO_ROS2.get(primitive, {})
        topic = mapping.get("topic")
        msg_type = mapping.get("msg_type", "unknown")
        
        logger.info(f"[ROS2] 执行: {primitive} → {topic} ({msg_type})")
        
        # TODO: 实现消息转换和发布
        # 参考 MOTION_PRIMITIVE_TO_ROS2 映射表
        
        return {
            "success": False,
            "error": "真实 ROS/2 执行需要对接硬件驱动",
            "topic": topic,
            "msg_type": msg_type,
            "primitive": primitive,
            "params": params
        }
    
    def get_status(self) -> Dict:
        if self.mock_mode:
            return self.hardware.get_pose({})
        return {"success": True}
    
    def get_checklist(self) -> str:
        """返回对接检查清单"""
        return CHECKLIST
    
    def get_topic_mapping(self) -> Dict:
        """返回完整的话题映射"""
        return MOTION_PRIMITIVE_TO_ROS2
    
    def shutdown(self):
        if not self.mock_mode and hasattr(self, 'node'):
            self.node.destroy_node()
        logger.info("桥接器已关闭")


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bridge = ROS2Bridge(mock_mode=True)
    
    print("=" * 60)
    print("ClawsJoy Robotics - ROS/2 接口规范")
    print("=" * 60)
    print(CHECKLIST)
    print("=" * 60)
    print(f"\n共定义 {len(MOTION_PRIMITIVE_TO_ROS2)} 个动作映射")
    
    bridge.shutdown()
