from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()


class Basemodel:

    __abstract__ = True
    id = Column(String(50), primary_key=True, default=str(uuid4))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def to_dict(self):
        obj = self.__dict__.copy()
        obj.pop("_sa_instance_state", None)
        return obj
