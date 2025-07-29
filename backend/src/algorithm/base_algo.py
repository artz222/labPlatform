import abc


class BaseAlgorithm:
    """
    实验算法基类
    所有实验算法都需要继承自该类
    所有实验算法都需要实现process方法
    experiment_devices和sub_rounds在实验过程中会进行更新，需要在process方法中使用

    Attributes:
        experiment_devices (dict[str, str]): 实验设备信息
        sub_rounds (list[dict[str, str]]): 实验回合信息
    """

    def __init__(self):
        # 实验设备信息
        self.experiment_devices = {}
        # 实验回合信息
        self.sub_rounds = []

    @abc.abstractmethod
    def process(
        self, uuid, submit_logs, cur_main_round, cur_sub_round, is_last_round
    ) -> dict[str, str]:
        """
        处理实验数据

        Returns:
            dict[str, str]: 处理结果
            处理结果格式参考: {
                "hint1": "value1",
                "hint2": "value2",
            }
        """

        print("===================开始进行当前实验回合数据处理====================")
