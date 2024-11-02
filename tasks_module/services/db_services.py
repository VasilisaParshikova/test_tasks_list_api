from sqlalchemy.future import select
from sqlalchemy.exc import DBAPIError

from tasks_module.models.models import Users, Tasks, StatusEnum
from tasks_module.models.database import session


class UsersRepository:

    def __init__(self, db_session=session):
        self._session = db_session

    async def get_by_username(self, username: str):
        user = await self._session.execute(
            select(Users).where(Users.username == username)
        )
        user = user.scalars().first()
        if not user:
            return {}
        return user.to_json()

    async def create_user(self, username: str, hashed_password: str):
        new_user = Users(username=username, hashed_password=hashed_password)
        self._session.add(new_user)
        try:
            await self._session.commit()
            return new_user.to_json()
        except DBAPIError as exc:
            raise Exception(f"{exc.detail}")


class TaskRepository:

    def __init__(self, db_session=session):
        self._session = db_session

    async def create_task(
        self, user_id: int, title: str, description: str, status: str = None
    ):
        if status:
            try:
                status = StatusEnum(status)
            except ValueError:
                raise ValueError(
                    f"Invalid status: {status}. Allowed values are: {[e.value for e in StatusEnum]}"
                )
            new_task = Tasks(
                user_id=user_id, title=title, description=description, status=status
            )
        else:
            new_task = Tasks(user_id=user_id, title=title, description=description)
        self._session.add(new_task)
        try:
            await self._session.commit()
            return new_task.to_json()
        except DBAPIError as exc:
            raise Exception(f"{exc.detail}")

    async def delete_task(self, user_id: int, id: int):
        task = await self._session.execute(select(Tasks).where(Tasks.id == id))
        task = task.scalars().first()
        if not task:
            raise Exception("No this task in database.")
        if task.user_id != user_id:
            raise Exception("Denied")
        try:
            await self._session.delete(task)
            return True
        except DBAPIError as exc:
            raise Exception(f"{exc.detail}")

    async def get_tasks_list(self, user_id: int, status: str = None):
        if status:
            try:
                status = StatusEnum(status)
            except ValueError:
                raise ValueError(
                    f"Invalid status: {status}. Allowed values are: {[e.value for e in StatusEnum]}"
                )
            tasks = await self._session.execute(
                select(Tasks).where(Tasks.user_id == user_id, Tasks.status == status)
            )
        else:
            tasks = await self._session.execute(
                select(Tasks).where(Tasks.user_id == user_id)
            )
        tasks = tasks.scalars().all()
        if not tasks:
            return []
        return [task.to_json() for task in tasks]

    async def update_task(
        self,
        id: int,
        user_id: int,
        title: str = None,
        description: str = None,
        status: str = None,
    ):
        if not title and not description and not status:
            raise Exception("No data")

        task = await self._session.execute(
            select(Tasks).where(Tasks.user_id == user_id, Tasks.id == id)
        )
        task = task.scalars().first()

        if not task:
            raise Exception("No this task in database.")

        if title:
            task.title = title

        if description:
            task.description = description

        if status:
            try:
                status = StatusEnum(status)
            except ValueError:
                raise ValueError(
                    f"Invalid status: {status}. Allowed values are: {[e.value for e in StatusEnum]}"
                )
            task.status = status

        self._session.add(task)

        try:
            await self._session.commit()
            return task.to_json()
        except DBAPIError as exc:
            raise Exception(f"{exc.detail}")
