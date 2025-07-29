import copy
import typing
import uuid

from fastapi import WebSocket

from .algorithm.base_algo import BaseAlgorithm
from .model.cfg import LabConfig, MainRoundConfig, SubRoundConfig
from .model.message import (
    CMD,
    DecisionMessage,
    ExperimentInfo,
    ExperimentStatus,
    Image,
    Info,
    Options,
    SocketMessage,
)


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
        self._exp_pending_msg = SocketMessage(
            cmd=CMD.UPDATE_EXPERIMENT_INFO,
            data=ExperimentInfo(
                infos=[],
                images=[],
                options=Options(options=[]),
                expStatus=ExperimentStatus.PENDING,
            ).model_dump_json(),
        ).model_dump_json()

        self._exp_end_msg = SocketMessage(
            cmd=CMD.UPDATE_EXPERIMENT_INFO,
            data=ExperimentInfo(
                infos=[],
                images=[],
                options=Options(options=[]),
                expStatus=ExperimentStatus.END,
            ).model_dump_json(),
        ).model_dump_json()

        self.connection_manager = connection_manager
        self.cur_main_round = 0
        self.cur_sub_round = 0
        self.lab_cfg = lab_cfg

        self.experiment_devices = {}
        """
        维护本次实验所需要的全部客户端设备信息

        字典结构
        key: 设备uuid
        value: 设备信息
        {
            "uuid": {
                "cur_message": str, # 保存的本设备当前回合的消息
                "role": (str, str), # 设备的角色 (组别, 角色)
                "websocket": WebSocket, # 设备的websocket连接对象
            },
        }
        """

        self.submit_logs = []
        """
        维护所有回合的提交日志

        列表结构
        [
            # 第1回合
            {
                "uuid1": {
                    "decision": str, # 保存的本设备当前回合的决策
                    "role": (str, str), # 设备的角色 (组别, 角色)
                },
                "uuid2": {
                    "decision": str, # 保存的本设备当前回合的决策
                    "role": (str, str), # 设备的角色 (组别, 角色)
                },
            },
            # 第2回合
            {
                "uuid1": {
                    "decision": str, # 保存的本设备当前回合的决策
                    "role": (str, str), # 设备的角色 (组别, 角色)
                },
                "uuid2": {
                    "decision": str, # 保存的本设备当前回合的决策
                    "role": (str, str), # 设备的角色 (组别, 角色)
                },
            },
            ...
        ]
        """

        self.cur_round_participants = set[str]()
        """
        维护当前回合的实验参与人员
            {uuid1, uuid2, ...}
        """

        self.cur_round_submit_devices = {}
        """
        维护当前回合进行了提交的实验设备信息

        字典结构
        key: 设备uuid
        value: 设备信息
        {
            "uuid": {
                "decision": str, # 保存的本设备当前回合的决策
                "role": (str, str), # 设备的角色 (组别, 角色)
            },
        }
        """
        self.main_rounds = self._flatten_main_rounds()
        self.algorithm = algorithm
        self.algorithm.experiment_devices = (
            self.experiment_devices
        )  # 让算法类能访问所有人的组别信息
        self._refresh_sub_rounds_list()
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
                self.cur_sub_round -= 1 # 恢复子回合数，避免溢出
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

        self.algorithm.sub_rounds = self.sub_rounds

    def _init_cur_round_participants(self):
        """
        初始化当前回合的实验参与人员

        """
        self.cur_round_participants.clear()
        round = self.sub_rounds[self.cur_sub_round]
        makers = round.decision.makers
        # makers 为空，所有设备都参与
        if makers is None:
            self.cur_round_participants.update(self.experiment_devices.keys())
            return
        for uuid, value in self.experiment_devices.items():
            for maker in makers:
                if maker.groups is None or value["role"][0] in maker.groups:
                    if maker.roles is None or value["role"][1] in maker.roles:
                        self.cur_round_participants.add(uuid)
        print(f"本回合参与人: {self.cur_round_participants}")

    def _get_cur_participants_num(self) -> int:
        """
        获取当前小回合的实验决策人数

        Returns:
            int: 当前小回合的实验决策人数
        """

        round = self.sub_rounds[self.cur_sub_round]
        makers = round.decision.makers
        num = 0
        for maker in makers:
            num += self._get_group_roles_num(groups=maker.groups, roles=maker.roles)

        return num

    def _get_group_roles_num(
        self, groups: list[str] = None, roles: list[str] = None
    ) -> int:
        """
        获取指定组别角色的实验人数

        Args:
            groups (list[str], optional): 组别列表. Defaults to None.
            roles (list[str], optional): 角色列表. Defaults to None.

        Returns:
            int: 组别角色实验人数
        """
        num = 0
        for group in self.lab_cfg.groups:
            if groups is None or group.name in groups:
                for role in group.roles:
                    if roles is None or role.name in roles:
                        num += role.num
        return num

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

    def _assign_role(self) -> tuple[str, str]:
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
            # 设备重连的时候下发设备当前实验信息
            print(f"设备重连 uuid: {data}")
            self.experiment_devices[data]["websocket"] = websocket
            if "cur_message" in self.experiment_devices[data]:
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

            # 设备第一次连接先下发pending信息
            self.experiment_devices[uuid]["cur_message"] = self._exp_pending_msg
            await self.connection_manager.send_message(self._exp_pending_msg, websocket)

            if self._total_participants_num() == len(self.experiment_devices):
                print("实验人数已足够, 开始实验")

                # 初始化当前回合参与人
                self._init_cur_round_participants()

                # 为每个参与人生成独立的 process_result
                process_result_map = {}
                for uid in self.cur_round_participants:
                    process_result_map[uid] = self.algorithm.process(
                        uuid=uid,
                        submit_logs=self.submit_logs,
                        cur_main_round=self.cur_main_round,
                        cur_sub_round=self.cur_sub_round,
                    )

                await self._start_cur_round(process_result_map)
        print(f"当前连接设备信息: {self.experiment_devices}")

    def _generate_pic_url(self, name: str) -> str:
        """
        生成图片URL

        Args:
            name (str): 图片名称

        Returns:
            str: 图片URL
        """
        return f"http://{self.local_ip}:{self.port}/images/{name}"

    async def _start_cur_round(self, process_result_map: dict[str, dict[str, str]]):
        """
        开始当前回合 下发实验信息

        Args:
            process_result_map (dict[str, dict[str, str]]): 上回合处理结果，每个参与者的结果
        """

        # 下发实验信息
        for uuid in self.cur_round_participants:
            # 获取每个人自己的界面数据
            user_result = process_result_map.get(uuid, {})
            socketMessage = self._generate_exp_info_message(uuid, user_result)
            self.experiment_devices[uuid][
                "cur_message"
            ] = socketMessage.model_dump_json()
            await self.connection_manager.send_message(
                socketMessage.model_dump_json(),
                self.experiment_devices[uuid]["websocket"],
            )

    def _generate_exp_info_message(
        self, uuid, process_result: dict[str, str]
    ) -> SocketMessage:
        """
        生成实验信息消息

        Args:
            process_result (dict[str, str]): 上回合处理结果

        Returns:
            SocketMessage: 实验信息消息
        """

        data = ExperimentInfo(
            infos=[
                Info(
                    hint="实验轮数",
                    value=f"{self.cur_main_round+1}/{len(self.main_rounds)}",
                ),
                Info(
                    hint="当前回合数",
                    value=f"{self.cur_sub_round+1}/{len(self.sub_rounds)}",
                ),
                Info(
                    hint="你的分组",
                    value=self.experiment_devices[uuid]["role"][0],
                ),
                Info(
                    hint="你的角色",
                    value=self.experiment_devices[uuid]["role"][1],
                ),
            ],
            images=[
                Image(imageUrl=self._generate_pic_url(name))
                for name in self.lab_cfg.hint_pics
            ],
            options=Options(
                options=self.sub_rounds[self.cur_sub_round].decision.options
            ),
        )
        if process_result.items():
            data.infos.extend(
                [Info(hint=key, value=value) for key, value in process_result.items()]
            )
        socketMessage = SocketMessage(
            cmd=CMD.UPDATE_EXPERIMENT_INFO,
            data=data.model_dump_json(),
        )

        return socketMessage

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
                await self._handle_submit_decision(websocket, message.data)
            case CMD.UPDATE_EXPERIMENT_INFO:
                pass

    async def _handle_submit_decision(self, websocket: WebSocket, data: str):
        """
        处理实验决策提交
        """

        # 解析消息
        msg = DecisionMessage.model_validate_json(data)

        # 下发消息：请等待其他实验参与者提交与后台处理
        self.experiment_devices[msg.uuid]["cur_message"] = self._exp_pending_msg
        await self.connection_manager.send_message(self._exp_pending_msg, websocket)

        # 记录当前实验设备提交信息
        self.cur_round_submit_devices[msg.uuid] = {
            "role": self.experiment_devices[msg.uuid]["role"],
            "decision": msg.decision,
        }

        print(f"当前回合提交信息更新: {self.cur_round_submit_devices}")

        # 本回合参与对象全部提交之后 调用算法进行处理 并推进下一回合实验展开
        if len(self.cur_round_participants) == len(self.cur_round_submit_devices):
            # 先保存本回合提交日志
            self.submit_logs.append(copy.deepcopy(self.cur_round_submit_devices))

            # 针对所有下一轮参与者分别计算界面数据
            process_result_map = {}

            # 回收当前回合提交设备信息
            self.cur_round_submit_devices.clear()
            # 切换到下一回合
            have_next_round = self._next_round()
            # 初始化当前回合参与人员
            self._init_cur_round_participants()
            
            if have_next_round > 0:
                for uid in self.cur_round_participants:
                    process_result_map[uid] = self.algorithm.process(
                        uuid=uid,
                        submit_logs=self.submit_logs,
                        cur_main_round=self.cur_main_round,
                        cur_sub_round=self.cur_sub_round,
                    )
                await self._start_cur_round(process_result_map)
            else:
                print("===================最后一回合数据处理====================")
                for uid in self.cur_round_participants:
                    process_result_map[uid] = self.algorithm.process(
                        uuid=uid,
                        submit_logs=self.submit_logs,
                        cur_main_round=self.cur_main_round,
                        cur_sub_round=self.cur_sub_round,
                    )
                print("===================实验结束====================")
                for value in self.experiment_devices.values():
                    value["cur_message"] = self._exp_end_msg
                await self.connection_manager.broadcast(self._exp_end_msg)


__all__ = ["ConnectionManager", "ExperimentManager"]
