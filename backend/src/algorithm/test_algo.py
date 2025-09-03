from .base_algo import BaseAlgorithm


class TestAlgorithm(BaseAlgorithm):
    """
    测试算法
    请参照该算法返回的格式，返回的格式为：
    {
        "infos": [
            ("#info_group", "历史信息"),
            ("前一个大回合我军得分", "0"),
            ("前一个大回合本参谋得分", "0"),
            ("#info_group", "统计信息"),
            ("我军累计得分", "0"),
        ],
        "images": [
            "3.png",
            "4.png",
        ],
    }
    """

    def process(
        self, uuid, submit_logs, cur_main_round, cur_sub_round, is_last_round
    ) -> dict[str, str]:
        return {
            "infos": [
                ("#info_group", "历史信息"),
                (
                    "前一个大回合我军得分#[解释： 前一个回合我军的得分balabalabalabala]",
                    "10",
                ),
                (
                    "前一个大回合本参谋得分#[解释： 前一个回合本参谋的得分balabalabalabala]",
                    "20",
                ),
                ("#info_group", "统计信息"),
                (
                    "我军累计得分#[解释： 我军累计得分balabalabalabala1测试测试测试测史册士大夫撒当发生的发生撒发生的发生地方啊啥的发生地方]",
                    "01",
                ),
                ("本参谋累计得分#[解释： 本参谋累计得分balabalabalabala2]", "02"),
                ("我军累计得分#[解释： 我军累计得分balabalabalabala3]", "03"),
                ("本参谋累计得分#[解释： 本参谋累计得分balabalabalabala4]", "04"),
                ("我军累计得分#[解释： 我军累计得分balabalabalabala5]", "05"),
                ("本参谋累计得分#[解释： 本参谋累计得分balabalabalabala6]", "06"),
                ("我军累计得分#[解释： 我军累计得分balabalabalabala7]", "07"),
                ("本参谋累计得分#[解释： 本参谋累计得分balabalabalabala8]", "08"),
            ],
            "images": [
                "3.png",
                "4.png",
            ],
        }
