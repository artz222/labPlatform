import json
import socket
import typing
import uuid

from fastapi import WebSocket

from .algorithm.base_algo import BaseAlgorithm
from .model.cfg import LabConfig, MainRoundConfig, SubRoundConfig
from .model.message import CMD, ExperimentInfo, Image, Info, Options, SocketMessage


class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        if websocket in self.active_connections:
            await websocket.send_text(message)

    async def send_json(self, message: typing.Any, websocket: WebSocket):
        if websocket in self.active_connections:
            await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class ExperimentManager:
    def __init__(
        self,
        lab_cfg: LabConfig,
        connection_manager: ConnectionManager,
        algorithm: BaseAlgorithm,
        local_ip: str,
        port: int,
    ):
        self.connection_manager = connection_manager
        self.cur_main_round = 0
        self.cur_sub_round = 0
        self.lab_cfg = lab_cfg
        self.experiment_devices = {}
        self.main_rounds = self._flatten_main_rounds()
        self._refresh_sub_rounds_list()
        self.algorithm = algorithm
        self.local_ip = local_ip
        self.port = port
        print(f"总实验人数: {self._total_participants_num()}")

    def _next_round(self) -> int:
        """
        切换到下一个回合

        Returns:
            int: 切换状态 0 成功，-1 已经是最后一个回合了
        """

        self.cur_sub_round += 1
        if self.cur_sub_round >= len(self.sub_rounds):
            if self.cur_main_round + 1 >= len(self.main_rounds):
                return -1
            self.cur_sub_round = 0
            self.cur_main_round += 1
            self._refresh_sub_rounds_list()
        return 1

    def _total_participants_num(self) -> int:
        """
        获取总实验人数

        Returns:
            int: 总实验人数
        """

        size = 0
        for group in self.lab_cfg.groups:
            for role in group.roles:
                size += role.num
        return size

    def _flatten_main_rounds(self) -> list[MainRoundConfig]:
        """
        展平主回合列表

        Returns:
            list[MainRoundConfig]: 展平后的主回合列表
        """

        main_rounds = []
        for main_round in self.lab_cfg.main_rounds:
            for _ in range(main_round.repeat):
                main_rounds.append(main_round)
        return main_rounds

    def _refresh_sub_rounds_list(self):
        """
        刷新当前大回合的小回合列表
        """

        self.sub_rounds = list[SubRoundConfig]()
        for sub_round in self.main_rounds[self.cur_main_round].sub_rounds:
            for _ in range(sub_round.repeat):
                self.sub_rounds.append(sub_round)

    def _get_cur_participants_num(self) -> int:
        """
        获取当前小回合的实验决策人数

        Returns:
            int: 当前小回合的实验决策人数
        """

        num = 0
        for sub_round in self.sub_rounds:
            num += sub_round.decision

        return 0

    def _generate_uuid(self) -> str:
        """
        生成唯一UUID标识符

        Returns:
            str: 符合RFC4122标准的UUID4字符串
        """
        return str(uuid.uuid4())

    def _is_reconnect(self, uuid: str) -> bool:
        """
        判断是否是重连

        Args:
            uuid (str): 连接设备传入的uuid

        Returns:
            bool: True 是重连，False 不是重连
        """

        return uuid in self.experiment_devices

    def _assign_role(self) -> (str, str):
        """
        分配角色（顺序分配）

        Returns:
            (str, str): 角色分组, 角色描述
        """

        cur_devices_num = len(self.experiment_devices)
        num = 0
        for group in self.lab_cfg.groups:
            for role in group.roles:
                if num + role.num > cur_devices_num:
                    return (group.name, role.name)
                num += role.num
        return ()

    async def _handle_connect(self, websocket: WebSocket, data: str):
        """
        处理连接

        Args:
            websocket (WebSocket): 当前客户端
            data (str): 连接数据
        """

        if self._is_reconnect(data):
            # TODO: 设备重连的时候下发设备当前实验信息
            print(f"设备重连 uuid: {data}")
            self.experiment_devices[data]["websocket"] = websocket
            await self.connection_manager.send_message(
                self.experiment_devices[data]["cur_message"],
                websocket,
            )

            return
        else:
            role = self._assign_role()
            if role == ():
                print(
                    f"实验人数已足够, 当前实验所需人数: {self._total_participants_num()}, 当前连接人数: {len(self.experiment_devices)}"
                )
                return
            uuid = self._generate_uuid()
            print(f"新设备连接 重新生成uuid: {uuid}")
            self.experiment_devices[uuid] = {
                "websocket": websocket,
                "role": role,
            }

            await self.connection_manager.send_json(
                SocketMessage(cmd=CMD.CONNECT, data=uuid).model_dump(),
                websocket,
            )
            if self._total_participants_num() == len(self.experiment_devices):
                print("实验人数已足够, 开始实验")
                await self._start_cur_round()
        print(self.experiment_devices)

    def _generate_pic_url(self, name: str) -> str:
        """
        生成图片URL

        Args:
            name (str): 图片名称

        Returns:
            str: 图片URL
        """
        return f"http://{self.local_ip}:{self.port}/images/{name}"

    async def _start_cur_round(self):
        """
        开始当前回合
        """

        socketMessage = SocketMessage(
            cmd=CMD.UPDATE_EXPERIMENT_INFO,
            data=ExperimentInfo(
                infos=[
                    Info(
                        hint="实验轮数",
                        value=f"{self.cur_main_round+1}/{len(self.main_rounds)}",
                    ),
                    Info(
                        hint="当前回合数",
                        value=f"{self.cur_sub_round+1}/{len(self.sub_rounds)}",
                    ),
                ],
                images=[
                    Image(imageUrl=self._generate_pic_url(name))
                    for name in self.lab_cfg.hint_pics
                ],
                options=Options(
                    options=self.sub_rounds[self.cur_sub_round].decision.options
                ),
            ).model_dump_json(),
        )
        for device in self.experiment_devices.values():
            device["cur_message"] = socketMessage.model_dump_json()
        await self.connection_manager.broadcast(socketMessage.model_dump_json())

    async def parse_message(self, message: SocketMessage, websocket: WebSocket):
        """
        解析消息

        Args:
            message (SocketMessage): 消息
            websocket (WebSocket): 当前客户端
        """

        print(f"收到消息: {message}")
        match message.cmd:
            case CMD.CONNECT:
                await self._handle_connect(websocket, message.data)
            case CMD.SUBMIT_DESITION:
                # TODO: 处理实验决策提交逻辑
                self.algorithm.process()
                if self._next_round() > 0:
                    await self._start_cur_round()
                else:
                    print("===================实验结束====================")
                    await self.connection_manager.broadcast(
                        SocketMessage(
                            cmd=CMD.UPDATE_EXPERIMENT_INFO,
                            data=ExperimentInfo(
                                infos=[],
                                images=[],
                                options=Options(options=[]),
                                end=True,
                            ).model_dump_json(),
                        ).model_dump_json()
                    )
            case CMD.UPDATE_EXPERIMENT_INFO:
                pass


__all__ = ["ConnectionManager", "ExperimentManager"]
