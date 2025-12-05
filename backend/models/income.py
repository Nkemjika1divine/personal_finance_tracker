from enum import Enum
from models.basemodel import Basemodel, Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    func,
    ForeignKey,
    Float,
)
from datetime import datetime


class Income(Basemodel, Base):
    __tablename__ = "incomes"

    user_id = Column(
        String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    timestamp = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)
