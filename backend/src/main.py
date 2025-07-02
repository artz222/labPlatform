from fastapi import FastAPI
import socket
import yaml
from pathlib import Path
from dataclasses import dataclass

app = FastAPI()

@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str

@dataclass
class ServerConfig:
    endpoint: str
    timeout: int

@dataclass
class AppConfig:
    database: DatabaseConfig
    server: ServerConfig
    features: dict
    modules: list

def load_config():
    config_path = Path(__file__).parent / 'cfg' / 'test.yaml'
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            print("完整配置:\n", config_data)
            return AppConfig(
                database=DatabaseConfig(**config_data['database']),
                server=ServerConfig(**config_data['server']),
                features=config_data['features'],
                modules=config_data['modules']
            )
    except Exception as e:
        print(f"配置加载错误: {str(e)}")
        raise

def get_local_ip():
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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    # 加载配置
    config = load_config()
    print("成功加载配置:\n", config)
    
    # 获取并打印IP地址
    ip = get_local_ip()
    port = 8000  # 确保与启动命令中的端口一致
    print(f"后端服务已启动，局域网访问地址: http://{ip}:{port}")
    print(f"请在客户端使用此IP和端口连接服务")