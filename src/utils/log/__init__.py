import logging
from types import FrameType
from typing import cast
from .logger import _logger, LoggerClear

__all__ = ["logger"]

logger = _logger


# https://blog.csdn.net/qq_51967017/article/details/134045236
def uvicorn_init_config():
    LOGGER_NAMES = ("uvicorn.asgi", "uvicorn.access", "uvicorn")

    # change handler for default uvicorn logger
    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in LOGGER_NAMES:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]

 
 
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = _logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)
 
        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1
 
        _logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage(),
        )