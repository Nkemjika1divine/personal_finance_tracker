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


class BudgetPeriod(Enum):
    monthly = "monthly"
    weekly = "weekly"


class Budget(Basemodel, Base):
    __tablename__ = "budgets"

    user_id = Column(
        String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = Column(
        String(50), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    amount_limit = Column(Float, nullable=False)
    period = Column(String(10), nullable=False)
