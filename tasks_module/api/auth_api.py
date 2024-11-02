from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from http import HTTPStatus
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from tasks_module.api.schemas import User, Tokens, AccessToken
from tasks_module.dependenses import (
    get_register_user_func,
    get_auth_user_func,
    token_required,
    get_refresh_user_access_token_fun,
    get_token,
)

router = APIRouter()


@router.post("/registe", response_model=User)
async def registration(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    registration_func=Depends(get_register_user_func),
):
    try:
        new_user = await registration_func(form_data.username, form_data.password)
        return JSONResponse(content=new_user)
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=exc.args)


@router.post("/login", response_model=Tokens)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service=Depends(get_auth_user_func),
):
    try:
        token = await auth_service(form_data.username, form_data.password)
        return JSONResponse(content=token)

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=exc.args,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/refresh", dependencies=[Depends(token_required())], response_model=AccessToken
)
async def refresh_access_token(
    user=Depends(token_required()),
    service_func=Depends(get_refresh_user_access_token_fun),
    token=Depends(get_token()),
):
    try:
        token = await service_func(token, user["username"])
        return JSONResponse(content=token)

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=exc.args,
            headers={"WWW-Authenticate": "Bearer"},
        )
