from fastapi import FastAPI, WebSocketDisconnect, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
import socket
from pydantic_core import to_json
import yaml
from pathlib import Path
from dataclasses import dataclass, asdict
from .connection_manager import connection_manager
from .model.message import SocketMessage, ExperimentInfo, Info, Image, Options


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动之前的工作
    initConfig()
    yield
    # 结束后的工作
    print("应用关闭")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    with open("./test/websocket_test.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(html_content)


@app.get("/images/{image_name}")
async def get_image(image_name: str):
    # 构建图片文件的绝对路径
    assets_dir = Path(__file__).parent.parent / "assets"
    image_path = assets_dir / image_name

    # 检查文件是否存在
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="图片文件不存在")

    # 检查是否是文件
    if not image_path.is_file():
        raise HTTPException(status_code=400, detail="路径不是有效的文件")

    # 确定媒体类型
    ext = image_name.lower().split(".")[-1]
    media_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "svg": "image/svg+xml",
    }

    media_type = media_types.get(ext)
    if not media_type:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式: {ext}")

    return FileResponse(str(image_path), media_type=media_type)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            socketMessage = SocketMessage(
                cmd="UPDATE_EXPERIMENT_INFO",
                data=ExperimentInfo(
                    infos=[
                        Info(hint="实验轮数", value="1/6"),
                        Info(hint="当前回合数", value="2/20"),
                        Info(hint="当前实验", value="实验1"),
                        Info(hint="当前实验", value="实验1"),
                        Info(hint="当前实验", value="实验1"),
                    ],
                    image=Image(imageUrl="http://192.168.31.88:8000/images/1.png"),
                    options=Options(options=["购买", "购买", "购买不购买"]),
                ).model_dump_json(),
            )
            await connection_manager.send_json(socketMessage.model_dump(), websocket)
            # await connection_manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast(f"Client left the chat")


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
    config_path = Path(__file__).parent / "cfg" / "test.yaml"
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
            print("完整配置:\n", config_data)
            return AppConfig(
                database=DatabaseConfig(**config_data["database"]),
                server=ServerConfig(**config_data["server"]),
                features=config_data["features"],
                modules=config_data["modules"],
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


def initConfig():
    # 加载配置
    config = load_config()
    print("成功加载配置:\n", config)

    # 获取并打印IP地址
    ip = get_local_ip()
    port = 8000  # 确保与启动命令中的端口一致
    print(f"后端服务已启动，局域网访问地址: http://{ip}:{port}")
    print(f"请在客户端使用此IP和端口连接服务")
