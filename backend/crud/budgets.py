from datetime import date, datetime
from models.budget import Budget
from models.category import Category
from models.expense import Expense
from sqlalchemy import func
from sqlalchemy.orm import Session
from storage.db import SessionLocal
from storage.redis import redis_cache
from utils.utils import (
    create_budget_key,
    model_to_dict,
    users_to_dict,
)

indexes = {
    "budgets": "idx:Budget",
}


def is_after_running_budget(
    db: Session, start_date: date, category_id: str, user_id: str
) -> bool:
    """This checks if a budget starts after the current running budget of a category ends"""
    try:
        budget = (
            db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.end_date >= start_date,
            )
            .first()
        )
        if budget:
            return True
        return False
    except Exception as e:
        raise ValueError(f"Couldn't check existing budget: {e}")


def check_budget_expense_level(budget: Budget):
    """This checks and returns the amount spent so far in a budget"""
    db = SessionLocal()
    try:
        total_spent = (
            db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(Expense.user_id == budget.user_id)
            .filter(Expense.category_id == budget.category_id)
            .filter(Expense.timestamp >= budget.start_date)
            .filter(Expense.timestamp <= budget.end_date)
            .scalar()
        )
        return float(total_spent)
    except Exception as e:
        raise ValueError(f"Couldn't save budget: {e}")


async def add_a_budget(
    amount: float, start_date: date, end_date: date, user_id: str, category_id: str
):
    """This adds a budget to the DB"""
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return -1
        if not is_after_running_budget(db, start_date, category_id, user_id):
            return 0
        budget = Budget(
            amount_limit=amount,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            category_id=category_id,
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


async def edit_a_budget(
    budget_id: str,
    amount: float = None,
    start_date: date = None,
    end_date: date = None,
    category_id: str = None,
):
    """This edits a budget"""
    db = SessionLocal()
    try:
        if category_id:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                return -1
        budget = (
            db.query(Budget)
            .filter(Budget.id == budget_id, Budget.is_deleted == False)
            .first()
        )
        if budget.end_date > datetime.now():
            return -2
        if not budget:
            return 0
        if amount:
            budget.amount_limit = amount
        if start_date:
            budget.start_date = start_date
        if end_date:
            budget.end_date = end_date
        db.commit()
        db.refresh(budget)
        budget = model_to_dict(budget)
        db.close()
        await redis_cache.set(
            key=create_budget_key(budget_id=budget["id"]),
            value=budget,
            indexes=[indexes["budgets"]],
        )
        return budget
    except Exception as e:
        raise ValueError(f"Couldn't edit budget: {e}")


async def current_running_budgets(user_id: str):
    """This returns all the current running budgets for a user"""
    db = SessionLocal()
    try:
        budgets = (
            db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.start_date <= datetime.now(),
                Budget.end_date >= datetime.now(),
            )
            .all()
        )
        if not budgets:
            return None
        return users_to_dict(budgets)
    except Exception as e:
        raise ValueError(f"Couldn't get budgets: {e}")


async def category_current_running_budget(user_id: str, category_id: str):
    """Returns the current running budget for a category"""
    db = SessionLocal()
    try:
        budget = (
            db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.start_date <= datetime.now(),
                Budget.end_date >= datetime.now(),
            )
            .first()
        )
        if not budget:
            return None
        return model_to_dict(budget)
    except Exception as e:
        raise ValueError(f"Couldn't get budgets: {e}")
