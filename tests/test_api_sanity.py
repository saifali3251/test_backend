"""Sanity and E2E unit tests for Project Tracker Backend API."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Verify root / returns API metadata and docs link."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project Tracker API"
    assert data["docs"] == "/docs"


def test_health_check(client: TestClient):
    """Verify /api/health queries DB and returns status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ping(client: TestClient):
    """Verify top-level /ping returns pong without touching the DB."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


def test_project_crud_lifecycle(client: TestClient):
    """Full lifecycle: create project, read, update, and delete."""
    # 1. Create project
    create_payload = {
        "name": "Alpha Launch",
        "description": "Initial deployment of Meeseek fabric",
        "status": "planning",
    }
    create_res = client.post("/api/projects", json=create_payload)
    assert create_res.status_code == 201
    project = create_res.json()
    project_id = project["id"]
    assert project["name"] == "Alpha Launch"
    assert project["status"] == "planning"

    # 2. List projects
    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    projects = list_res.json()
    assert len(projects) >= 1
    assert any(p["id"] == project_id for p in projects)

    # 3. Get project by ID
    get_res = client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Alpha Launch"

    # 4. Update project (using valid ProjectStatus: 'active')
    patch_payload = {"status": "active", "description": "Running strikes"}
    patch_res = client.patch(f"/api/projects/{project_id}", json=patch_payload)
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "active"
    assert updated["description"] == "Running strikes"

    # 5. Delete project
    del_res = client.delete(f"/api/projects/{project_id}")
    assert del_res.status_code == 204

    # 6. Verify 404 after deletion
    not_found_res = client.get(f"/api/projects/{project_id}")
    assert not_found_res.status_code == 404


def test_member_and_task_workflow(client: TestClient):
    """Verify creating a member, project, task, and assigning the member."""
    # 1. Create project
    proj_res = client.post("/api/projects", json={"name": "Beta Testing", "status": "active"})
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Create member
    member_res = client.post(
        "/api/members",
        json={"name": "Alice Engineer", "email": "alice@aibuildercup.io", "role": "Lead Engineer"},
    )
    assert member_res.status_code == 201
    member_id = member_res.json()["id"]

    # 3. Create label
    label_res = client.post("/api/labels", json={"name": "agentic", "color": "#10b981"})
    assert label_res.status_code == 201
    label_id = label_res.json()["id"]

    # 4. Create task attached to project, member, and label
    task_payload = {
        "title": "Build debounced webhook handler",
        "description": "Handle rapid GitHub merges",
        "status": "todo",
        "priority": "high",
        "project_id": proj_id,
        "assignee_id": member_id,
        "label_ids": [label_id],
    }
    task_res = client.post("/api/tasks", json=task_payload)
    assert task_res.status_code == 201
    task_data = task_res.json()
    assert task_data["title"] == "Build debounced webhook handler"
    assert task_data["project_id"] == proj_id
    assert task_data["assignee_id"] == member_id
    assert len(task_data["labels"]) == 1

    # 5. Verify task appears in project task query
    tasks_res = client.get(f"/api/tasks?project_id={proj_id}")
    assert tasks_res.status_code == 200
    assert len(tasks_res.json()) == 1

    # 6. Verify dashboard summary endpoint returns counts
    summary_res = client.get("/api/dashboard/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["projects"] >= 1
    assert summary["members"] >= 1
    assert summary["tasks"] >= 1
    assert summary["labels"] >= 1

