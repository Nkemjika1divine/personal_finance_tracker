from models.basemodel import Basemodel, Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey


class Category(Basemodel, Base):
    __tablename__ = "categories"
    name = Column(String(50), nullable=False)
    user_id = Column(
        String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
