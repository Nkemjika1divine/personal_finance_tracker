from models.notification import Notification
from storage.db import SessionLocal
from utils.utils import users_to_dict


async def get_a_users_notifications(user_id: str, page: int, limit: int):
    """This gets all the noitifications of a usser"""
    try:
        db = SessionLocal()
        skip = (page - 1) * limit
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not notifications:
            return None
        return users_to_dict(notifications)
    except Exception as e:
        raise ValueError(f"Couldn't get notifications: {e}")
