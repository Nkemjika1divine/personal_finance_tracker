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


async def weekly_spending_trend(
    user_id: str, start_date: date = None, end_date: date = None
):
    """This returns the spending trend of a user by days of the week"""
    db = SessionLocal()
    try:
        if start_date and end_date:
            trend = (
                db.query(
                    func.dayname(Expense.timestamp).label("weekday"),
                    func.sum(Expense.amount).label("total"),
                )
                .filter(Expense.user_id == user_id)
                .filter(Expense.timestamp >= start_date)
                .filter(Expense.timestamp <= end_date)
            )
        if start_date and not end_date:
            trend = (
                db.query(
                    func.dayname(Expense.timestamp).label("weekday"),
                    func.sum(Expense.amount).label("total"),
                )
                .filter(Expense.user_id == user_id)
                .filter(Expense.timestamp >= start_date)
            )
        if end_date and not start_date:
            trend = (
                db.query(
                    func.dayname(Expense.timestamp).label("weekday"),
                    func.sum(Expense.amount).label("total"),
                )
                .filter(Expense.user_id == user_id)
                .filter(Expense.timestamp <= end_date)
            )
        if not start_date and not end_date:
            trend = db.query(
                func.dayname(Expense.timestamp).label("weekday"),
                func.sum(Expense.amount).label("total"),
            ).filter(Expense.user_id == user_id)

        results = trend.group_by(func.dayname(Expense.timestamp)).all()

        # Default so all days appear even if empty
        week_template = {
            "Monday": 0.0,
            "Tuesday": 0.0,
            "Wednesday": 0.0,
            "Thursday": 0.0,
            "Friday": 0.0,
            "Saturday": 0.0,
            "Sunday": 0.0,
        }

        for weekday, total in results:
            week_template[weekday] = float(total)

        return week_template

    except Exception as e:
        raise ValueError(f"Value Error: {e}")


async def average_daily_spending(
    user_id: str,
    start_date: date = None,
    end_date: date = None,
):
    """This calculates the average daily spend over a period of time"""
    db = SessionLocal()
    try:
        if not start_date and not end_date:
            query = db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id
            )

        if start_date and not end_date:
            query = (
                db.query(func.sum(Expense.amount))
                .filter(Expense.user_id == user_id)
                .filter(Expense.timestamp >= start_date)
            )
        if end_date and not start_date:
            query = (
                db.query(func.sum(Expense.amount))
                .filter(Expense.user_id == user_id)
                .filter(Expense.timestamp <= end_date)
            )
        if start_date and end_date:
            query = (
                db.query(func.sum(Expense.amount))
                .filter(Expense.user_id == user_id)
                .filter(Expense.timestamp >= start_date)
                .filter(Expense.timestamp <= end_date)
            )
        total = query.scalar() or 0

        # Determine date range
        # If no dates provided, use user's earliest + latest expense
        if not start_date or not end_date:
            minmax = (
                db.query(func.min(Expense.timestamp), func.max(Expense.timestamp))
                .filter(Expense.user_id == user_id)
                .first()
            )
            if not start_date:
                start_date = minmax[0]
            if not end_date:
                end_date = minmax[1]

        if not start_date or not end_date:
            return {"average_daily_spending": 0}

        days = (end_date - start_date).days + 1
        avg = total / days if days > 0 else 0

        return {"average_daily_spending": round(avg, 2)}
    except Exception as e:
        raise ValueError(f"Value Error: {e}")


async def average_weekly_spending(
    user_id: str,
    start_date: date = None,
    end_date: date = None,
):
    """This returns the average weekly spending over a period of time"""
    db = SessionLocal()
    try:
        query = db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id)

        if start_date:
            query = query.filter(Expense.timestamp >= start_date)
        if end_date:
            query = query.filter(Expense.timestamp <= end_date)

        total = query.scalar() or 0

        # Determine range
        if not start_date or not end_date:
            minmax = (
                db.query(func.min(Expense.timestamp), func.max(Expense.timestamp))
                .filter(Expense.user_id == user_id)
                .first()
            )
            if not start_date:
                start_date = minmax[0]
            if not end_date:
                end_date = minmax[1]

        if not start_date or not end_date:
            return {"average_weekly_spending": 0}

        weeks = ((end_date - start_date).days + 1) / 7
        avg = total / weeks if weeks > 0 else 0

        return {"average_weekly_spending": round(avg, 2)}
    except Exception as e:
        raise ValueError(f"Value Error: {e}")
