import json
import os
import requests
import zipfile
import shutil
from io import BytesIO
from dateutil import parser

# 读取 JSON 文件中的项目数据
def load_packages(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# 将项目数据写回 JSON 文件
def save_packages(file_path, packages):
    with open(file_path, 'w') as file:
        json.dump(packages, file, indent=4)

# 获取最新的提交时间
def get_latest_commit_time(git_url):
    api_url = git_url.replace("https://github.com/", "https://api.github.com/repos/")
    if "/tree/" in api_url:
        api_url = api_url.split("/tree/")[0]
    
    commits_url = f"{api_url}/commits"
    response = requests.get(commits_url)
    
    if response.status_code == 200:
        commits = response.json()
        latest_commit_date = parser.parse(commits[0]['commit']['committer']['date'])
        return int(latest_commit_date.timestamp() * 1000)
    else:
        print(f"Error fetching commits from {git_url}")
        return None

# 获取最新的发布信息
def get_latest_release(git_url):
    api_url = git_url.replace("https://github.com/", "https://api.github.com/repos/")
    if "/tree/" in api_url:
        api_url = api_url.split("/tree/")[0]
    
    releases_url = f"{api_url}/releases/latest"
    response = requests.get(releases_url)
    
    if response.status_code == 200:
        release = response.json()
        return release['tag_name'], release['body']
    elif response.status_code == 404:
        return None, None
    else:
        print(f"Error fetching releases from {git_url}")
        return None, None

# 下载并解压缩文件到指定路径
def download_and_extract_zip(url, extract_to):
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            # 获取压缩包中的根目录名称，并将内容提取到目标路径
            root_dir = zip_ref.namelist()[0].split('/')[0]
            for member in zip_ref.namelist():
                member_path = os.path.join(extract_to, os.path.relpath(member, root_dir))
                if member.endswith('/'):
                    os.makedirs(member_path, exist_ok=True)
                else:
                    with zip_ref.open(member) as source, open(member_path, "wb") as target:
                        shutil.copyfileobj(source, target)
        print(f"Downloaded and extracted to {extract_to}")
    else:
        print(f"Failed to download zip file from {url}")

# 更新项目
def update_packages(packages, json_file_path):
    for project in packages:
        if not project.get('autoUpdate', False):
            print(f"Skipping {project['name']} as autoUpdate is set to false.")
            continue  # 跳过不需要自动更新的项目

        print(f"\nChecking for updates on {project['name']}...")
        latest_commit_time = get_latest_commit_time(project['url'])
        
        if latest_commit_time and latest_commit_time > project['lastUpdateTime']:
            print(f"A new update is available for {project['name']}.")

            latest_release, release_notes = get_latest_release(project['url'])
            if latest_release:
                print(f"Latest release: {latest_release}")
                print(f"Release notes: {release_notes}")
            else:
                print("No release information available.")
            
            user_input = input(f"Do you want to update {project['name']}? (y/n): ")

            if user_input.lower() == 'y':
                # 删除旧文件夹（如果存在）
                if os.path.exists(project['name']):
                    shutil.rmtree(project['name'])
                
                # 构建下载链接
                download_url = f"{project['url']}/archive/refs/heads/main.zip"
                download_and_extract_zip(download_url, project['name'])

                # 更新项目的 lastUpdateTime 和 releases 信息
                project['lastUpdateTime'] = latest_commit_time
                project['releases'] = latest_release if latest_release else project['releases']
                print(f"{project['name']} has been updated.\n")
            else:
                print(f"{project['name']} was not updated.\n")
        else:
            print(f"{project['name']} is up-to-date.\n")
    
    # 更新 JSON 文件中的项目数据
    save_packages(json_file_path, packages)

if __name__ == "__main__":
    # 定义 JSON 文件路径
    json_file_path = 'packages.json'

    # 加载项目数据
    packages = load_packages(json_file_path)

    # 执行更新检查
    update_packages(packages, json_file_path)
