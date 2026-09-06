import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    # Reset in-memory storage before each test so tests don't leak state.
    app_module.tasks.clear()
    app_module.next_id = 1
    with app_module.app.test_client() as client:
        yield client


def test_get_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["title"] == "Buy milk"
    assert data["done"] is False


def test_created_task_appears_in_list(client):
    client.post("/tasks", json={"title": "Buy milk"})
    client.post("/tasks", json={"title": "Walk the dog"})

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["title"] == "Buy milk"
    assert data[1]["title"] == "Walk the dog"


def test_create_task_missing_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_task_blank_title(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_task_no_body(client):
    response = client.post("/tasks")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_complete_task(client):
    create_response = client.post("/tasks", json={"title": "Buy milk"})
    task_id = create_response.get_json()["id"]

    response = client.patch(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == task_id
    assert data["done"] is True

    list_response = client.get("/tasks")
    assert list_response.get_json()[0]["done"] is True


def test_complete_task_not_found(client):
    response = client.patch("/tasks/999/complete")
    assert response.status_code == 404
    assert "error" in response.get_json()
