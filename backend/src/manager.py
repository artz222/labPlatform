import typing

from fastapi import WebSocket

from .model.cfg import LabConfig, MainRoundConfig, SubRoundConfig
from .model.message import CMD, ExperimentInfo, Image, Info, Options, SocketMessage


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_json(self, message: typing.Any, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class ExperimentManager:
    def __init__(self, lab_cfg: LabConfig, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.cur_main_round = 0
        self.cur_sub_round = 0
        self.lab_cfg = lab_cfg
        self.main_rounds = self._flatten_main_rounds()
        self._refresh_sub_rounds_list()
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
        return 0

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

        self.sub_rounds = [SubRoundConfig]
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
        生成唯一标识符

        Returns:
            str: 唯一标识符
        """

        return "uuiduuid"

    async def _handle_connect(self, websocket: WebSocket, data: str):
        """
        处理连接

        Args:
            websocket (WebSocket): 当前客户端
        """
        # TODO: 处理设备初始连接逻辑
        await self.connection_manager.send_json(
            SocketMessage(cmd=CMD.CONNECT, data=self._generate_uuid()).model_dump(),
            websocket,
        )

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
                pass
            case CMD.UPDATE_EXPERIMENT_INFO:
                pass

        socketMessage = SocketMessage(
            cmd=CMD.UPDATE_EXPERIMENT_INFO,
            data=ExperimentInfo(
                infos=[
                    Info(hint="实验轮数", value="1/6"),
                    Info(hint="当前回合数", value="3/20"),
                    Info(hint="hint1", value="value"),
                    Info(hint="hint2", value="value"),
                    Info(hint="hint3", value="value"),
                    Info(
                        hint="测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试",
                        value="value",
                    ),
                ],
                image=Image(imageUrl="http://192.168.31.88:8000/images/1.png"),
                options=Options(options=["购买", "购买", "购买不购买"]),
            ).model_dump_json(),
        )
        await self.connection_manager.send_json(socketMessage.model_dump(), websocket)


__all__ = ["ConnectionManager", "ExperimentManager"]
