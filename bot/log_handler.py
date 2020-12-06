import logging, sys
from config import settings

fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


def add_handler():
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
