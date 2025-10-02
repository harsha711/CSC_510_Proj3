import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_restaurant():
    return {
        "name": "Testaurant",
        "address": "123 Test St",
        "phone": "123-456-7890",
        "cuisine": "Test Cuisine"
    }

def test_create_restaurant(sample_restaurant):
    response = client.post("/restaurants/",json=sample_restaurant)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Testaurant"
    assert "id" in data

def test_list_restaurants():
    response = client.get("/restaurants/")
    assert response.status_code == 200
    assert isinstance(response.json(),list)