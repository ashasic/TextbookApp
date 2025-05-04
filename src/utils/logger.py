import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Only add handler once
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        # Ensure logs directory exists
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, "application.log")
        handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
        )
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
        handler.setFormatter(fmt)

        logger.addHandler(handler)

    return logger
