import abc


class BaseAlgorithm:

    @abc.abstractmethod
    def process(self) -> dict[str, str]:
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
