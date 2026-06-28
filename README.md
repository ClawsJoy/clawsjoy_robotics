# ClawsJoy Robotics

A standard interface from LLM to ROS/2 robot actions.
Any LLM outputs an action. Any robot implements these topics.

## Architecture

User: "拿水杯" -> ClawsJoy Main (cortex) -> intent -> action -> Robotics Agent -> Robot execution

Robotics Agent: planner (task->actions) + world_model (spatial graph) + bridge (ROS/2 or Mock)

## Quick Start

./install.sh
python3 tests/test_e2e.py
python3 robotics_agent.py

## Demo
from robotics_agent import RoboticsAgentV4
agent = RoboticsAgentV4(mock_mode=True)
print(agent.process('拿水杯')['response'])
Output: Task completed in 6 steps

Full demo: DEMO_OUTPUT.txt

## Tasks

- Fetch: "拿水杯" (6 steps)
- Patrol: "巡逻" (6 steps)
- Introduce: "介绍自己" (2 steps)
- Clean up: "收拾桌子" (7 steps)

## 12 Motion Primitives

Move: navigate_to, move_arm, move_base -> /base/cmd_vel, /arm/joint_trajectory
Manipulate: grasp, release, push -> /gripper/command
Perceive: look_at, detect_objects, get_pose -> /perception/objects
Interact: speak, play_gesture -> /speech/tts
System: wait, emergency_stop -> /safety/estop

## Integration Checklist

1. Arm: /arm/joint_trajectory (pub) + /arm/joint_states (sub)
2. Gripper: /gripper/command (sub, Float32, 0=close 1=open)
3. Base: /base/cmd_vel (pub) + /base/odom (sub)
4. Camera: /camera/rgb (sub) + /camera/depth (sub)
5. Perception: /perception/objects (sub)
6. Speech: /speech/tts (pub)
7. Safety: /safety/estop (pub)

Set mock_mode=False and run.

## Customize

Edit config/robot_config.yaml, config/object_aliases.yaml, config/task_templates.yaml
No code changes needed.

## Docs

- docs/QUICKSTART.md
- docs/API.md
- docs/ERROR_CODES.md
- docs/INTEGRATION_UR5.md

## License

MIT
