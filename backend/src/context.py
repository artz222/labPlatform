import socket

from .cfg_parser import load_app_config, load_lab_config
from .manager import ConnectionManager, ExperimentManager


class Context:
    def __init__(self):
        self.connection_manager = ConnectionManager()

    def _initConfig(self):
        # 加载配置
        self.app_config = load_app_config()
        self.lab_config = load_lab_config(self.app_config.lab_cfg_path)

    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 连接到外部地址以确定使用的网络接口
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def init(self):
        self._initConfig()
        self.experiment_manager = ExperimentManager(
            self.lab_config, self.connection_manager
        )

        # 获取并打印IP地址
        port = 8000  # 确保与启动命令中的端口一致
        print(f"后端服务已启动，局域网访问地址: http://{self._get_local_ip()}:{port}")
        print(f"请在客户端使用此IP和端口连接服务")
