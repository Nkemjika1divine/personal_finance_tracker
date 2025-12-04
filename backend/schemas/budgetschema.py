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
    period: str = Field(
        description="This is the budget period; must be weekly or monthly ",
        max_length=8,
        min_length=5,
    )
    category_id: str = Field(
        description="This is the category for the budget",
    )

    @validator("period")
    def validate_period(cls, value: str):
        # remove any trailing lines
        value = value.strip()
        value = value.lower()
        terms_list = [
            "weekly",
            "monthly",
        ]
        if value not in terms_list:
            raise ValueError(
                "Value must be one of the following: ['monthly', 'weekly']"
            )
        return value


class BudgetUpdateExpected(BaseModel):
    """Model for creating a Category"""

    amount_limit: float = Field(
        default=None,
        description="This is the amount being budgeted",
        ge=0,
    )
    period: str = Field(
        default="",
        description="This is the budget period; must be weekly or monthly ",
        max_length=8,
        min_length=5,
    )
    category_id: str = Field(
        default=None,
        description="This is the category for the budget",
    )

    @validator("period")
    def validate_period(cls, value: str = None):
        # remove any trailing lines
        if value:
            value = value.strip()
            value = value.lower()
            terms_list = [
                "weekly",
                "monthly",
            ]
            if value not in terms_list:
                raise ValueError(
                    "Value must be one of the following: ['monthly', 'weekly']"
                )
            return value
