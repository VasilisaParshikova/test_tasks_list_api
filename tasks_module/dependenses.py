from tasks_module.services.auth_utils import (
    register_user_func,
    auth_user_func,
    get_current_user,
    refresh_user_access_token,
    BearerToken,
)
from tasks_module.services.db_services import TaskRepository


def get_auth_user_func():
    return auth_user_func


def get_register_user_func():
    return register_user_func


def token_required():
    return get_current_user


def get_refresh_user_access_token_fun():
    return refresh_user_access_token


def get_task_repository():
    return TaskRepository()


def get_token():
    return BearerToken()
