from typing import List

from pydantic import BaseModel


class AppConfig(BaseModel):
    """
    应用配置
    """

    lab_cfg_path: str


class RoleConfig(BaseModel):
    """
    角色配置
    """

    name: str
    num: int


class GroupConfig(BaseModel):
    """
    组别配置
    """

    name: str
    roles: List[RoleConfig]


class MakerConfig(BaseModel):
    """
    决策人配置
    """

    groups: List[str] = None
    roles: List[str]


class DecisionConfig(BaseModel):
    """
    决策配置
    """

    makers: List[MakerConfig] = None
    options: List[str]


class SubRoundConfig(BaseModel):
    """
    子回合配置
    """

    repeat: int
    decision: DecisionConfig
    hint: str


class MainRoundConfig(BaseModel):
    """
    主回合配置
    """

    repeat: int
    sub_rounds: List[SubRoundConfig]


class AlgorithmConfig(BaseModel):
    """
    算法配置
    """

    module: str
    class_name: str = None


class LabConfig(BaseModel):
    """
    实验配置
    """

    groups: List[GroupConfig]
    main_rounds: List[MainRoundConfig]
    algorithm: AlgorithmConfig
    hint_pics: List[str] = None


__all__ = ["AppConfig", "LabConfig"]
