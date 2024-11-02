import os
from datetime import datetime, timezone, timedelta
from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from http import HTTPStatus
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from tasks_module.services.db_services import UsersRepository
from tasks_module.models.redis_client import RedisClient

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_service = UsersRepository()

redis_service = RedisClient


def get_hash_password(plain_password):
    return pwd_context.hash(plain_password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str):
    user = await user_service.get_by_username(username=username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def auth_user_func(username: str, password: str):
    user = await authenticate_user(username=username, password=password)
    if not user:
        raise Exception("Incorrect username or password")
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"username": user["username"]},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_access_token(
        data={"username": user["username"]},
        expires_delta=refresh_token_expires,
    )
    await redis_service.set_with_expiry(
        key=refresh_token,
        value=user["username"],
        ttl_seconds=refresh_token_expires * 60,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh_user_access_token(refresh_token: str, username: str):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username_from_radis = await redis_service.get(refresh_token)

    if not username_from_radis:
        raise credentials_exception
    if username != username_from_radis:
        raise credentials_exception

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"username": username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def register_user_func(username: str, password: str = None):
    user = await user_service.get_by_username(username=username)
    if user:
        raise Exception("User with this email already exist")

    hashed_password = get_hash_password(plain_password=password)

    new_user = await user_service.create_user(
        username=username, hashed_password=hashed_password
    )

    return new_user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if not username:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await user_service.get_by_username(username=username)
    if user is None:
        raise credentials_exception
    return user


class BearerToken(HTTPBearer):
    async def __call__(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer()),
    ) -> str:

        credentials_exception = HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        if credentials is None or credentials.scheme.lower() != "bearer":
            raise credentials_exception
        return credentials.credentials
