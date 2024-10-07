import logging
import json
from datetime import datetime
from app.core.config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_record)

# Remove all handlers associated with the root logger object
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# create logger  
logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)
logger.propagate = False 

json_formatter = JSONFormatter()

# create file handler which logs even debug messages
file_handler = logging.FileHandler(settings.LOG_FILE)
file_handler.setFormatter(json_formatter)
file_handler.setLevel(settings.LOG_LEVEL)

# create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setFormatter(json_formatter)
console_handler.setLevel(settings.LOG_LEVEL)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)