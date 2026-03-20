import sentry_sdk
from app.api.main import api_router
from app.core.config import settings
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    if exc.status_code == 404:
        print(f"404 ошибка на пути: {request.url.path}")
        print(f"Метод: {request.method}")
        print(f"Детали: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail2": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Логируем полную информацию об ошибке для отладки
    print(f"500 ошибка на пути: {request.url.path}")
    print(f"Метод: {request.method}")
    print(f"Тип ошибки: {type(exc).__name__}")
    print(f"Сообщение: {str(exc)}")
    print("Трассировка:")
    
    # Формируем подробное сообщение об ошибке
    error_message = f"{type(exc).__name__}: {str(exc)}"
    
    # В зависимости от окружения можно возвращать разную детализацию
    if settings.ENVIRONMENT == "production":
        # В продакшене показываем только тип ошибки
        error_detail = f"Internal server error: {type(exc).__name__}"
    else:
        # В разработке показываем полную информацию
        error_detail = error_message
    
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "error": error_detail,
        },
    )
