# 获取项目根目录
import os 
import sys


def trim_path(path):
    return os.path.normpath(os.path.abspath(path))

THIS_DIR = trim_path(os.path.dirname(__file__))
ROOT_DIR = trim_path(os.path.dirname(THIS_DIR))

        
def add_dir_to_sys_path(dir):
    try:
        trimmed_dir = trim_path(dir)
        if trimmed_dir not in sys.path:
            sys.path.append(trimmed_dir)
    except Exception as e:
        print(f"Error adding directory to sys.path: {e}")

add_dir_to_sys_path(ROOT_DIR)
# print(ROOT_DIR)




