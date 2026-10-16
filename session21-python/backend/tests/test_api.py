import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine

@pytest.fixture(scope="session", autouse=True)
def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["docs"] == "/docs"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}

def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text or "http_request_duration_seconds" in response.text or "# HELP" in response.text

def test_create_task():
    payload = {
        "title": "Configure EKS Ingress Controller",
        "description": "Deploy AWS Load Balancer Controller to handle ingress traffic",
        "priority": "HIGH",
        "assignee": "DevOps Engineer"
    }
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["priority"] == "HIGH"
    assert data["status"] == "TODO"
    assert "id" in data

def test_list_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_task_by_id():
    res = client.post("/api/tasks", json={"title": "Test Single Task", "priority": "LOW"})
    task_id = res.json()["id"]

    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Test Single Task"

def test_update_task():
    res = client.post("/api/tasks", json={"title": "Task To Update", "priority": "MEDIUM"})
    task_id = res.json()["id"]

    update_payload = {"status": "IN_PROGRESS", "priority": "HIGH"}
    response = client.put(f"/api/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"
    assert response.json()["priority"] == "HIGH"

def test_stats():
    response = client.get("/api/tasks/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "todo" in data
    assert "inProgress" in data
    assert "done" in data

def test_get_task_not_found():
    response = client.get("/api/tasks/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_delete_task():
    res = client.post("/api/tasks", json={"title": "Task To Delete", "priority": "LOW"})
    task_id = res.json()["id"]

    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 404
