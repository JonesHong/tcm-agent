# run_service.py
import asyncio
import subprocess
import sys
import os
from src.utils.path import get_services

# 定义目录
ROOT_DIR = os.path.dirname(__file__)
SERVICES_DIR = os.path.join(ROOT_DIR, "src", "services")

def run_service(service_name):
    services = get_services(ROOT_DIR, SERVICES_DIR)
    print(services)

    if service_name in services:
        subprocess.run([sys.executable, services[service_name]])
    else:
        print(f"Service {service_name} not found.")

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print("Usage: python run_service.py [service_name]")
        else:
            run_service(sys.argv[1])
    except (SystemExit, KeyboardInterrupt, asyncio.CancelledError):
        print("收到停止訊號")
    finally:
        print("服務已停止")
