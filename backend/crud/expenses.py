from ast import mod
from datetime import date
from models.expense import Expense
from models.category import Category
from sqlalchemy.orm import Session
from storage.db import SessionLocal
from storage.redis import RedisCache, redis_cache
from models.user import User
from utils.utils import (
    create_expense_key,
    model_to_dict,
    users_to_dict,
)

indexes = {
    "expenses": "idx:Expense",
}


async def create_expense(
    user_id: str, category_id: str, amount: float, description: str, timestamp: date
):
    """This creates an expense"""
    db = SessionLocal()
    try:
        if category_id:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                return -1
        expense = Expense(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            description=description,
            timestamp=timestamp,
        )
        db.add(expense)
        db.commit()
        expense = model_to_dict(expense)
        db.close()
        await redis_cache.set(
            key=create_expense_key(expense_id=expense["id"]),
            value=expense,
            indexes=[indexes["expense"]],
        )
        return expense
    except Exception as e:
        raise ValueError(f"Couldn't save expense: {e}")


async def soft_delete_an_expense(expense_id: str):
    """This soft_deletes an expense"""
    db = SessionLocal()
    try:
        expense = (
            db.query(Expense)
            .filter(Expense.id == expense_id, Expense.is_deleted == False)
            .first()
        )
        if not expense:
            return 0
        expense.is_deleted = True
        await redis_cache.delete(
            create_expense_key(expense_id=expense.id), index=indexes["expenses"]
        )
        db.commit()
        db.close()
        return 1
    except Exception as e:
        raise ValueError(f"Couldn't Delete expense: {e}")


async def get_all_expenses(page: int, limit: int):
    """This returns all the expenses in the db"""
    try:
        db = SessionLocal()
        skip = (page - 1) * limit
        expenses = (
            db.query(Expense)
            .filter(Expense.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not expenses:
            return None
        return users_to_dict(expenses)
    except Exception as e:
        raise ValueError(f"Couldn't get expenses: {e}")


async def get_a_users_expenses(user_id: str, page: int, limit: int):
    """This returns all the expenses of a user"""
    try:
        db = SessionLocal()
        skip = (page - 1) * limit
        expenses = (
            db.query(Expense)
            .filter(Expense.user_id == user_id, Expense.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not expenses:
            return None
        return users_to_dict(expenses)
    except Exception as e:
        raise ValueError(f"Couldn't get expenses: {e}")


async def get_a_expense(expense_id: str):
    """This returns a expense"""
    try:
        expense = await redis_cache.get(create_expense_key(expense_id))
        if expense:
            return expense
        db = SessionLocal()
        expense = (
            db.query(Expense)
            .filter(Expense.id == expense_id, Expense.is_deleted == False)
            .first()
        )
        if not expense:
            return None
        return model_to_dict(expense)
    except Exception as e:
        raise ValueError(f"Couldn't get expense: {e}")


async def edit_an_expense(
    expense_id: str,
    amount: float = None,
    timestamp: date = None,
    description: str = None,
    category_id: str = None,
):
    """This edits a expense"""
    db = SessionLocal()
    try:
        if category_id:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                return -1
        expense = (
            db.query(Expense)
            .filter(Expense.id == expense_id, Expense.is_deleted == False)
            .first()
        )
        if not expense:
            return 0
        if amount:
            expense.amount = amount
        if timestamp:
            expense.timestamp = timestamp
        if description:
            expense.timestamp = description
        db.commit()
        db.refresh(expense)
        expense = model_to_dict(expense)
        db.close()
        await redis_cache.set(
            key=create_expense_key(expense_id=expense["id"]),
            value=expense,
            indexes=[indexes["expenses"]],
        )
        return expense
    except Exception as e:
        raise ValueError(f"Couldn't edit expense: {e}")
