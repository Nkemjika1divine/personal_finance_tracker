from schemas.incomeschema import IncomeExpected, IncomeUpdateExpected
from schemas.expenseschema import ExpenseExpected, ExpenseUpdateExpected
from crud.incomes import (
    create_income,
    edit_an_income,
    get_a_users_incomes,
    get_all_incomes,
    get_an_income,
    soft_delete_an_income,
)
from schemas.budgetschema import BudgetExpected
from fastapi import APIRouter, Request, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from utils.errors import Not_Found, ServerError, Unauthorized, Forbidden, Bad_Request


income_router = APIRouter()


@income_router.get("/incomes")
async def get_expenses(
    request: Request, page: int = Query(1, ge=1), limit: int = Query(20, ge=1)
):
    """This returns a list of all incomes"""
    if request.state.role == "admin" or request.state.role == "superuser":
        incomes = get_all_incomes(page=page, limit=limit)
        if incomes:
            return JSONResponse(content=incomes, status_code=HTTP_200_OK)
        raise Not_Found("No incomes found")
    raise Forbidden("You are not authorized to view this")


@income_router.get("/incomes/{user_id}")
async def get_user_incomes(
    request: Request,
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
):
    """This returns the incomes of a user"""
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        incomes = get_a_users_incomes(user_id=user_id, page=page, limit=limit)
        if incomes:
            return JSONResponse(content=incomes, status_code=HTTP_200_OK)
        raise Not_Found("No incomes found")
    raise Forbidden("You are not authorized to view this user's records")


@income_router.get("/income/{user_id}/{income_id}")
async def get_income(request: Request, user_id: str, income_id: str):
    """This returns a user's single income"""
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        income = get_an_income(income_id=income_id)
        if income:
            return JSONResponse(content=income, status_code=HTTP_200_OK)
        raise Not_Found("No income found")
    raise Forbidden("You are not authorized to view this user's records")


@income_router.post("/add_income")
async def create_an_income(request: Request, incomeex: IncomeExpected):
    """This creates a income"""
    income = create_income(
        amount=incomeex.amount,
        user_id=request.state.user["id"],
        description=incomeex.description,
        timestamp=incomeex.timestamp,
    )
    if not income:
        raise Bad_Request("income does not exist")
    return JSONResponse(content=income, status_code=HTTP_201_CREATED)


@income_router.put("/delete_income/{user_id}/{income_id}")
async def soft_delete_income(request: Request, user_id: str, income_id: str):
    "this softdeletes a income"
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        success = soft_delete_an_income(income_id)
        if success:
            return JSONResponse(
                content="income deleted successfully", status_code=HTTP_200_OK
            )
        raise Not_Found("income not found")
    raise Forbidden("You are not authorized to perform this action")


@income_router.put("/edit_income/{user_id}/{income_id}")
async def edit_income(
    request: Request, user_id: str, income_id: str, incomeup: IncomeUpdateExpected
):
    "this edits an income"
    if user_id == request.state.user["id"]:
        income = edit_an_income(
            income_id=income_id,
            amount=incomeup.amount,
            timestamp=incomeup.timestamp,
            description=incomeup.description,
        )
        if income == 0:
            raise Not_Found("income does not exist")
        return JSONResponse(content=income, status_code=HTTP_200_OK)
    raise Forbidden("You are not authorized to perform this action")
