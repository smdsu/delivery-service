from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if not request.url.path.startswith("/docs"):
            response.headers["Content-Security-Policy"] = "default-src 'self'"
            response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
