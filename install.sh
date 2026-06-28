#!/bin/bash
# ClawsJoy Robotics - 一键安装脚本
set -e

echo "========================================"
echo " ClawsJoy Robotics 安装"
echo "========================================"

# 检测系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ 无法检测操作系统"
    exit 1
fi

echo "系统: $OS"

# Python 依赖
echo ""
echo "--- Python 依赖 ---"
pip install pyyaml requests numpy 2>/dev/null || pip3 install pyyaml requests numpy
echo "✅ Python 依赖"

# ROS/2 检测
echo ""
echo "--- ROS/2 检测 ---"
if python3 -c "import rclpy" 2>/dev/null; then
    echo "✅ ROS/2 已安装"
    ROS2_MODE="real"
else
    echo "⚠️  ROS/2 未安装，使用模拟模式"
    echo "   安装 ROS/2: https://docs.ros.org/en/humble/Installation.html"
    ROS2_MODE="mock"
fi

# 主版检测
echo ""
echo "--- ClawsJoy 主版检测 ---"
MAIN_PATH="$HOME/clawsjoy_v5"
if [ -d "$MAIN_PATH" ]; then
    echo "✅ 找到主版: $MAIN_PATH"
else
    echo "⚠️  未找到主版，请先安装 ClawsJoy v6.0"
    echo "   git clone https://github.com/your/clawsjoy_v5.git ~/clawsjoy_v5"
fi

# 配置文件
echo ""
echo "--- 配置文件 ---"
if [ ! -f adapters/robot_config.yaml ]; then
    cp adapters/standard_arm.yaml adapters/robot_config.yaml 2>/dev/null || true
    echo "✅ 已创建默认配置"
fi

echo ""
echo "========================================"
echo " 安装完成"
echo ""
echo " 运行测试:"
echo "   cd ~/clawsjoy_robotics && python3 tests/test_e2e.py"
echo ""
echo " 启动模拟模式:"
echo "   cd ~/clawsjoy_robotics && python3 robotics_agent.py"
echo ""
echo " 模式: $ROS2_MODE"
echo "========================================"
