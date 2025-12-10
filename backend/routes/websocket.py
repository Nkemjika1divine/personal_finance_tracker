from fastapi import APIRouter, WebSocket, Depends, Request
from utils.websocket import ConnectionManager


websocket_router = APIRouter()
manager = ConnectionManager()


@websocket_router.websocket("/ws")
async def websocket_ep(websocket: WebSocket, request: Request):
    """"""
    await manager.connect(request.state.user["id"], websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        await manager.disconnect(request.state.user["id"], websocket)
