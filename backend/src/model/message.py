from pydantic import BaseModel


class SocketMessage(BaseModel):
    cmd: str
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
    image: Image
    options: Options
