import pytest
from app.services import user_service
from app.models.user_model import UserCreate

def test_create_user_conflict(monkeypatch):
    # simulate existing user
    def fake_find_one(q): return {"_id": "x", "username": "bob"}
    monkeypatch.setattr(user_service.db.users, "find_one", fake_find_one)
    uc = UserCreate(username="bob", password="p", name="Bob")
    with pytest.raises(Exception):
        user_service.create_user(uc)

def test_password_hashing(monkeypatch):
    called = {}
    def fake_insert_one(doc):
        called['doc'] = doc
        class R: inserted_id = "id"
        return R()
    monkeypatch.setattr(user_service.db.users, "insert_one", fake_insert_one)
    monkeypatch.setattr(user_service.db.users, "find_one", lambda q: {"_id": "id", "username": "x"})
    uc = UserCreate(username="u1", password="pass", name="U")
    res = user_service.create_user(uc)
    assert "_id" in res
