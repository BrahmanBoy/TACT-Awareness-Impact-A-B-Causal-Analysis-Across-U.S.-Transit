import logging, sys

def get_logger(name: str = "tact"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s - %(message)s"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger
