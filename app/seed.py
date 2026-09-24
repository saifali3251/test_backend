"""One-time baseline seed — a few sample projects/tasks so a freshly struck
workspace shows a populated UI instead of an empty one.

Idempotent: no-ops if any project already exists, so re-running (or a golden
rebuild finding an already-seeded DB) is safe.

Run with: python -m app.seed
"""

from __future__ import annotations

from datetime import date, timedelta

from app.database import SessionLocal
from app.models import Label, Member, Project, Task


def seed() -> None:
    with SessionLocal() as db:
        if db.query(Project).first() is not None:
            print("seed: projects already exist, skipping")
            return

        alice = Member(name="Alice Chen", email="alice@example.com", role="Engineer")
        bob = Member(name="Bob Nguyen", email="bob@example.com", role="Designer")
        db.add_all([alice, bob])
        db.flush()

        bug = Label(name="bug", color="#dc2626")
        feature = Label(name="feature", color="#2563eb")
        db.add_all([bug, feature])
        db.flush()

        project = Project(
            name="Fieldwork Launch",
            description="Get the project tracker into shape for its first users.",
            status="active",
        )
        db.add(project)
        db.flush()

        db.add_all(
            [
                Task(
                    title="Set up CI pipeline",
                    description="Run backend + frontend tests on every push.",
                    status="in_progress",
                    priority="high",
                    due_date=date.today() + timedelta(days=3),
                    project_id=project.id,
                    assignee_id=alice.id,
                    labels=[feature],
                ),
                Task(
                    title="Fix dashboard summary rounding",
                    description="Percentages on the dashboard don't add up to 100.",
                    status="todo",
                    priority="medium",
                    due_date=date.today() + timedelta(days=7),
                    project_id=project.id,
                    assignee_id=bob.id,
                    labels=[bug],
                ),
            ]
        )
        db.commit()
        print("seed: inserted 1 project, 2 members, 2 labels, 2 tasks")


if __name__ == "__main__":
    seed()
