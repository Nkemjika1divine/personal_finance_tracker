from datetime import date
from pydantic import BaseModel, EmailStr, Field, validator


class IncomeExpected(BaseModel):
    """Model for creating an Income"""

    amount: float = Field(
        description="This is the amount gotten",
        ge=0,
    )
    timestamp: date = Field(
        description="The date and time of the income came in",
    )
    description: str = Field(
        default=None, description="The description of the income", max_length=199
    )


class IncomeUpdateExpected(BaseModel):
    """Model for creating an Income"""

    amount: float = Field(
        default=None,
        description="This is the amount gotten",
        ge=0,
    )
    timestamp: date = Field(
        default=None,
        description="The date and time of the income came in",
    )
    description: str = Field(
        default=None, description="The description of the income", max_length=199
    )
