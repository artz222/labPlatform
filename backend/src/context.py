import socket

from cfg_parser import load_algorithm, load_app_config, load_lab_config
from manager import ConnectionManager, ExperimentManager


class Context:
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.port = 8000  # 在这里修改端口号

    def _initConfig(self):
        # 加载配置
        self.app_config = load_app_config()
        self.lab_config = load_lab_config(self.app_config.lab_cfg_path)
        self._algorithm = load_algorithm(self.lab_config.algorithm)

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
        # 获取并打印IP地址

        self.local_ip = self._get_local_ip()
        print(f"后端服务已启动，局域网访问地址: http://{self.local_ip}:{self.port}")
        print(f"请在客户端使用此IP和端口连接服务")

        self.experiment_manager = ExperimentManager(
            self.lab_config,
            self.connection_manager,
            self._algorithm,
            self.local_ip,
            self.port,
        )
