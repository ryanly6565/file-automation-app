import logging
from pathlib import Path

def get_logger(log_file: Path = Path("logs/automation.log")) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("file_automation")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(log_file)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger