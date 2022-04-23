import functools

from loguru import logger


def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


def setup_logger():
    import datetime
    import os

    from pygelf import GelfTcpHandler

    logger.add(
        "logs/log_{time}.log",
        rotation=datetime.timedelta(days=1),
        retention=30,
        level="INFO",
    )
    # Send logs to a remote server
    if "REMOTE_SYSLOG_IP" in os.environ:
        logger.add(
            GelfTcpHandler(
                host=os.environ["REMOTE_SYSLOG_IP"],
                port=os.environ["REMOTE_SYSLOG_PORT"],
            ),
            level="INFO",
        )
    else:
        logger.warning(
            "no REMOTE_SYSLOG_IP configured, will write logs only to STDOUT and logs/log_*.log"
        )
