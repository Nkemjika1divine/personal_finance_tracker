from datetime import date
from crud.analytics import total_expenses
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
