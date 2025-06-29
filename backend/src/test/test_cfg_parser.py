import unittest
import yaml
import pprint
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))  # 添加src目录到Python路径
from cfg_parser import load_corps_fight_config

class TestCfgParser(unittest.TestCase):
    def setUp(self):
        # 获取测试配置文件路径
        self.valid_config_path = Path(__file__).parent.parent / 'cfg' / 'corpsFight.yml'
        # 创建临时无效YAML文件
        self.invalid_config_path = Path(__file__).parent / 'invalid_config.yml'
        with open(self.invalid_config_path, 'w', encoding='utf-8') as f:
            f.write('invalid: [yaml: {unclosed')

    def tearDown(self):
        # 清理临时文件
        if self.invalid_config_path.exists():
            self.invalid_config_path.unlink()

    def test_load_valid_config(self):
        """测试加载有效的配置文件"""
        config = load_corps_fight_config(str(self.valid_config_path))

        # 验证基本结构
        self.assertIsNotNone(config)
        self.assertIsInstance(config, type(config))
        self.assertIsInstance(config.groups, list)
        self.assertIsInstance(config.main_rounds, list)

        # 验证groups配置
        if config.groups:
            group = config.groups[0]
            self.assertIsNotNone(group.name)
            self.assertIsInstance(group.roles, list)
            if group.roles:
                role = group.roles[0]
                self.assertIsNotNone(role.name)
                self.assertIsInstance(role.num, int)
                self.assertGreater(role.num, 0)

        # 验证main_rounds配置
        if config.main_rounds:
            main_round = config.main_rounds[0]
            self.assertIsInstance(main_round.repeat, int)
            self.assertGreaterEqual(main_round.repeat, 1)
            self.assertIsInstance(main_round.sub_rounds, list)

            if main_round.sub_rounds:
                sub_round = main_round.sub_rounds[0]
                self.assertIsInstance(sub_round.repeat, int)
                self.assertGreaterEqual(sub_round.repeat, 1)
                self.assertIsNotNone(sub_round.decision)
                self.assertIsInstance(sub_round.decision.maker, str)
                self.assertIsInstance(sub_round.decision.options, list)
                self.assertIsInstance(sub_round.decision.prompt, str)

    def test_load_nonexistent_file(self):
        """测试加载不存在的配置文件"""
        with self.assertRaises(FileNotFoundError):
            load_corps_fight_config('nonexistent_config.yml')

    def test_load_invalid_yaml(self):
        """测试加载无效YAML格式的配置文件"""
        with self.assertRaises(yaml.YAMLError):
            load_corps_fight_config(str(self.invalid_config_path))

if __name__ == '__main__':
    # 解析并打印配置
    try:
        config = load_corps_fight_config()
        print("Corps Fight Configuration:")
        pprint.pprint(config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
    # 运行单元测试
    unittest.main()