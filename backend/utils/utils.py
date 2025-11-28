#!/usr/bin/python3
"""Utility module"""
from datetime import datetime
from bcrypt import hashpw, checkpw, gensalt
import re
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect


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
