from datetime import date
from operator import ge
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from utils.utils import category_normalizer
import re


class BudgetExpected(BaseModel):
    """Model for creating a Category"""

    amount_limit: float = Field(
        description="This is the amount being budgeted",
        ge=0,
    )
    start_date: date = Field(
        description="The date the budget starts",
    )
    end_date: date = Field(
        description="The date the budget ends",
    )
    category_id: str = Field(
        description="This is the category for the budget",
    )


class BudgetUpdateExpected(BaseModel):
    """Model for creating a Category"""

    amount_limit: float = Field(
        default=None,
        description="This is the amount being budgeted",
        ge=0,
    )
    start_date: date = Field(
        default=None,
        description="The date the budget starts",
    )
    end_date: date = Field(
        default=None,
        description="The date the budget ends",
    )
    category_id: str = Field(
        default=None,
        description="This is the category for the budget",
    )
