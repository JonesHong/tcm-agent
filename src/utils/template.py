""" run_all.bat
cd "C:\Users\User\Desktop\a20-1"
::start /min "tymetro-cd-server" 0-media-server.bat
start /min "tymetro-cd-server" 1-cd-server.bat
start /min "tymetro-camera" 2-camera.bat
start /min "tymetro-stream-mic" 3-stream-mic.bat
start /min "tymetro-face-server" 4-face-server.bat
start /min "tymetro-audio-detect" 5-audio-detect.bat
start /min "tymetro-pipe_line_server" 6-pipe_line_server.bat
start /min "tymetro-asr_server" 7-asr_server.bat
start /min "tymetro-qa_server" 8-qa_server.bat
start /min "tymetro-qa_menu" qa_menu.bat
start chrome --kiosk -url "http://127.0.0.1:5173/touch-screen"
start /min "tymetro-vroid_vtuber_node" vroid_vtuber_node.bat
start /min "tymetro-vroid_node" vroid_node.bat

start /min "tymetro-unreal_node" unreal_node.bat
"""
run_all_bat=None



# 获取项目根目录
import os 
import sys

def trim_path(path):
    return os.path.normpath(os.path.abspath(path))

THIS_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.dirname(THIS_DIR)
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













