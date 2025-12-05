from schemas.expenseschema import ExpenseExpected, ExpenseUpdateExpected
from crud.expenses import (
    create_expense,
    edit_an_expense,
    get_a_expense,
    get_a_users_expenses,
    get_all_expenses,
    soft_delete_an_expense,
)
from schemas.budgetschema import BudgetExpected
from fastapi import APIRouter, Request, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from utils.errors import Not_Found, ServerError, Unauthorized, Forbidden, Bad_Request


expense_router = APIRouter()


@expense_router.get("/expenses")
async def get_expenses(
    request: Request, page: int = Query(1, ge=1), limit: int = Query(20, ge=1)
):
    """This returns a list of all expenses"""
    if request.state.role == "admin" or request.state.role == "superuser":
        expenses = get_all_expenses(page=page, limit=limit)
        if expenses:
            return JSONResponse(content=expenses, status_code=HTTP_200_OK)
        raise Not_Found("No expenses found")
    raise Forbidden("You are not authorized to view this")


@expense_router.get("/expenses/{user_id}")
async def get_user_expenses(
    request: Request,
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
):
    """This returns the expenses of a user"""
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        expenses = get_a_users_expenses(user_id=user_id, page=page, limit=limit)
        if expenses:
            return JSONResponse(content=expenses, status_code=HTTP_200_OK)
        raise Not_Found("No expense found")
    raise Forbidden("You are not authorized to view this user's records")


@expense_router.get("/expense/{user_id}/{expense_id}")
async def get_expense(request: Request, user_id: str, expense_id: str):
    """This returns a user's single expense"""
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        expense = get_a_expense(expense_id=expense_id)
        if expense:
            return JSONResponse(content=expense, status_code=HTTP_200_OK)
        raise Not_Found("No expense found")
    raise Forbidden("You are not authorized to view this user's records")


@expense_router.post("/add_expense")
async def create_an_expense(request: Request, expensexp: ExpenseExpected):
    """This creates a expense"""
    expense = create_expense(
        amount=expensexp.amount,
        category_id=expensexp.category_id,
        user_id=request.state.user["id"],
        description=expensexp.description,
        timestamp=expensexp.timestamp,
    )
    if not expense:
        raise Bad_Request("expense does not exist")
    return JSONResponse(content=expense, status_code=HTTP_201_CREATED)


@expense_router.put("/delete_expense/{user_id}/{expense_id}")
async def soft_delete_expense(request: Request, user_id: str, expense_id: str):
    "this softdeletes a expense"
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        success = soft_delete_an_expense(expense_id)
        if success:
            return JSONResponse(
                content="expense deleted successfully", status_code=HTTP_200_OK
            )
        raise Not_Found("expense not found")
    raise Forbidden("You are not authorized to perform this action")


@expense_router.put("/edit_expense/{user_id}/{expense_id}")
async def edit_expense(
    request: Request, user_id: str, expense_id: str, expenseup: ExpenseUpdateExpected
):
    "this edits an expense"
    if user_id == request.state.user["id"]:
        expense = edit_an_expense(
            expense_id=expense_id,
            amount=expenseup.amount,
            timestamp=expenseup.timestamp,
            description=expenseup.description,
            category_id=expenseup.category_id,
        )
        if expense == -1:
            raise Bad_Request("category does not exist")
        if expense == 0:
            raise Not_Found("expense does not exist")
        return JSONResponse(content=expense, status_code=HTTP_200_OK)
    raise Forbidden("You are not authorized to perform this action")
