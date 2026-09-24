from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

ProjectStatus = Literal["planning", "active", "completed", "paused"]
TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high"]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    status: ProjectStatus = "planning"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectRead(ProjectBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


class MemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    role: str = Field(default="Contributor", min_length=1, max_length=80)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    role: str | None = Field(default=None, min_length=1, max_length=80)


class MemberRead(MemberBase, ORMModel):
    id: int
    created_at: datetime


class LabelBase(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    color: str = Field(default="#2563eb", pattern=r"^#[0-9a-fA-F]{6}$")


class LabelCreate(LabelBase):
    pass


class LabelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")


class LabelRead(LabelBase, ORMModel):
    id: int


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = ""
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    due_date: date | None = None
    project_id: int
    assignee_id: int | None = None


class TaskCreate(TaskBase):
    label_ids: list[int] = []


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    project_id: int | None = None
    assignee_id: int | None = None
    label_ids: list[int] | None = None


class TaskRead(TaskBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime
    labels: list[LabelRead]


class DashboardSummary(BaseModel):
    projects: int
    members: int
    tasks: int
    labels: int
    tasks_by_status: dict[str, int]