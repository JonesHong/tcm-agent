# 获取项目根目录
import os 
import sys


def trim_path(path):
    return os.path.normpath(os.path.abspath(path))

THIS_DIR = trim_path(os.path.dirname(__file__))
UTIL_DIR = trim_path(os.path.dirname(THIS_DIR))
ROOT_DIR = trim_path(os.path.dirname(UTIL_DIR))

        
def add_dir_to_sys_path(dir):
    try:
        trimmed_dir = trim_path(dir)
        if trimmed_dir not in sys.path:
            sys.path.append(trimmed_dir)
    except Exception as e:
        print(f"Error adding directory to sys.path: {e}")

add_dir_to_sys_path(ROOT_DIR)

from util.config.manager import ConfigManager
config = ConfigManager()
log_config = config.log

from util.log.logger import LoggerClear, init_logger
log_path = log_config.log_path if log_config.log_path else os.path.join(ROOT_DIR, "logs")
def logger_init(process_id):
    process_id = log_config.process_id if log_config.process_id else process_id
    print(process_id,log_config.process_id)
    init_logger(level=log_config.level,
    log_path = log_path,
    process_id = process_id,
    rotation = log_config.rotation)
    #啟動Log清除者
    logger_cleaner = LoggerClear(log_path=log_path, log_retention=log_config.rotation)
    logger_cleaner.start()

