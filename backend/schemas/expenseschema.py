from datetime import date
from operator import ge
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from utils.utils import category_normalizer
import re


class ExpenseExpected(BaseModel):
    """Model for creating a Category"""

    amount: float = Field(
        description="This is the amount being expensed",
        ge=0,
    )
    timestamp: date = Field(
        default=None,
        description="The date and time of the expense made",
    )
    category_id: str = Field(
        description="This is the category for the budget",
    )
    description: str = Field(
        default=None, description="The description of the expense made", max_length=199
    )


class ExpenseUpdateExpected(BaseModel):
    """Model for updating a Category"""

    amount: float = Field(
        default=None,
        description="This is the amount being expensed",
        ge=0,
    )
    timestamp: date = Field(
        default=None,
        description="The date and time of the expense made",
    )
    category_id: str = Field(
        default=None,
        description="This is the category for the budget",
    )
    description: str = Field(
        default=None, description="The description of the expense made", max_length=199
    )
