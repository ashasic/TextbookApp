import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        os.path.join(os.getcwd(), "logs", "application.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
    )
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger
