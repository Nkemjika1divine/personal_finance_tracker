from schemas.categoryschema import CategoryExpected
from crud.categories import create_a_category, delete_a_category, get_all_categories
from fastapi import APIRouter, Request, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from schemas.userschema import UserExpected, UserResponse, UserUpdate
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from typing import Annotated
from uuid import uuid4
from utils.errors import Not_Found, ServerError, Unauthorized, Forbidden, Bad_Request


category_router = APIRouter()


@category_router.get("/categories")
async def get_categories():
    """This returns all the categories in the DB"""
    categories = get_all_categories()
    if categories:
        return JSONResponse(content=categories, status_code=HTTP_200_OK)
    raise Not_Found("No caegories in the DB")


@category_router.post("/add_category")
async def create_category(request: Request, categoryexpected: CategoryExpected):
    """This creates a category"""
    category = create_a_category(categoryexpected.name, request.state.user["id"])
    if not category:
        raise Bad_Request("Couldn't create category")
    return JSONResponse(content=category, status_code=HTTP_201_CREATED)


@category_router.delete("/delete_category/{category_id}")
async def delete_category(category_id: str):
    """This deletes a category from the system"""
    success = delete_a_category(category_id)
    if success:
        return JSONResponse(
            content="category deleted successfuly", status_code=HTTP_200_OK
        )
