# 获取项目根目录
import os 
import sys

def trim_path(path):
    return os.path.normpath(os.path.abspath(path))

THIS_DIR = os.path.dirname(__file__)
SERVICES_DIR = os.path.dirname(THIS_DIR)
SRC_DIR = os.path.dirname(SERVICES_DIR)
ROOT_DIR = os.path.dirname(SRC_DIR)

        
def add_dir_to_sys_path(dir):
    try:
        trimmed_dir = trim_path(dir)
        if trimmed_dir not in sys.path:
            sys.path.append(trimmed_dir)
    except Exception as e:
        print(f"Error adding directory to sys.path: {e}")

add_dir_to_sys_path(ROOT_DIR)

        
# 获取当前文件的完整文件名
CURRENT_FILE_NAME = lambda file: os.path.basename(file)
# 分离文件名和扩展名
FILE_NAME_WITHOUT_EXTENSION = lambda file: os.path.splitext(CURRENT_FILE_NAME(file))[0]
# 获取当前文件所在的目录名称
FOLDER_NAME = os.path.basename(THIS_DIR)

from src.utils.log.logger import LoggerClear, init_logger
def logger_start(file=None,folder=FOLDER_NAME):
    if file is not None:
        init_logger(process_id = FILE_NAME_WITHOUT_EXTENSION(file))
    elif folder is not None:
        init_logger(process_id = folder)
    #啟動Log清除者
    logger_cleaner = LoggerClear()
    logger_cleaner.start()













