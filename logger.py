import logging
import os
import sys
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler


class ThreadContextFilter(logging.Filter):
    """
    This filter adds thread information to log records
    """

    def filter(self, record):
        record.threadid = threading.get_ident()
        record.threadname = threading.current_thread().name
        return True


def setup_logger(name='amazon_scraper'):
    """
    Setup logger with thread information and rotating file handler
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create formatter with thread information
    formatter = logging.Formatter(
        '%(asctime)s - [%(threadname)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create rotating file handler
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'scraper_{current_time}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Add thread context filter
    thread_filter = ThreadContextFilter()
    file_handler.addFilter(thread_filter)
    console_handler.addFilter(thread_filter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Create global logger instance
logger = setup_logger()