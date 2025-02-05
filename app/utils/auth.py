# app/utils/auth.py
import jwt
from datetime import datetime, timedelta
from app.config import settings


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(hours=1)
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt
