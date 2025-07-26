import logging
import logging.handlers
import sys
import time
from pathlib import Path
from datetime import datetime
import config

def setup_logging(log_level: str = "INFO", log_to_file: bool = True):
    """
    Set up comprehensive logging for the AI Memory Bank application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file in addition to console
    """
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    
    if log_to_file:
        # Ensure log directory exists
        log_file = config.PROJECT_ROOT / "logs" / "ai_memory_bank.log"
        log_file.parent.mkdir(exist_ok=True)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        root_logger.addHandler(file_handler)
    
    # Create specific loggers for different components
    loggers = {
        'ai_memory_bank.app': logging.getLogger('ai_memory_bank.app'),
        'ai_memory_bank.embedder': logging.getLogger('ai_memory_bank.embedder'),
        'ai_memory_bank.parser': logging.getLogger('ai_memory_bank.parser'),
        'ai_memory_bank.search': logging.getLogger('ai_memory_bank.search'),
        'ai_memory_bank.storage': logging.getLogger('ai_memory_bank.storage'),
    }
    
    # Set levels for specific loggers
    for logger_name, logger in loggers.items():
        logger.setLevel(getattr(logging, log_level.upper()))
    
    # Log startup
    logging.info("Logging system initialized")
    logging.info(f"Log level: {log_level}")
    logging.info(f"Logging to file: {log_to_file}")
    
    return loggers

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(f'ai_memory_bank.{name}')

# Performance logging decorator
def log_performance(func):
    """Decorator to log function performance."""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger('performance')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"{func.__name__} completed in {duration:.3f}s")
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
            raise
    
    return wrapper

# Request logging middleware
class RequestLoggingMiddleware:
    """Middleware to log HTTP requests."""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger('requests')
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Log request
            method = scope["method"]
            path = scope["path"]
            self.logger.info(f"Request: {method} {path}")
            
            # Process request
            await self.app(scope, receive, send)
            
            # Log response time
            duration = time.time() - start_time
            self.logger.info(f"Response: {method} {path} completed in {duration:.3f}s")
        else:
            await self.app(scope, receive, send) 