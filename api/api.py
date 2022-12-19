from fastapi import FastAPI
from api.router.user import router as user_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(user_router)
    return app
