import configparser
import os
from src.utils.path import get_services


# 定义目录和 Conda 环境名称
ROOT_DIR = os.path.dirname(__file__)
SERVICES_DIR = os.path.join(ROOT_DIR, "src", "services")
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
conda_env = "tcm-agent"

 
config_path = os.path.join(ROOT_DIR, "config", "config.ini")
# 创建配置解析器对象
config = configparser.ConfigParser()

# 读取配置文件
config.read(config_path,encoding='utf-8')
minimized_bat = config.getboolean('System','minimized_bat')

# 模板字符串
template = """cd {ROOT_DIR} && conda activate {conda_env} && ^
python .\{service_path}
"""

print("= = = START = = =\n")
# 获取 services 字典
services = get_services(ROOT_DIR, SERVICES_DIR)

# 确保脚本目录存在
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# 生成 .bat 文件
for service_name, service_path in services.items():
    bat_content = template.format(ROOT_DIR=ROOT_DIR, conda_env=conda_env, service_path=service_path)
    bat_file_path = os.path.join(SCRIPTS_DIR, f"{service_name}.bat")
    with open(bat_file_path, "w") as bat_file:
        bat_file.write(bat_content)

    print(f"+ {service_name}.bat created successfully.")

print("= Batch files created successfully.\n")

# 生成 run_all_service.bat
run_all_content = f'cd "{ROOT_DIR}"\n'
for service_name in services.keys():
    run_all_content += f'start {" /min" if minimized_bat else ""} "tcm-{service_name.replace('_service','')}" scripts\\{service_name}.bat\n'

    # if minimized_bat:
    #     run_all_content += f'start /min "{service_name}" scripts\\{service_name}.bat\n'
    # else:
    #     run_all_content += f'start  "{service_name}" scripts\\{service_name}.bat\n'

run_all_file_path = os.path.join(SCRIPTS_DIR, "run_all_services.bat")
with open(run_all_file_path, "w") as run_all_file:
    run_all_file.write(run_all_content)

print("+ run_all_service.bat created successfully.")

print("\n= = = DONE = = =")
