from app.api.routes import (
    agent_point,
    employee,
    grade,
    location,
    login,
    priority,
    private,
    role,
    task,
    task_status,
    task_type,
    users,
    utils,
)
from app.core.config import settings
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(agent_point.router)
api_router.include_router(grade.router)
api_router.include_router(location.router)
api_router.include_router(priority.router)
api_router.include_router(role.router)
api_router.include_router(task.router)
api_router.include_router(task_status.router)
api_router.include_router(task_type.router)
api_router.include_router(users.router)
api_router.include_router(employee.router)
api_router.include_router(utils.router)


if settings.ENVIRONMENT == "local":
    # api_router.include_router(private.router)
    pass
