"""配置加载器"""
import yaml
import os

_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

def load_yaml(filename: str) -> dict:
    """加载 YAML 配置文件"""
    path = os.path.join(_CONFIG_DIR, filename)
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_task_templates() -> dict:
    return load_yaml('task_templates.yaml').get('templates', {})

def get_object_aliases() -> dict:
    return load_yaml('object_aliases.yaml').get('aliases', {})

def get_robot_config() -> dict:
    return load_yaml('robot_config.yaml').get('robot', {})
