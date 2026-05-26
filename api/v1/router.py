from fastapi import APIRouter
from config.config import config
from api.v1.endpoints.users import users_router
from api.v1.endpoints.step_history import step_history_router

router = APIRouter(prefix=config["endpoint"]["prefix"])

router.include_router(users_router)
router.include_router(step_history_router)