from pydantic import BaseModel
from typing import Union


class User(BaseModel):
    id: int
    username: str


class AccessToken(BaseModel):
    token_type: str
    access_token: str


class Tokens(AccessToken):
    refresh_token: str


class TaskBase(BaseModel):
    title: str
    description: str
    status: Union[str, None] = None


class TaskPut(BaseModel):
    title: Union[str, None] = None
    description: Union[str, None] = None
    status: Union[str, None] = None


class Task(TaskBase):
    id: int
    status: str


class TaskList(BaseModel):
    tasks: list[Task]


class BaseResponse(BaseModel):
    result: bool
