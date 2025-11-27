from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey
from models.basemodel import Basemodel, Base
from bcrypt import hashpw, checkpw, gensalt


class User(Basemodel, Base):
    __tablename__ = "users"
    username = Column(String(30), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(9), default="user")
    is_deleted = Column(Boolean, default=False)
    deleted_by = Column(String(30), ForeignKey("users.id", ondelete="CASCADE"))
    image = Column(String(50))

    def is_valid_password(self, password: str) -> bool:
        """Verifies to ensure that password entered is the same in the DB"""
        if not password or type(password) is not str:
            return False
        return checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
