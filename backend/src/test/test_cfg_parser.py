import pprint
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))  # 添加src目录到Python路径
from cfg_parser import load_corps_fight_config

if __name__ == '__main__':
    # 解析并打印配置
    try:
        config = load_corps_fight_config()
        print("Corps Fight Configuration:")
        pprint.pprint(config)
    except Exception as e:
        print(f"Error loading configuration: {e}")