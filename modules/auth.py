from __future__ import annotations

import hashlib
import os
import re
import secrets
from typing import Optional

from database.init import create_user, fetch_user_by_username

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")
MIN_PASSWORD_LENGTH = 6


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    hash_obj = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt.hex() + "$" + hash_obj.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        hash_obj = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return secrets.compare_digest(hash_obj.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False


def register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not USERNAME_RE.match(username):
        return False, "Username must be 3\u201330 characters (letters, numbers, underscores only)."
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if fetch_user_by_username(username) is not None:
        return False, "Username already taken."

    password_hash = hash_password(password)
    create_user(username, password_hash)
    return True, "Account created successfully."


def authenticate_user(username: str, password: str) -> Optional[int]:
    username = username.strip()
    user = fetch_user_by_username(username)
    if user is None:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user["id"]
