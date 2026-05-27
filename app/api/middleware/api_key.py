from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, public_paths: set[str] | None = None):
        super().__init__(app)
        self.public_paths = public_paths or set()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.public_paths:
            return await call_next(request)

        api_key = request.headers.get("x-api-key")

        if api_key != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "unauthorized",
                    "message": "API Key inválida",
                },
            )

        return await call_next(request)
