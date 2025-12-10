from models.basemodel import Basemodel, Base
from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    Text,
)
from datetime import datetime


class Notification(Basemodel, Base):
    __tablename__ = "notifications"

    user_id = Column(
        String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
