from models.user import User
from storage.db import SessionLocal
from storage.redis import redis_cache
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse
from utils.errors import *
from utils.utils import create_user_token_key
from jose import JWTError, jwt
from os import environ

load_dotenv()


async def auth_middleware(request: Request, call_next):
    """Middleware action to identify authorized logins"""
    # check if the path does not require authentication

    path_list = [
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
        "/register",
        "/login",
    ]
    if any(request.url.path.startswith(path) for path in path_list):
        return await call_next(request)
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401, content={"message": "Unauthorized: Not Authenticated"}
        )
    token = auth_header.split(" ")[1]
    # Verify JWT
    try:
        payload = jwt.decode(
            token,
            environ.get("JWT_SECRET_KEY"),
            algorithms=[environ.get("JWT_ALGORITHM")],
        )
        request.state.user = payload  # store the user's information in the request
    except JWTError:
        return JSONResponse(
            status_code=401, content={"message": "Unauthorized: Invalid Token"}
        )

    user_id = request.state.user["user_id"]
    # check for logged out accounts
    key = create_user_token_key(user_id)
    cached_data = await redis_cache.get(key)
    if cached_data:
        return JSONResponse(
            status_code=401, content={"message": "Unauthorized: Not Authenticated"}
        )
    # get user's role
    """key = create_user_key(user_id)
    user = await redis_cache.get(key)
    if user:
        request.state.role = user["role"]
    else:"""
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Unauthorized: you are not authorized to access this feature"
            },
        )
    request.state.role = user.role
    # block admin only paths
    admin_ony_paths = []
    if any(request.url.path.startswith(path) for path in admin_ony_paths):
        if user.role == "user":
            return JSONResponse(
                status_code=403, content={"message": "Forbidden: Admins Only"}
            )
        # call the next request
    return await call_next(request)
