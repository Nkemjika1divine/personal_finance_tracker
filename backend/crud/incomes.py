from ast import mod
from datetime import date
from models.income import Income
from models.category import Category
from sqlalchemy.orm import Session
from storage.db import SessionLocal
from storage.redis import RedisCache, redis_cache
from models.user import User
from utils.utils import (
    create_income_key,
    model_to_dict,
    users_to_dict,
)

indexes = {
    "incomes": "idx:Income",
}


async def create_income(
    user_id: str, amount: float, timestamp: date, description: str = None
):
    """This creates an income"""
    db = SessionLocal()
    try:
        income = Income(
            user_id=user_id,
            amount=amount,
            description=description,
            timestamp=timestamp,
        )
        db.add(income)
        db.commit()
        income = model_to_dict(income)
        db.close()
        await redis_cache.set(
            key=create_income_key(income_id=income["id"]),
            value=income,
            indexes=[indexes["incomes"]],
        )
        return income
    except Exception as e:
        raise ValueError(f"Couldn't save income: {e}")


async def soft_delete_an_income(income_id: str):
    """This soft_deletes an income"""
    db = SessionLocal()
    try:
        income = (
            db.query(Income)
            .filter(Income.id == income_id, Income.is_deleted == False)
            .first()
        )
        if not income:
            return 0
        income.is_deleted = True
        await redis_cache.delete(
            create_income_key(income_id=income.id), index=indexes["incomes"]
        )
        db.commit()
        db.close()
        return 1
    except Exception as e:
        raise ValueError(f"Couldn't Delete income: {e}")


async def get_all_incomes(page: int, limit: int):
    """This returns all the incomes in the db"""
    try:
        db = SessionLocal()
        skip = (page - 1) * limit
        incomes = (
            db.query(Income)
            .filter(Income.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not incomes:
            return None
        return users_to_dict(incomes)
    except Exception as e:
        raise ValueError(f"Couldn't get incomes: {e}")


async def get_a_users_incomes(user_id: str, page: int, limit: int):
    """This returns all the incomes of a user"""
    try:
        db = SessionLocal()
        skip = (page - 1) * limit
        incomes = (
            db.query(Income)
            .filter(Income.user_id == user_id, Income.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not incomes:
            return None
        return users_to_dict(incomes)
    except Exception as e:
        raise ValueError(f"Couldn't get incomes: {e}")


async def get_an_income(income_id: str):
    """This returns a income"""
    try:
        income = await redis_cache.get(create_income_key(income_id))
        if income:
            return income
        db = SessionLocal()
        income = (
            db.query(Income)
            .filter(Income.id == income_id, Income.is_deleted == False)
            .first()
        )
        if not income:
            return None
        return model_to_dict(income)
    except Exception as e:
        raise ValueError(f"Couldn't get income: {e}")


async def edit_an_income(
    income_id: str,
    amount: float = None,
    timestamp: date = None,
    description: str = None,
):
    """This edits a income"""
    db = SessionLocal()
    try:
        income = (
            db.query(Income)
            .filter(Income.id == income_id, Income.is_deleted == False)
            .first()
        )
        if not income:
            return 0
        if amount:
            income.amount = amount
        if timestamp:
            income.timestamp = timestamp
        if description:
            income.timestamp = description
        db.commit()
        db.refresh(income)
        income = model_to_dict(income)
        db.close()
        await redis_cache.set(
            key=create_income_key(income_id=income["id"]),
            value=income,
            indexes=[indexes["incomes"]],
        )
        return income
    except Exception as e:
        raise ValueError(f"Couldn't edit income: {e}")
