from .constants import LOG_FMT_DATE, LOG_FMT_COLOR, LOG_LVL_SUCCESS
from typing import Optional
import logging


class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter that supports ANSI color codes.

    Adapted from https://stackoverflow.com/a/384125
    """
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, style: Optional[str] = '%'):
        logging.Formatter.__init__(self, fmt, datefmt, style)

    def format(self, record: logging.LogRecord):
        log_fmt = LOG_FMT_COLOR.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt, datefmt=LOG_FMT_DATE)
        return formatter.format(record)


def logForLevel(self, message, *args, **kwargs):
    if self.isEnabledFor(LOG_LVL_SUCCESS):
        self._log(LOG_LVL_SUCCESS, message, args, **kwargs)


def logToRoot(message, *args, **kwargs):
    logging.log(LOG_LVL_SUCCESS, message, *args, **kwargs)


def get_color_logger(name: str) -> logging.Logger:
    # Add success level
    logging.addLevelName(LOG_LVL_SUCCESS, 'SUCCESS')
    setattr(logging, 'SUCCESS', LOG_LVL_SUCCESS)
    setattr(logging.getLoggerClass(), 'success', logForLevel)
    setattr(logging, 'success', logToRoot)

    # Instantiate logger
    logger = logging.getLogger(name)

    # Add color formatter
    color_handler = logging.StreamHandler()
    color_handler.setFormatter(ColorFormatter())
    logger.addHandler(color_handler)

    return logger
