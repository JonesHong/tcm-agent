# 获取项目根目录
import os 
import sys


def trim_path(path):
    return os.path.normpath(os.path.abspath(path))

THIS_DIR = trim_path(os.path.dirname(__file__))
UTIL_DIR = trim_path(os.path.dirname(THIS_DIR))
ROOT_DIR = trim_path(os.path.dirname(UTIL_DIR))

def add_dir_to_sys_path_be_levels_up(levels_up=1):
    global THIS_DIR
    try:
        TARGET_DIR = os.path.join(THIS_DIR, *['..']*levels_up)
        TARGET_DIR_TRIM = trim_path(TARGET_DIR)
        add_dir_to_sys_path(TARGET_DIR_TRIM)
    except Exception as e:
        print(f"Error adding directory to sys.path: {e}")
        
        
def add_dir_to_sys_path(dir):
    try:
        trimmed_dir = trim_path(dir)
        if trimmed_dir not in sys.path:
            sys.path.append(trimmed_dir)
    except Exception as e:
        print(f"Error adding directory to sys.path: {e}")
