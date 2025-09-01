from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import ValidationError

from cfg_parser import *
from context import Context
from model.cfg import *
from model.message import SocketMessage

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


context = Context()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动之前的工作
    try:
        context.init()
    except Exception as e:
        print(f"配置加载错误: {str(e)}")
        raise
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
async def get_image(image_name: str, t: str = None):
    # 构建图片文件的绝对路径
    logger.info(f"Image name: {image_name}")
    assets_dir = (
        Path(__file__).parent.parent / "assets" / context.exp_config.hint_pics_path
    )
    image_path = assets_dir / image_name
    logger.info(f"Image path: {image_path}")

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

    return FileResponse(
        str(image_path),
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await context.connection_manager.connect(websocket)
    try:
        while True:
            try:
                json_data = await websocket.receive_text()
                message = SocketMessage.model_validate_json(json_data)
                await context.experiment_manager.parse_message(message, websocket)
            except ValidationError as e:
                print(f"消息格式错误: {str(e)}")
                continue
    except WebSocketDisconnect:
        context.connection_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=context.port,
        reload=True,
        access_log=True,
        log_level="info",
    )
