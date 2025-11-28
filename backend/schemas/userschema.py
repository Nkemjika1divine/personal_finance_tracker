from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re


class UserExpected(BaseModel):
    """Model for creating a User account"""

    username: str = Field(
        description="This is the name of the user being created",
        max_length=30,
        min_length=5,
        title="User's Name",
        pattern=r"^[A-Za-z]+$",
    )
    email: EmailStr = Field(
        description="A valid email address. Must be unique values",
        min_length=5,
        max_length=100,
    )
    password: str = Field(
        min_length=8,
        max_length=20,
        description="Must contain alphanumeric characters, and optional speccial characters, and must be 8 to 20 characters long",
    )

    # make email lowercase
    @validator("email", pre=True)
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    # regex function for validating password
    @validator("password", pre=True)
    def validate_password(cls, value: str):
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must contain atleast one letter or one number")
        if not re.fullmatch(r"[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':\",.<>?/|`~]+", value):
            raise ValueError("Password contains invalid characters")
        return value


class UserResponse(BaseModel):
    id: str
    email: EmailStr

    class Config:
        from_attributes = True  # lets FastAPI convert SQLAlchemy -> Pydantic


class UserUpdate(BaseModel):
    """Model for updating the User Model"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
