from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from app.utils.logger import logger
from time import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    # max 100 request in 60 second
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()

        if client_ip not in self.clients:
            self.clients[client_ip] = []

        request_times = self.clients[client_ip]
        request_times = [t for t in request_times if current_time - t < self.window]

        if len(request_times) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"}
                )

        request_times.append(current_time)
        self.clients[client_ip] = request_times

        return await call_next(request)