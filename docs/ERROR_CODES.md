# ClawsJoy Robotics 错误码

## 动作执行错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `未找到物体: xxx` | 物体不在世界模型里 | 确认物体已通过 detect_objects 发现，或在 config 的 initial_objects 里注册 |
| `未知动作: xxx` | 调用了 motion_primitives.yaml 之外的动作 | 检查拼写，或添加新动作 |
| `执行失败于: grasp` | 夹爪闭合失败 | 检查夹爪话题、力控参数 |
| `执行失败于: navigate_to` | 导航失败 | 检查底盘话题、目标位置是否可达 |

## ROS/2 通信错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `ROS/2 不可用` | 未安装 rclpy 或环境没 source | `source /opt/ros/humble/setup.bash` |
| `话题无订阅者` | 机器人驱动未启动 | 检查机器人驱动进程 |
| `消息类型不匹配` | 话题的消息类型与预期不同 | 对照 `bridge/ros2_bridge.py` 的输出确认 |

## 配置错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `未注册的物体类型: xxx` | object_aliases.yaml 里没有这个别名 | 添加映射 |
| `关节名不匹配` | robot_config.yaml 的 joint_names 与实际不同 | 对照 `ros2 topic echo /arm/joint_states` 修正 |
EOF

echo "✅ ERROR_CODES.md 已创建"
第四步：对接示例
bash
cat > ~/clawsjoy_robotics/docs/INTEGRATION_UR5.md << 'EOF'
# UR5e 对接示例

## 环境准备

```bash
# 安装 UR 驱动
sudo apt install ros-humble-ur-robot-driver ros-humble-ur-description

# 启动 UR5e 驱动（真机或仿真）
ros2 launch ur_bringup ur_control.launch.py ur_type:=ur5e robot_ip:=192.168.1.100
确认话题
bash
ros2 topic list | grep -E "joint|gripper|io"
# 应看到:
# /joint_states
# /scaled_joint_trajectory_controller/joint_trajectory
# /io_and_status_controller/io_states
配置 ClawsJoy
编辑 config/robot_config.yaml：

yaml
robot:
  arm:
    model: "ur5e"
    dof: 6
    joint_names:
      - shoulder_pan_joint
      - shoulder_lift_joint
      - elbow_joint
      - wrist_1_joint
      - wrist_2_joint
      - wrist_3_joint
    gripper:
      type: "robotiq_2f"          # UR 常用夹爪
      max_open_mm: 85
      
  ros2_topics:
    arm_joint_trajectory: "/scaled_joint_trajectory_controller/joint_trajectory"
    arm_joint_states: "/joint_states"
    gripper_command: "/gripper/command"
测试
bash
python3 -c "
from robotics_agent import RoboticsAgentV4
agent = RoboticsAgentV4(mock_mode=False)
print(agent.process('拿水杯')['response'])
"
预期结果
UR5e 执行 6 步动作序列：

摄像头看向桌子

检测到水杯

机械臂移动到桌子附近

末端接近水杯

夹爪闭合抓取

语音播报 "已拿到水杯"
