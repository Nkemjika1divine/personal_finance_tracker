from fastapi import UploadFile
from crud.users import get_user_by_email
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import environ
import imghdr
import jwt


load_dotenv()
ALLOWED_TYPES = ["jpeg", "jpg", "png"]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict):
    data_to_encode = data.copy()
    expiry_time = datetime.utcnow() + timedelta(
        hours=int(environ.get("ACCESS_TOKEN_EXPIRY_HOUR"))
    )
    data_to_encode.update({"exp": expiry_time})
    encoded_jwt = jwt.encode(
        data_to_encode,
        environ.get("JWT_SECRET_KEY"),
        algorithm=environ.get("JWT_ALGORITHM"),
    )
    # to get a jwt key, run "openssl rand -hex 32"
    return encoded_jwt


def authenticate_user(email: str, password: str):
    """Authenticates the password of a user. Returns true if the password is correct"""
    from storage.db import SessionLocal

    db = SessionLocal()
    user = get_user_by_email(email=email)
    if user and user.is_valid_password(password):
        return user
    return False


async def validate_images(file: UploadFile) -> int:
    """This is used to validate a file uploaded to fastAPI"""
    contents = await file.read()
    if len(contents) > int(environ.get("MAX_PIC_SIZE")):
        return -1

    if file.content_type not in ["image/jpeg", "image/png"]:
        return -2

    filetype = imghdr.what(None, h=contents)
    if filetype not in ALLOWED_TYPES:
        return 0

    file.file.seek(0)
    return 1
