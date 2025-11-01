from app.db import db
from bson.objectid import ObjectId
from app.models.exception_model import NotFoundException, BadRequestException, DatabaseException, ConflictException
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _strip_password(doc: dict) -> dict:
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    doc.pop("password", None)
    return doc

def create_user(user_create):
    # enforce unique username globally
    existing = db.users.find_one({"username": user_create.username})
    if existing:
        raise ConflictException(detail="Username already taken")
    hashed = pwd_ctx.hash(user_create.password)
    doc = user_create.model_dump()
    doc["password"] = hashed
    try:
        res = db.users.insert_one(doc)
        created = db.users.find_one({"_id": res.inserted_id})
        return _strip_password(created)
    except Exception as e:
        raise DatabaseException(message=f"Failed to create user: {e}")

def login_user(username: str, password: str):
    user = db.users.find_one({"username": username})
    if not user or not pwd_ctx.verify(password, user.get("password", "")):
        raise BadRequestException(message="Invalid username or password")
    # demo token: user id
    return {"access_token": str(user["_id"]), "token_type": "bearer"}

def get_user_by_id(user_id: str):
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise NotFoundException(name="Invalid user id")
    user = db.users.find_one({"_id": obj})
    if not user:
        raise NotFoundException(name="User not found")
    return _strip_password(user)

def get_user_by_username(username: str):
    user = db.users.find_one({"username": username})
    if not user:
        raise NotFoundException(name="User not found")
    return _strip_password(user)

def update_user(user_id: str, update_data: dict):
    if not update_data:
        raise BadRequestException(message="No fields to update")
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise NotFoundException(name="Invalid user id")
    db.users.update_one({"_id": obj}, {"$set": update_data})
    updated = db.users.find_one({"_id": obj})
    return _strip_password(updated)

def delete_user(user_id: str):
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise NotFoundException(name="Invalid user id")
    res = db.users.delete_one({"_id": obj})
    if res.deleted_count == 0:
        raise NotFoundException(name="User not found")
    return
