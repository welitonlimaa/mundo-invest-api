import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.api.middleware.api_key import ApiKeyMiddleware
from app.api.routes.clientes import router as clientes_router
from app.api.routes.webhooks import router as webhooks_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.env == "local":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Mundo Invest API",
    version="0.1.0",
    lifespan=lifespan,
)

PUBLIC_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
}

app.add_middleware(
    ApiKeyMiddleware,
    public_paths=PUBLIC_PATHS,
)

app.include_router(clientes_router)
app.include_router(webhooks_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "environment": settings.env,
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = exc.errors()
    first = errors[0] if errors else {}

    field = " -> ".join(str(loc) for loc in first.get("loc", [])[1:])

    msg = first.get("msg", "Erro de validação")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": f"Campo '{field}': {msg}",
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception("Unhandled exception", exc_info=exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "Erro interno do servidor",
        },
    )


handler = Mangum(app, lifespan="off")
