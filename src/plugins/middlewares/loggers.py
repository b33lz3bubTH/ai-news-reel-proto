import logging
import os
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from logging.handlers import TimedRotatingFileHandler
from contextvars import ContextVar

# Define context variables for tracking request_id dynamically
request_id_var = ContextVar('request_id', default='N/A')

class ContextFilter(logging.Filter):
    def filter(self, record):
        # Inject request_id into the log record dynamically
        record.request_id = request_id_var.get()
        return True

class LoggerFactory:
    def __init__(self, log_dir="/tmp"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def create_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Create Timed Rotating File Handler
        log_file = self._generate_log_file_name(name)
        file_handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=7)
        file_handler.setLevel(logging.DEBUG)

        # Define log formatter with request_id context
        formatter = logging.Formatter("%(asctime)s - %(name)s - [RequestID: %(request_id)s] - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add file and console handlers, along with context filter
        logger.addHandler(file_handler)
        logger.addFilter(ContextFilter())

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def _generate_log_file_name(self, name):
        return os.path.join(self.log_dir, f"{name}.log")


# Middleware function to set request_id in each request's context
def set_request_id(request_id):
    request_id_var.set(request_id)


# Instantiate a logger for general use
logger = LoggerFactory().create_logger("app_logger")

class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        unique_request_id = str(uuid.uuid4())  # Generate a unique request ID
        set_request_id(unique_request_id)  # Set the request ID in context
        logger.info(f"Incoming request with ID: {unique_request_id}")
        response = await call_next(request)
        logger.info(f"Completed request with ID: {unique_request_id}")
        return response
