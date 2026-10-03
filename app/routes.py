from typing import Annotated, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api")
root_router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
ModelType = TypeVar("ModelType")


def get_or_404(db: Session, model: type[ModelType], item_id: int) -> ModelType:
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return item


def commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="A record with that value already exists") from error


@root_router.get("/ping")
def ping() -> dict[str, str]:
    return {"ping": "pong"}


@router.get("/health")
def health(db: DbSession) -> dict[str, str]:
    db.execute(select(1))
    return {"status": "ok"}


@router.post("/projects", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: schemas.ProjectCreate, db: DbSession) -> models.Project:
    project = models.Project(**payload.model_dump())
    db.add(project)
    commit(db)
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[schemas.ProjectRead])
def list_projects(db: DbSession) -> list[models.Project]:
    return list(db.scalars(select(models.Project).order_by(models.Project.created_at.desc())))


@router.get("/projects/{project_id}", response_model=schemas.ProjectRead)
def get_project(project_id: int, db: DbSession) -> models.Project:
    return get_or_404(db, models.Project, project_id)


@router.patch("/projects/{project_id}", response_model=schemas.ProjectRead)
def update_project(project_id: int, payload: schemas.ProjectUpdate, db: DbSession) -> models.Project:
    project = get_or_404(db, models.Project, project_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    commit(db)
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: DbSession) -> Response:
    db.delete(get_or_404(db, models.Project, project_id))
    commit(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/members", response_model=schemas.MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(payload: schemas.MemberCreate, db: DbSession) -> models.Member:
    member = models.Member(**payload.model_dump())
    db.add(member)
    commit(db)
    db.refresh(member)
    return member


@router.get("/members", response_model=list[schemas.MemberRead])
def list_members(db: DbSession) -> list[models.Member]:
    return list(db.scalars(select(models.Member).order_by(models.Member.name)))


@router.get("/members/{member_id}", response_model=schemas.MemberRead)
def get_member(member_id: int, db: DbSession) -> models.Member:
    return get_or_404(db, models.Member, member_id)


@router.patch("/members/{member_id}", response_model=schemas.MemberRead)
def update_member(member_id: int, payload: schemas.MemberUpdate, db: DbSession) -> models.Member:
    member = get_or_404(db, models.Member, member_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, key, value)
    commit(db)
    db.refresh(member)
    return member


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: DbSession) -> Response:
    db.delete(get_or_404(db, models.Member, member_id))
    commit(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/labels", response_model=schemas.LabelRead, status_code=status.HTTP_201_CREATED)
def create_label(payload: schemas.LabelCreate, db: DbSession) -> models.Label:
    label = models.Label(**payload.model_dump())
    db.add(label)
    commit(db)
    db.refresh(label)
    return label


@router.get("/labels", response_model=list[schemas.LabelRead])
def list_labels(db: DbSession) -> list[models.Label]:
    return list(db.scalars(select(models.Label).order_by(models.Label.name)))


@router.get("/labels/{label_id}", response_model=schemas.LabelRead)
def get_label(label_id: int, db: DbSession) -> models.Label:
    return get_or_404(db, models.Label, label_id)


@router.patch("/labels/{label_id}", response_model=schemas.LabelRead)
def update_label(label_id: int, payload: schemas.LabelUpdate, db: DbSession) -> models.Label:
    label = get_or_404(db, models.Label, label_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(label, key, value)
    commit(db)
    db.refresh(label)
    return label


@router.delete("/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(label_id: int, db: DbSession) -> Response:
    db.delete(get_or_404(db, models.Label, label_id))
    commit(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def task_query():
    return select(models.Task).options(selectinload(models.Task.labels))


def validate_task_relations(db: Session, project_id: int, assignee_id: int | None) -> None:
    get_or_404(db, models.Project, project_id)
    if assignee_id is not None:
        get_or_404(db, models.Member, assignee_id)


def get_labels(db: Session, label_ids: list[int]) -> list[models.Label]:
    labels = list(db.scalars(select(models.Label).where(models.Label.id.in_(label_ids)))) if label_ids else []
    if len(labels) != len(set(label_ids)):
        raise HTTPException(status_code=404, detail="One or more labels were not found")
    return labels


@router.post("/tasks", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate, db: DbSession) -> models.Task:
    values = payload.model_dump(exclude={"label_ids"})
    validate_task_relations(db, payload.project_id, payload.assignee_id)
    task = models.Task(**values, labels=get_labels(db, payload.label_ids))
    db.add(task)
    commit(db)
    return db.scalar(task_query().where(models.Task.id == task.id))


@router.get("/tasks", response_model=list[schemas.TaskRead])
def list_tasks(db: DbSession, project_id: int | None = None, task_status: str | None = None) -> list[models.Task]:
    query = task_query().order_by(models.Task.created_at.desc())
    if project_id is not None:
        query = query.where(models.Task.project_id == project_id)
    if task_status is not None:
        query = query.where(models.Task.status == task_status)
    return list(db.scalars(query))


@router.get("/tasks/{task_id}", response_model=schemas.TaskRead)
def get_task(task_id: int, db: DbSession) -> models.Task:
    task = db.scalar(task_query().where(models.Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=schemas.TaskRead)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: DbSession) -> models.Task:
    task = get_task(task_id, db)
    values = payload.model_dump(exclude_unset=True, exclude={"label_ids"})
    project_id = values.get("project_id", task.project_id)
    assignee_id = values.get("assignee_id", task.assignee_id)
    validate_task_relations(db, project_id, assignee_id)
    for key, value in values.items():
        setattr(task, key, value)
    if payload.label_ids is not None:
        task.labels = get_labels(db, payload.label_ids)
    commit(db)
    return db.scalar(task_query().where(models.Task.id == task.id))


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DbSession) -> Response:
    db.delete(get_or_404(db, models.Task, task_id))
    commit(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def dashboard_summary(db: DbSession) -> schemas.DashboardSummary:
    status_rows = db.execute(select(models.Task.status, func.count()).group_by(models.Task.status)).all()
    return schemas.DashboardSummary(
        projects=db.scalar(select(func.count()).select_from(models.Project)) or 0,
        members=db.scalar(select(func.count()).select_from(models.Member)) or 0,
        tasks=db.scalar(select(func.count()).select_from(models.Task)) or 0,
        labels=db.scalar(select(func.count()).select_from(models.Label)) or 0,
        tasks_by_status={task_status: count for task_status, count in status_rows},
    )