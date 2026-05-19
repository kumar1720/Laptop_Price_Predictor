import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.utils.logger import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request basic info
        logger.info(f"---> {request.method} {request.url.path}")
        
        # Proceed with request
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        logger.info(f"<--- {request.method} {request.url.path} Completed with Status {response.status_code} in {process_time:.2f}ms")
        
        return response
