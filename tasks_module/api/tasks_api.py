from fastapi import APIRouter, Depends, Request, Path
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from http import HTTPStatus
from typing import Union
from tasks_module.api.schemas import TaskBase, Task, TaskList, TaskPut, BaseResponse
from tasks_module.dependenses import token_required, get_task_repository

router = APIRouter()


@router.get("", dependencies=[Depends(token_required())], response_model=TaskList)
async def get_tasks(
    status: Union[str, None] = None,
    user=Depends(token_required()),
    tasks_service=Depends(get_task_repository),
):
    tasks_list = await tasks_service.get_tasks_list(user_id=user["id"], status=status)
    print(tasks_list)
    return JSONResponse(content=tasks_list)


@router.post("", dependencies=[Depends(token_required())], response_model=Task)
async def create_task(
    task_data: TaskBase,
    user=Depends(token_required()),
    tasks_service=Depends(get_task_repository),
):
    try:
        new_task = await tasks_service.create_task(
            user_id=user["id"],
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=exc.args,
        )
    return JSONResponse(content=new_task)


@router.put("/{id}", dependencies=[Depends(token_required())], response_model=Task)
async def update_task(
    task_data: TaskPut,
    id: int = Path(title="Id of the task"),
    user=Depends(token_required()),
    tasks_service=Depends(get_task_repository),
):
    try:
        task = await tasks_service.update_task(
            id=id,
            user_id=user["id"],
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=exc.args,
        )
    return JSONResponse(content=task)


@router.delete(
    "/{id}", dependencies=[Depends(token_required())], response_model=BaseResponse
)
async def delete_task(
    id: int = Path(title="Id of the task"),
    user=Depends(token_required()),
    tasks_service=Depends(get_task_repository),
):
    try:
        await tasks_service.delete_task(id=id, user_id=user["id"])
        return JSONResponse(content={"result": True})
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=exc.args,
        )
