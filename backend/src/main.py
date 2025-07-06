from fastapi import FastAPI, WebSocketDisconnect, WebSocket
from contextlib import asynccontextmanager
import socket
import yaml
from pathlib import Path
from dataclasses import dataclass
from .connection_manager import connection_manager
from fastapi.responses import HTMLResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动之前的工作
    initConfig()
    yield
    # 结束后的工作
    print("应用关闭")


app = FastAPI(lifespan=lifespan)


from fastapi.responses import FileResponse
from fastapi import HTTPException
from pathlib import Path

# 测试websockets连接是否正常
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def root():
    return HTMLResponse(html)


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

testjson = """
{
    "action": "test",
    "params": {
        "test": "test"
    }
}
"""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.send_json(testjson, websocket)
            await connection_manager.broadcast(f"Client says: {data}")
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
