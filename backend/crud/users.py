from uuid import uuid4
from sqlalchemy.orm import Session
from storage.db import SessionLocal
from storage.redis import redis_cache
from models.user import User
from utils.utils import create_user_key, model_to_dict, users_to_dict, hash_password


async def create_user(name: str, email: str, password: str):
    """Creates a new user in the DB"""
    db = SessionLocal()
    user = get_user_by_email(email=email)
    if user:
        return None
    # check if this is the first account being created
    user: db.query(User).first()
    role = "user"
    if not user:
        role = "superuser"
    # validate and hash the password
    hashed_password = hash_password(password)
    # Save the user
    user = User(
        username=name,
        email=email.lower(),
        password=hashed_password,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user = model_to_dict(user)
    await redis_cache.set(key=create_user_key(user["id"]), value=user)
    return user


def get_user_by_email(email: str):
    """Gets a user by searching with the email"""
    db = SessionLocal()
    user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
    if user:
        return user
    return None


async def get_user_by_id(db: Session, user_id: str):
    """Gets a user by searching with the id"""
    key = create_user_key(user_id)
    cached_info = redis_cache.get(key=key)
    if cached_info:
        return cached_info
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if user:
        user = model_to_dict(user)
        await redis_cache.set(key=key, value=user)
        return user
    return None


async def update_user(user_id: str, updates: dict):
    """This updates a user's information in the DB"""
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        return None
    for key, value in updates.items():
        if key == "password":
            updates["password"] = hash_password(updates["password"])
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    user = model_to_dict(user)
    # Create key for caching the User info
    # Cache the user info
    await redis_cache.set(key=create_user_key(user_id), value=user)
    return user


async def delete_a_user(user_id: str, deleter_id: str) -> int:
    """This soft_deletes a user from the db"""
    # Delete the user from redis cache
    key = create_user_key(user_id)
    await redis_cache.delete(key)

    # delete the user from the db
    db = SessionLocal()
    try:
        user = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if user:
            user.is_deleted = True
            user.deleted_by = deleter_id
    except Exception as e:
        raise ValueError(f"Error: {e}")
    return 1


def delete_a_user_permanently(user_id: str) -> int:
    """This deletes a user permanently"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return -1
        if user.is_deleted is not True:
            return 0
        db.delete(user)
        db.commit()
    except Exception as e:
        raise ValueError(f"Error: {e}")
    return 1


def get_users(page: int, limit: int):
    """This returns all users in the DB using pages"""
    db = SessionLocal()
    skip = (page - 1) * limit
    users = db.query(User).offset(skip).limit(limit).all()
    if not users:
        return None
    total = db.query(User).count()
    users = users_to_dict(users)
    return {"total": total, "data": users}
