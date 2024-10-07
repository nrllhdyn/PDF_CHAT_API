import time
from functools import wraps
from app.utils.logger import logger

class PerformanceMetrics:
    @staticmethod
    def measure_time(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Function {func.__name__} took {execution_time:.4f} seconds to execute")
            return result
        return wrapper

    @staticmethod
    def log_response_length(response: str):
        response_length = len(response)
        logger.info(f"Response length: {response_length} characters")