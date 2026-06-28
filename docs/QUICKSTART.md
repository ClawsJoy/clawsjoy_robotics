# ClawsJoy Robotics 快速开始

## 30 分钟跑通模拟模式

### 环境要求
- Python 3.10+
- 8GB 内存
- Linux / macOS / Windows WSL2

### 安装

```bash
# 1. 克隆
git clone https://github.com/your-org/clawsjoy_robotics.git
cd clawsjoy_robotics

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证
python3 tests/test_e2e.py
# 输出: 34 通过 / 0 失败
##第一条指令
python3 -c "
from robotics_agent import RoboticsAgentV4
agent = RoboticsAgentV4(mock_mode=True)
result = agent.process('拿水杯')
print(result['response'])
"
# 输出: ✅ 完成任务，共执行 6 个动作
##添加你自己的物体
###编辑 config/object_aliases.yaml：
aliases:
  零件: part          # 添加这行
  螺丝: screw         # 添加这行
###编辑 config/robot_config.yaml，在 initial_objects 里加：
initial_objects:
  - {id: "part_a_01", type: "part", position: {x: 1.0, y: 0.5, z: 0.3}}
###再运行：
python3 -c "
from robotics_agent import RoboticsAgentV4
agent = RoboticsAgentV4(mock_mode=True)
print(agent.process('拿零件')['response'])
"
##添加你自己的任务
###编辑 config/task_templates.yaml，添加：
  sort_parts:
    description: "分拣零件"
    keywords: ["分拣", "分类"]
    steps:
      - action: detect_objects
      - action: grasp
        params: {object_id: "{{first_object}}"}
      - action: navigate_to
        params: {target_location: "bin_a"}
      - action: release
##对接真实机器人
1 天对接流程
上午：确认 ROS/2 话题
运行机器人驱动，确认这些话题存在：
ros2 topic list | grep -E "arm|gripper|base|camera|perception|speech|safety"
如果话题名不同，编辑 config/robot_config.yaml 的 ros2_topics 部分。
下午：对接测试
# 1. 设 mock_mode=False
python3 -c "
from robotics_agent import RoboticsAgentV4
agent = RoboticsAgentV4(mock_mode=False)  # 真实模式
print(agent.process('拿水杯')['response'])
"
如果失败：查看 logs/clawsjoy_robotics.log，根据错误码查 docs/ERROR_CODES.md。
下一步
看 bridge/ros2_bridge.py 运行输出 → 完整接口规范
看 docs/API.md → 每个方法的输入输出
看 docs/INTEGRATION.md → UR5 对接示例
