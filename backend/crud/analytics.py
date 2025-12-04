from datetime import date

from sqlalchemy import func
from models.expense import Expense
from storage.db import SessionLocal


async def total_expenses(user_id: str, start_date: date = None, end_date: date = None):
    """This returns total expenses over a period of time"""
    db = SessionLocal()
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
