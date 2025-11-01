# backend/app/tests/unit/test_dish_unit.py
import pytest
from app.services import dish_service
from app.models.dish_model import DishCreate

def test_create_dish_validation(monkeypatch):
    dc = DishCreate(name="", restaurant="", price=0)
    with pytest.raises(Exception):
        dish_service.create_dish(dc)

def test_conflict_dish(monkeypatch):
    def fake_find_one(q):
        return {"name":"D","restaurant":"R"}
    monkeypatch.setattr(dish_service.db.dishes, "find_one", fake_find_one)
    dc = DishCreate(name="D", restaurant="R", price=5)
    with pytest.raises(Exception):
        dish_service.create_dish(dc)
