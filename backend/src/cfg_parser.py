from pathlib import Path
import yaml
from .model.cfg import LabConfig, AppConfig
import pprint


def load_lab_config(config_path: str) -> LabConfig:
    """加载并解析实验配置文件

    Args:
        config_path: 配置文件路径，不可为空

    Returns:
        解析后的LabConfig对象

    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML解析错误
    """

    cfg_path = Path(config_path)

    if not cfg_path.exists():
        raise FileNotFoundError(f"实验配置文件不存在: {cfg_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        lab_config = yaml.safe_load(f)
        print("成功加载实验配置:")
        pprint.pprint(lab_config)
    return LabConfig(**lab_config)


def load_app_config() -> AppConfig:
    """加载并解析应用配置文件

    Returns:
        解析后的AppConfig对象

    Raises:
        FileNotFoundError: 应用配置文件不存在
        yaml.YAMLError: YAML解析错误
    """

    config_path = Path(__file__).parent / "cfg" / "app_cfg.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"应用配置文件不存在: {config_path}")

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
        print("成功加载应用配置:")
        pprint.pprint(config_data)

    return AppConfig(**config_data)


__all__ = ["load_app_config", "load_lab_config"]
