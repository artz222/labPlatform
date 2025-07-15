from tokenize import group
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
    name: str
    roles: List[RoleConfig]


class MakerConfig(BaseModel):
    groups: List[str] = None
    roles: List[str] = None


class DecisionConfig(BaseModel):
    makers: List[MakerConfig]
    options: List[str]


class SubRoundConfig(BaseModel):
    repeat: int
    decision: DecisionConfig
    hint: str


class MainRoundConfig(BaseModel):
    repeat: int
    sub_rounds: List[SubRoundConfig]

class AlgorithmConfig(BaseModel):
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
