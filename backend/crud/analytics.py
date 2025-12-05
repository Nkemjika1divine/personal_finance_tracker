from calendar import monthrange
from datetime import datetime, date
from sqlalchemy import func
from models.budget import Budget
from models.category import Category
from utils.utils import users_to_dict
from models.expense import Expense
from storage.db import SessionLocal


async def total_expenses(user_id: str, start_date: date = None, end_date: date = None):
    """This returns total expenses over a period of time"""
    db = SessionLocal()
    try:
        if start_date and end_date:
            expenses = (
                db.query(func.sum(Expense.amount))
                .filter(Expense.user_id == user_id, Expense.timestamp >= start_date)
                .filter(Expense.user_id == user_id, Expense.timestamp <= end_date)
            )
        if start_date and not end_date:
            expenses = db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id, Expense.timestamp >= start_date
            )
        if end_date and not start_date:
            expenses = db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id, Expense.timestamp <= end_date
            )
        if not end_date and not start_date:
            expenses = (
                db.query(func.sum(Expense.amount))
                .filter(
                    Expense.user_id == user_id,
                )
                .all()
            )
        total = expenses.scalar() or 0

        return {
            "total_spending": float(total),
            "start_date": start_date,
            "end_date": end_date,
        }
    except Exception as e:
        raise ValueError(f"Value Error: {e}")


async def get_expenses_by_category(
    user_id: str, category_id: str, month: int, year: int, page: int, limit: int
):
    """This returns the expenses made on a category by month of a year"""
    db = SessionLocal()
    skip = (page - 1) * limit
    start_date = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)
    try:
        expenses = (
            db.query(Expense)
            .filter(Expense.user_id == user_id, Expense.category_id == category_id)
            .filter(Expense.timestamp >= start_date)
            .filter(Expense.timestamp <= end_date)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not expenses:
            return None
        return users_to_dict(expenses)
    except Exception as e:
        raise ValueError(f"Value Error: {e}")


async def get_expenses_for_all_categories(
    user_id: str, start_date: date, end_date: date
):
    """This returns all expenses made for all categories for a period of time"""
    db = SessionLocal()
    try:
        expenses = (
            db.query(
                Category.name,
                func.coalesce(func.sum(Expense.amount), 0).label("total"),
            )
            .outerjoin(
                Expense,
                (Expense.category_id == Category.id)
                & (Expense.user_id == user_id)
                & (Expense.timestamp >= start_date)
                & (Expense.timestamp <= end_date),
            )
            .group_by(Category.id, Category.name)
            .all()
        )
        return {category: float(total) for category, total in expenses}
    except Exception as e:
        raise ValueError(f"Value Error: {e}")


async def compare_expenses_with_budget(budget_id: str, user_id: str):
    """This returns the expenses made over a budgeted period"""
    db = SessionLocal()
    try:
        result = (
            db.query(Expense.id, Expense.amount, Expense.timestamp, Expense.description)
            .join(
                Budget,
                (Expense.category_id == Budget.category_id)
                & (Expense.user_id == Budget.user_id)
                & (Expense.timestamp >= Budget.start_date)
                & (Expense.timestamp <= Budget.end_date),
            )
            .filter(Budget.id == budget_id, Budget.user_id == user_id)
            .all()
        )
        result = [
            {
                "id": exp.id,
                "amount": float(exp.amount),
                "description": exp.description,
                "timestamp": exp.timestamp.isoformat(),
            }
            for exp in result
        ]
        return result
    except Exception as e:
        raise ValueError(f"Value Error: {e}")
