from utils.utils import create_notification_key, model_to_dict
from models.notification import Notification
from storage.db import SessionLocal
from storage.redis import redis_cache
from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: str, websocket: WebSocket):
        """"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].close()
            del self.active_connections[user_id]

    async def send_to_user(self, user_id: str, message: str):
        """"""
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)


manager = ConnectionManager()


async def create_notifications(user_id: str, message: str):
    """This creates a notification"""
    db = SessionLocal()
    notification = Notification(message=message, user_id=user_id)
    db.add(notification)
    db.commit()
    notification = model_to_dict(notification)
    await redis_cache.set(
        key=create_notification_key(notification["id"]), value=notification
    )
    return notification
