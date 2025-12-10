import stat

from pydantic import Json
from schemas.budgetschema import BudgetExpected, BudgetUpdateExpected
from crud.budgets import (
    add_a_budget,
    current_running_budgets,
    edit_a_budget,
    get_a_budget,
    get_a_users_budgets,
    get_all_budgets,
    soft_delete_a_budget,
)
from fastapi import APIRouter, Request, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from utils.errors import Not_Found, ServerError, Unauthorized, Forbidden, Bad_Request


budget_router = APIRouter()


@budget_router.get("/budgets")
async def get_budgets(
    request: Request, page: int = Query(1, ge=1), limit: int = Query(20, ge=1)
):
    """This returns a list of all budgets"""
    if request.state.role == "admin" or request.state.role == "superuser":
        budgets = get_all_budgets(page=page, limit=limit)
        if budgets:
            return JSONResponse(content=budgets, status_code=HTTP_200_OK)
        raise Not_Found("No budget found")
    raise Forbidden("You are not authorized to view this")


@budget_router.get("/budgets/{user_id}")
async def get_user_budget(
    request: Request,
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
):
    """This returns the budgets of a user"""
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        budgets = get_a_users_budgets(user_id=user_id, page=page, limit=limit)
        if budgets:
            return JSONResponse(content=budgets, status_code=HTTP_200_OK)
        raise Not_Found("No budget found")
    raise Forbidden("You are not authorized to view this user's records")


@budget_router.get("/budget/{user_id}/{budget_id}")
async def get_budget(request: Request, user_id: str, budget_id: str):
    """This returns a user's single budget"""
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        budget = get_a_budget(budget_id=budget_id)
        if budget:
            return JSONResponse(content=budget, status_code=HTTP_200_OK)
        raise Not_Found("No budget found")
    raise Forbidden("You are not authorized to view this user's records")


@budget_router.post("/add_budget")
async def create_budget(request: Request, budgetexpected: BudgetExpected):
    """This creates a budget"""
    budget = add_a_budget(
        amount=budgetexpected.amount_limit,
        start_date=budgetexpected.start_date,
        end_date=budgetexpected.end_date,
        category_id=budgetexpected.category_id,
        user_id=request.state.user["id"],
    )
    if budget == -1:
        raise Bad_Request("Category does not exist")
    if budget == 0:
        raise Bad_Request(
            "There's already a budget set for this category within the timeframe"
        )
    return JSONResponse(content=budget, status_code=HTTP_201_CREATED)


@budget_router.delete("/delete_budget/{user_id}/{budget_id}")
async def soft_delete_budget(request: Request, user_id: str, budget_id: str):
    "this softdeletes a budget"
    if (
        request.state.role == "admin"
        or request.state.role == "superuser"
        or user_id == request.state.user["id"]
    ):
        success = soft_delete_a_budget(budget_id)
        if success:
            return JSONResponse(
                content="budget deleted successfully", status_code=HTTP_200_OK
            )
        raise Not_Found("budget not found")
    raise Forbidden("You are not authorized to perform this action")


@budget_router.put("/edit_budget/{user_id}/{budget_id}")
async def edit_budget(
    request: Request, user_id: str, budget_id: str, budgetupdate: BudgetUpdateExpected
):
    "this edits a budget"
    if user_id == request.state.user["id"]:
        budget = edit_a_budget(
            budget_id,
            budgetupdate.amount_limit,
            budgetupdate.start_date,
            budgetupdate.end_date,
            budgetupdate.category_id,
        )
        if budget == -1:
            raise Bad_Request("category does not exist")
        if budget == -2:
            raise Bad_Request("cannot edit a budget whose period has passed")
        if budget == 0:
            raise Not_Found("budget does not exist")
        return JSONResponse(content=budget, status_code=HTTP_200_OK)
    raise Forbidden("You are not authorized to perform this action")


@budget_router.get("/current_running_budgets")
async def get_current_running_budgets(request: Request):
    """This returns all the current running budgets for a user"""
    budgets = current_running_budgets(request.state.user["id"])
    if not budgets:
        raise Not_Found("No current running budget")
    return JSONResponse(content=budgets, status_code=HTTP_200_OK)
