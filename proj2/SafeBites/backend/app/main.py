from fastapi import FastAPI
from SafeBites.backend.app.routers import restaurant_router, dish_router
from app.services.exception_service import register_exception_handlers

app = FastAPI(title="SafeBites")

app.include_router(restaurant_router.router)
app.include_router(dish_router.router)

register_exception_handlers(app)

@app.get("/")
def root():
    return {"message":"Welcome to SafeBites API"}

