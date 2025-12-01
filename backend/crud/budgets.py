from ast import mod
from models.budget import Budget
from models.category import Category
from sqlalchemy.orm import Session
from storage.db import SessionLocal
from storage.redis import redis_cache
from utils.utils import (
    create_budget_key,
    create_category_key,
    create_user_key,
    model_to_dict,
    users_to_dict,
    hash_password,
)

indexes = {
    "budgets": "idx:Budget",
}


async def add_a_budget(amount: float, period: str, user_id: str, category_id: str):
    """This adds a budget to the DB"""
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        budget = Budget(
            amount=amount, period=period, user_id=user_id, category_id=category_id
        )
        db.add(budget)
        db.commit()
        budget = model_to_dict(budget)
        db.close()
        await redis_cache.set(
            key=create_budget_key(budget_id=budget["id"]),
            value=budget,
            indexes=[indexes["budgets"]],
        )
        return budget
    except Exception as e:
        raise ValueError(f"Couldn't save budget: {e}")


async def soft_delete_a_budget(budget_id: str):
    """This soft_deletes a budget"""
    db = SessionLocal()
    try:
        budget = (
            db.query(Budget)
            .filter(Budget.id == budget_id, Budget.is_deleted == False)
            .first()
        )
        if not budget:
            return 0
        budget.is_deleted = True
        await redis_cache.delete(
            create_budget_key(budget_id=budget.id), index=indexes["budgets"]
        )
        db.commit()
        db.close()
        return 1
    except Exception as e:
        raise ValueError(f"Couldn't Delete budget: {e}")


async def get_all_budgets(page: int, limit: int):
    """This returns all the budgets in the db"""
    try:
        db = SessionLocal()
        skip = (page - 1) * limit
        budgets = (
            db.query(Budget)
            .filter(Budget.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not budgets:
            return None
        return users_to_dict(budgets)
    except Exception as e:
        raise ValueError(f"Couldn't get budgets: {e}")


async def get_a_users_budgets(user_id: str, page: int, limit: int):
    """This returns all the budgets of a user"""
    try:
        db = SessionLocal()
        skip = (page - 1) * limit
        budgets = (
            db.query(Budget)
            .filter(Budget.user_id == user_id, Budget.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not budgets:
            return None
        return users_to_dict(budgets)
    except Exception as e:
        raise ValueError(f"Couldn't get budgets: {e}")


async def get_a_budget(budget_id: str):
    """This returns a budget"""
    try:
        budget = await redis_cache.get(create_budget_key(budget_id))
        if budget:
            return budget
        db = SessionLocal()
        budget = (
            db.query(Budget)
            .filter(Budget.id == budget_id, Budget.is_deleted == False)
            .first()
        )
        if not budget:
            return None
        return model_to_dict(budget)
    except Exception as e:
        raise ValueError(f"Couldn't get budget: {e}")
