import datetime
from loguru import logger

logger.add('logs/log_{time}.log', rotation=datetime.timedelta(days=1))


def print_log(s, level: str = 'INFO'):
    level = level.upper()
    logger.log(level, s)
