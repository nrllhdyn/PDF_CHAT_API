from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils.logger import logger

async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        logger.error(f"HTTP error occurred: {exc.detail}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    except Exception as exc:
        logger.error(f"Unexpected error occurred: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )