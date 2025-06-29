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
    maker: str
    options: List[str]
    prompt: str

@dataclass
class SubRoundConfig:
    repeat: int
    decision: DecisionConfig

@dataclass
class MainRoundConfig:
    repeat: int
    sub_rounds: List[SubRoundConfig]

@dataclass
class CorpsFightConfig:
    groups: List[GroupConfig]
    main_rounds: List[MainRoundConfig]


def load_corps_fight_config(config_path: str = None) -> CorpsFightConfig:
    """加载并解析军团战斗配置文件
    
    Args:
        config_path: 配置文件路径，默认为项目根目录下的cfg/corpsFight.yml
    
    Returns:
        解析后的CorpsFightConfig对象
    
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

    # 解析角色配置
    roles = []
    for role_data in config_data.get('roles', []):
        roles.append(RoleConfig(
            name=role_data['name'],
            num=role_data['num']
        ))

    # 解析分组配置
    groups = []
    for group_data in config_data.get('groups', []):
        group_roles = []
        for role_data in group_data.get('roles', []):
            group_roles.append(RoleConfig(
                name=role_data['name'],
                num=role_data['num']
            ))
        groups.append(GroupConfig(
            name=group_data['name'],
            roles=group_roles
        ))

    # 解析小回合配置
    main_rounds = []
    for main_round_data in config_data.get('main_rounds', []):
        sub_rounds = []
        for sub_round_data in main_round_data.get('sub_rounds', []):
            decision_data = sub_round_data.get('decision', {})
            decision = DecisionConfig(
                maker=decision_data.get('maker', ''),
                options=decision_data.get('options', []),
                prompt=decision_data.get('prompt', '')
            )
            sub_rounds.append(SubRoundConfig(
                repeat=sub_round_data.get('repeat', 1),
                decision=decision
            ))
        main_rounds.append(MainRoundConfig(
            repeat=main_round_data.get('repeat', 1),
            sub_rounds=sub_rounds
        ))

    return CorpsFightConfig(
        groups=groups,
        main_rounds=main_rounds
    )


__all__ = ['CorpsFightConfig', 'load_corps_fight_config']