from enum import Enum
from models.basemodel import Basemodel, Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Float,
)
from datetime import datetime


class Notification(Basemodel, Base):
    __tablename__ = "notifications"

    user_id = Column(
        String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    notification = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False)
