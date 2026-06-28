# ClawsJoy Robotics

ClawsJoy 具身智能延申版 — 将认知框架连接到物理机器人。

## 架构
用户: "拿水杯"
↓
ClawsJoy 主版 (cortex) → 意图识别 → action
↓
Robotics Agent
├ planner → 任务→动作序列 (拿→[看,检测,导航,抓取,播报])
├ world_model → 物理世界知识图谱 (物体在哪,什么状态)
└ bridge → ROS/2 通信 (真实) 或 Mock (模拟)
↓
机器人执行

## 快速开始

```bash
# 安装
./install.sh

# 测试
python3 tests/test_e2e.py

# 运行
python3 robotics_agent.py
##目录结构
clawsjoy_robotics/
├── motion_primitives.yaml    # 12个标准动作定义
├── robotics_agent.py         # 统一入口
├── bridge/
│   ├── mock_hardware.py      # 模拟硬件
│   └── ros2_bridge.py        # ROS/2 适配器
├── world_model/
│   └── world_model.py        # 空间知识图谱
├── planner/
│   └── planner.py            # 任务规划器
├── adapters/                 # 机器人配置模板
├── tests/
│   └── test_e2e.py           # 端到端测试 (34项)
└── install.sh
##支持的任务
任务	示例	动作数
拿取物体	"拿水杯" "帮我拿遥控器"	6
巡逻	"巡逻"	6
自我介绍	"介绍自己"	2
收拾整理	"收拾桌子"	7
标准动作 (12个)
移动: navigate_to, move_arm, move_base
操作: grasp, release, push
感知: look_at, detect_objects, get_pose
交互: speak, play_gesture
系统: wait, emergency_stop

##对接真实机器人
from bridge.ros2_bridge import ROS2Bridge

bridge = ROS2Bridge(mock_mode=False)  # 使用真实 ROS/2
bridge.execute("grasp", {"object_id": "cup_01"})
演示输出文本
cd ~/clawsjoy_robotics && python3 -c "
from robotics_agent import RoboticsAgentV4
from bridge.ros2_bridge import ROS2Bridge

agent = RoboticsAgentV4(mock_mode=True)
bridge = ROS2Bridge(mock_mode=True)

print('=' * 60)
print('ClawsJoy Robotics - 标准接口演示')
print('=' * 60)

print(bridge.get_checklist())

print('\n' + '=' * 60)
print('任务演示')
print('=' * 60)

for task in ['介绍自己', '拿水杯', '帮我拿遥控器', '巡逻']:
    print(f'\n📋 用户: \"{task}\"')
    result = agent.process(task)
    print(f'   ✅ {result[\"response\"]}')

print('\n' + '=' * 60)
print('动作→ROS/2 映射表')
print('=' * 60)
for action, mapping in bridge.get_topic_mapping().items():
    topic = mapping.get('topic', 'N/A')
    msg = mapping.get('msg_type', 'N/A')
    print(f'  {action:20s} → {topic:30s} ({msg})')

agent.shutdown()
"