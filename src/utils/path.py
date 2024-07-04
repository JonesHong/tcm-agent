# 获取项目根目录
import os 
import sys


def trim_path(path):
    return os.path.normpath(os.path.abspath(path))

THIS_DIR = os.path.dirname(__file__)
UTIL_DIR = os.path.dirname(THIS_DIR)
ROOT_DIR = os.path.dirname(UTIL_DIR)

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


def get_services(base_dir, services_dir):
    services = {}
    for service_name in os.listdir(services_dir):
        service_path = os.path.join(services_dir, service_name)
        if os.path.isdir(service_path) and "main.py" in os.listdir(service_path):
            relative_path = os.path.join("src", "services", service_name, "main.py").replace("/", "\\")
            services[service_name] = relative_path
    print(f"get_services: \n{services}\n")
    return services
