from datetime import date
from crud.analytics import (
    get_expenses_by_category,
    get_expenses_for_all_categories,
    total_expenses,
)
from schemas.budgetschema import BudgetExpected
from fastapi import APIRouter, Request, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from utils.errors import Not_Found, ServerError, Unauthorized, Forbidden, Bad_Request


analytics_router = APIRouter()


@analytics_router.get("/total_exp/{user_id}")
async def get_total_expenses(
    request: Request, start_date: date = None, end_date: date = None
):
    """This returns all the expenses of a user in a period of time"""
    if start_date and end_date:
        if start_date > end_date:
            raise Bad_Request("start date cannot be further in time than end date")
    expenses = total_expenses(
        user_id=request.state.user["id"], start_date=start_date, end_date=end_date
    )
    return JSONResponse(content=expenses, status_code=HTTP_200_OK)


@analytics_router.get("/month_exp/{category_id}")
async def get_monthly_category_expenses(
    request: Request,
    category_id: str,
    year: int,
    month: int = Query(ge=1, le=12),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
):
    """This returns a user's monthly expense for a category"""
    expenses = get_expenses_by_category(
        user_id=request.state.user["id"],
        category_id=category_id,
        year=year,
        month=month,
        page=page,
        limit=limit,
    )
    if not expenses:
        raise Not_Found("no expenses found")
    return JSONResponse(content=expenses, status_code=HTTP_200_OK)


@analytics_router.get("/expense_by_categories")
async def get_User_expenses_by_categories(
    request: Request, start_date: date = None, end_date: date = None
):
    """This gets a user's monthly expenses by categories"""
    expenses = get_expenses_for_all_categories(
        request.state.user["id"], start_date, end_date
    )
    return JSONResponse(content=expenses)
