from storage.db import get_db
from storage.redis import redis_cache
from dotenv import load_dotenv
from crud.users import (
    create_user,
    delete_a_user,
    delete_a_user_permanently,
    get_users,
    update_user,
)
from fastapi import APIRouter, Request, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from schemas.userschema import UserExpected, UserResponse, UserUpdate
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from typing import Annotated
from uuid import uuid4
from utils.errors import Not_Found, ServerError, Unauthorized, Forbidden, Bad_Request
from utils.utils import (
    create_user_token_key,
    model_to_dict,
)
from utils.email import send_welcome_email_to_user
from utils.security import authenticate_user, create_access_token


load_dotenv()


user_router = APIRouter()


@user_router.post("/register", response_model=UserResponse)
async def register(background_tasks: BackgroundTasks, user_input: UserExpected):
    """Route for Registration"""
    user = await create_user(
        name=user_input.username,
        email=user_input.email,
        password=user_input.password,
    )
    if not user:
        raise Forbidden("email already registered")
    # Send email
    background_tasks.add_task(
        send_welcome_email_to_user, user_input.email.lower(), user_input.username
    )
    return JSONResponse(content=user, status_code=HTTP_201_CREATED)


@user_router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise Unauthorized(detail="Invalid Email or Password")
    data = {"user_id": user.id, "email": user.email}
    access_token = create_access_token(data=data)
    return JSONResponse(
        content={
            "token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
        },
        status_code=HTTP_200_OK,
    )


@user_router.put("/edit_profile/{user_id}")
async def edit_profile(
    user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)
):
    """Allows a user to edit the profile of another user"""
    user = update_user(user_id, user_update.dict(exclude_unset=True))
    if not user:
        raise Not_Found("User does not exist")
    return JSONResponse(content=user, status_code=HTTP_200_OK)


@user_router.put("/edit_my_profile")
async def edit_my_profile(request: Request, user_update: UserUpdate):
    """Edits a user's profile by the user"""
    current_user = request.state.user
    user = update_user(current_user["user_id"], user_update.dict(exclude_unset=True))
    if not user:
        raise Not_Found(f"User does not exist")
    return JSONResponse(content=model_to_dict(user), status_code=HTTP_201_CREATED)


@user_router.get("/users")
async def get_all_users(page: int = Query(1, ge=1), limit: int = Query(20, ge=1)):
    """Gets all the users in the DB"""
    users = get_users(page=page, limit=limit)
    if users:
        return JSONResponse(content=users, status_code=HTTP_200_OK)
    raise Not_Found("users do not exist")


@user_router.put("/delete_user/{user_id}")
async def delete_user(request: Request, user_id: str):
    """This deletes a user from the system"""
    if request.state.user["role"] != "superuser":
        raise Unauthorized("You are not authorized to perform this action")
    success = delete_a_user(user_id, request.state.user["user_id"])
    if success:
        return JSONResponse(
            content="User successfully deleted", status_code=HTTP_200_OK
        )
    raise Not_Found("User does not exist")


@user_router.delete("/rm_user_perm/{user_id}")
async def remove_user(request: Request, user_id: str):
    """This permanently deletes a user from the system"""
    if request.state.user["role"] != "superuser":
        raise Unauthorized("You are not authorized to perform this action")
    success = delete_a_user_permanently(user_id)
    if success == 0:
        raise Unauthorized("This user has to be deactivated first")
    if success == 1:
        return JSONResponse(
            content="User successfully deleted", status_code=HTTP_200_OK
        )
    raise Not_Found("User does not exist")


@user_router.post("/logout")
async def logout(request: Request):
    """This handles a user's logout"""
    token = request.headers.get("Authorization").split(" ")[1]
    key = create_user_token_key(request.state.user["user_id"])
    await redis_cache.set(key=key, value=token, exp_seconds=3600)
    return JSONResponse(content="User logged out successfully", status_code=HTTP_200_OK)
