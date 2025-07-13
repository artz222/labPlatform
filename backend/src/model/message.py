from enum import StrEnum
from pydantic import BaseModel


class CMD(StrEnum):
    """客户端交互命令枚举类"""

    UPDATE_EXPERIMENT_INFO = "UPDATE_EXPERIMENT_INFO"
    CONNECT = "CONNECT"
    SUBMIT_DESITION = "SUBMIT_DESITION"


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
    end: bool = False
