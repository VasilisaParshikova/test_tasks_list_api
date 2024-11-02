from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
import enum

from tasks_module.models.database import Base


class StatusEnum(enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String, nullable=True)
    tasks = relationship("Tasks", backref="user", lazy="selectin")

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password,
        }


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.CREATED, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def to_json(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["status"] = self.status.value
        return data
