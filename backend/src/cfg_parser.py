from dataclasses import dataclass
from typing import List, Dict, Any
import yaml
from pathlib import Path

@dataclass
class RoleConfig:
    name: str
    num: int

@dataclass
class GroupConfig:
    name: str
    roles: List[RoleConfig]

@dataclass
class DecisionConfig:
    maker: List[str]
    options: List[str]

@dataclass
class SubRoundConfig:
    repeat: int
    decision: DecisionConfig
    hint: str

@dataclass
class MainRoundConfig:
    repeat: int
    sub_rounds: List[SubRoundConfig]

@dataclass
class LabConfig:
    groups: List[GroupConfig]
    main_rounds: List[MainRoundConfig]


def load_corps_fight_config(config_path: str = None) -> LabConfig:
    """加载并解析军团战斗配置文件
    
    Args:
        config_path: 配置文件路径，默认为项目根目录下的cfg/corpsFight.yml
    
    Returns:
        解析后的LabConfig对象
    
    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML解析错误
    """
    if not config_path:
        # 默认配置路径：项目根目录下的cfg/corpsFight.yml
        config_path = Path(__file__).parent / 'cfg' / 'corpsFight.yml'
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    return LabConfig(**config_data)


__all__ = ['LabConfig', 'load_corps_fight_config']