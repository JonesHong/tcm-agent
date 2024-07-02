# https://betterstack.com/community/guides/logging/loguru/#getting-started-with-loguru
# https://www.readfog.com/a/1640196300205035520
# https://stackoverflow.com/questions/70977165/how-to-use-loguru-defaults-and-extra-information

import os
import time
from loguru import logger as _logger
import sys
from datetime import datetime, timedelta
from threading import Thread
# from config._enum import LogLevelEnum
logger_format = (
    # "<level>{time:YYYY-MM-DD HH:mm:ss} | {level}\t{process} | {file}:{function}:{line} - {message} </level>"
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}{process}</level> | "
    "<cyan>{file}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
_logger.configure(extra={})  # Default values
def init_logger(level = "INFO", log_path = "log", process_id = "", rotation = "20"):
    _logger.remove(0)
    _logger.add(
            f'{log_path}/[{process_id}]{datetime.now().strftime("%Y%m%d-%H%M%S")}.log', 
            format=logger_format, 
            rotation=f"{rotation}MB",  
            encoding="utf-8", 
            enqueue=True,
            # retention=f"{SystemConfig.LOG_RETENTION} days", 
            level=level
        )
    _logger.add(
            sys.stderr, 
            format=logger_format, 
            level=level,
        )

class LoggerClear:
    def __init__(self, log_path, log_retention) -> None:
         self.clear_thread = Thread(target=self.__clean_old_log_loop, args=(log_path, log_retention),daemon=True)
         self.__is_running = False

    def start(self):
        if self.__is_running:
            _logger.info(f"Logger: Already Running...!!!")
        else:
            self.clear_thread.start()
            _logger.info(f"Logger: Clear Log Thread Started...!!!")
            self.__is_running = True

    def __clean_old_log_loop(self, log_path, log_retention):
            check_path = log_path
            while True:
                current_datetime = datetime.now()
                try:
                    existing_record_list = os.listdir(check_path)
                    for file in existing_record_list:
                        if file.startswith("."):
                            continue
                        is_file = os.path.isfile(os.path.join(check_path, file))
                        is_expired_days = os.path.getctime(os.path.join(check_path, file)) < (current_datetime - timedelta(days=int(log_retention))).timestamp()
                        if is_file and is_expired_days:
                            os.remove(os.path.join(check_path, file))
                            _logger.info(f"Logger: Clean Log: {os.path.join(check_path, file)}")
                except Exception as e:
                    _logger.info(f"Logger: Clean Record Failed...!!! Exception: {str(e)}")
                finally:
                    time.sleep(60)

