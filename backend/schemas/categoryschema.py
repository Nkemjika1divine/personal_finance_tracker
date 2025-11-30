from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from utils.utils import category_normalizer
import re


class CategoryExpected(BaseModel):
    """Model for creating a Category"""

    name: str = Field(
        description="This is the name of the user being created",
        max_length=30,
        min_length=5,
        title="User's Name",
        pattern=r"^[A-Za-z]+$",
    )

    # validate name
    @validator("name", pre=True)
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return category_normalizer(value)
        return value
