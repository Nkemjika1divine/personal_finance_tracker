from ast import mod
from backend.routes import categories
from models.category import Category
from sqlalchemy.orm import Session
from storage.db import SessionLocal
from storage.redis import RedisCache, redis_cache
from models.user import User
from utils.utils import (
    create_category_key,
    create_user_key,
    model_to_dict,
    users_to_dict,
    hash_password,
)

indexes = {
    "categories": "idx:Category",
}


async def create_a_category(name: str, user_id: str = None):
    """This creates a new category in the DB"""
    db = SessionLocal()
    try:
        category = Category(name=name, user_id=user_id)
        db.add(category)
        db.commit()
        category = model_to_dict(category)
        db.close()
        await redis_cache.set(
            key=create_category_key(category_id=category["id"]),
            value=category,
            indexes=[indexes["categories"]],
        )
        return category
    except Exception as e:
        raise ValueError(f"Couldn't save category: {e}")


async def delete_a_category(category_id: str):
    """This deletes a category"""
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return 0
        db.delete(category)
        await redis_cache.delete(
            create_category_key(category_id=category.id), index=indexes["categories"]
        )
        db.commit()
        db.close()
        return 1
    except Exception as e:
        raise ValueError(f"Couldn't save category: {e}")


async def get_all_categories():
    """This returns all the categories in the db"""
    categories = await redis_cache.get_index([indexes["categories"]])
    if categories:
        return categories
    db = SessionLocal()
    categories = db.query(Category).all()
    if not categories:
        return None
    return users_to_dict(categories)
