# logger.py
import logging
import sys

class Trace:
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = self.setup_logger(name, level)

    def setup_logger(self, name: str, level: int) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # Formatter
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger