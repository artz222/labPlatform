from enum import StrEnum
from pydantic import BaseModel


class CMD(StrEnum):
    """客户端交互命令枚举类"""

    UPDATE_EXPERIMENT_INFO = "UPDATE_EXPERIMENT_INFO"
    """更新实验信息"""

    CONNECT = "CONNECT"
    """连接实验"""

    SUBMIT_DESITION = "SUBMIT_DESITION"
    """提交决策"""


class ExperimentStatus(StrEnum):
    """实验状态枚举类"""

    RUNNING = "RUNNING"
    """实验运行中"""

    PENDING = "PENDING"
    """实验等待中"""

    END = "END"
    """实验已结束"""


class SocketMessage(BaseModel):
    cmd: CMD
    data: str


class Info(BaseModel):
    hint: str
    value: str


class Image(BaseModel):
    imageUrl: str


class Options(BaseModel):
    options: list[str]


class ExperimentInfo(BaseModel):
    infos: list[Info]
    images: list[Image]
    options: Options
    expStatus: ExperimentStatus = ExperimentStatus.RUNNING


class DecisionMessage(BaseModel):
    """决策消息"""

    uuid: str
    """设备uuid"""

    decision: str
    """决策"""
