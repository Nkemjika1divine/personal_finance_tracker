#!/usr/bin/python3
"""Utility module"""
from models.category import Category
from sqlalchemy import exists
import inflect
import re
from datetime import datetime
import unicodedata
from bcrypt import hashpw, checkpw, gensalt
import re
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect


DEFAULT_CATEGORIES = [
    "Rent and Housing",
    "Utilities",
    "Groceries",
    "Food and Dining",
    "Internet and Data",
    "Airtime and Calls",
    "Transportation",
    "Fuel",
    "Vehicle Maintenance",
    "Business Expenses",
    "Tools and Equipment",
    "Bank Charges",
    "Savings and Investment",
    "Loan and Debt Payment",
    "Entertainment",
    "Shopping",
    "Clothing and Fashion",
    "Subscriptions",
    "Healthcare",
    "Education",
    "Child Expenses",
    "Gifts and Donations",
    "Miscellaneous",
    "Emergency",
]


def create_default_categories():
    """This creates default categories in the DB"""
    from storage.db import SessionLocal

    db = SessionLocal()
    try:
        for name in DEFAULT_CATEGORIES:
            exist = (
                db.query(Category)
                .filter(Category.name == name, Category.user_id == None)
                .first()
            )
            if not exist:
                db.add(Category(name=name, user_id=None))
        db.commit()
    finally:
        db.close()


def category_normalizer(name: str):
    """This checks if a category has been entered before"""

    inflect = inflect.engine()

    name = name.lower()
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = name.replace("&", "and")
    name = re.sub(r"[^\W\S]", "", name)  # remove punctuations
    name = re.sub(r"\s+", " ", name)  # Collapse multiple spaces

    words = name.split()
    if len(words) > 0:
        singular = inflect.singular_noun(words[-1])
        if singular:
            words[-1] = singular
    name = " ".join(words)
    return name


def check_if_word_exists(word: str = None, sentence: str = None) -> bool:
    """Uses regex to check if a word exists in another string"""
    if not word or not sentence:
        return False

    pattern = re.compile(re.escape(word), re.IGNORECASE)
    if pattern.search(sentence):
        return True
    return False


def sort_dict_by_values(dictionary, reverse: bool = True):
    """Sorts a dictionary by value"""
    return {
        keys: values
        for keys, values in sorted(
            dictionary.items(), key=lambda item: item[1], reverse=reverse
        )
    }


def hash_password(password: str) -> str:
    """Hashes a user's password"""
    if not password or type(password) is not str:
        return None
    return hashpw(password.encode("utf8"), gensalt()).decode("utf8")


def model_to_dict(obj, request: Request = None):
    """Converts a model to a JSON serialized object"""
    data = {}
    for model in inspect(obj).mapper.column_attrs:
        value = getattr(obj, model.key)
        if isinstance(value, datetime):
            value = value.isoformat()
        data[model.key] = value
    data.pop("password", None)
    data.pop("is_deleted", None)
    data.pop("deleted_by", None)
    if "cover_image_url" in data and data["cover_image_url"] != None:
        image_url = request.url_for("static", path=f"uploads/{data["cover_image_url"]}")
        data["cover_image_url"] = str(image_url)
    return data


def users_to_dict(users, request: Request = None):
    return {user.id: model_to_dict(user, request) for user in users}


def create_user_key(user_id: str):
    """creates a cache key for users"""
    return f"User:{user_id}"


def create_user_token_key(user_id: str):
    """creates a cache token key for users"""
    return f"UserSessionToken:{user_id}"


def create_category_key(category_id: str):
    """creates a cache key for categories"""
    return f"Category:{category_id}"
