import asyncio
import signal
import sys
import os
from typing import Optional

from fastapi.responses import JSONResponse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
import httpx
import configparser
from datetime import datetime, timedelta, timezone
from models.schemas.fastapi import LoginInModel, QuanxiRequest    # 引入 LoginInModel


# 獲取當前文件的絕對路徑
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, '../config.ini')

# 定義 token 文件路徑
TOKEN_FILE = os.path.join(base_dir, '../data/json/token_info.json')

# 讀取 config.ini 配置
config = configparser.ConfigParser()
config.read(config_path)

print(config['AIKanShe']['appId'])

# 定義保存影像和 JSON 文件的目錄
UPLOAD_DIR = os.path.join(base_dir, "../uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 保存 token 資訊
def save_token(token_data):
    print("保存 token 資訊到本地文件")
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)

# 讀取 token 資訊
def load_token():
    if not os.path.exists(TOKEN_FILE):
        print("token 文件不存在")
        return None
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            token_data['meta']['timestamp'] = datetime.fromisoformat(token_data['meta']['timestamp'])
            token_data['data']['user']['createTime'] = datetime.fromisoformat(token_data['data']['user']['createTime'])
            return token_data
    except (json.JSONDecodeError, KeyError):
        print("token 文件無效或損壞")
        return None

# 檢查 token 是否有效
def is_token_valid(token_data):
    if not token_data:
        return False
    valid = datetime.now(timezone.utc) < token_data['meta']['timestamp'] + timedelta(hours=10)
    print(f"token 是否有效: {valid}")
    return valid

# 檢查 token 是否需要刷新
def needs_refresh(token_data):
    if not token_data:
        return False
    now = datetime.now(timezone.utc)
    token_age = now - token_data['meta']['timestamp']
    refresh_needed = 10 < token_age.total_seconds() / 3600 < 20
    print(f"token 是否需要刷新: {refresh_needed}")
    return refresh_needed

# 獲取新 token
async def get_new_token():
    try:  # 新增
        print("獲取新 token")
        login_url = "https://api.aikanshe.com/account/login"
        headers = {"Content-Type": "application/json"}
        AIKanShe = config['AIKanShe']
        userKeyRes = await get_user_key()
        userKey = userKeyRes['data']['userKey']
        timestamp = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        body = LoginInModel(
            appId=AIKanShe['appId'],
            methodName="login",
            password=AIKanShe['password'],
            timestamp=timestamp,
            userKey=userKey
        ).dict()
        async with httpx.AsyncClient() as client:
            response = await client.post(login_url, json=body, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Login failed")
            data = response.json()
            data['meta']['timestamp'] = datetime.now(timezone.utc).isoformat()
            save_token(data)
            return data['data']['jwt']
    except Exception as e:  # 新增
        print(f"獲取新 token 發生錯誤: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Failed to get new token")  # 新增

# 獲取最新的 appkey
async def get_latest_appkey():
    try:  # 新增
        print("獲取最新的 appkey")
        appkey_url = "https://api.aikanshe.com/user/getAppkey"
        headers = {"Authorization": f"Bearer {await get_token()}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(appkey_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to get appkey")
            data = response.json()
            latest_appkey = max(data['data'], key=lambda x: x['createTime'])['appkey']
            return latest_appkey
    except Exception as e:  # 新增
        print(f"獲取最新的 appkey 發生錯誤: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Failed to get latest appkey")  # 新增

# 更新 appkey
async def update_appkey(old_appkey):
    try:  # 新增
        print("更新 appkey")
        update_url = "https://api.aikanshe.com/user/updateAppkey"
        headers = {"Authorization": f"Bearer {await get_token()}", "Content-Type": "application/json"}
        body = {
            "appkey": old_appkey
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(update_url, json=body, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to update appkey")
            return response.json()
    except Exception as e:  # 新增
        print(f"更新 appkey 發生錯誤: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Failed to update appkey")  # 新增

# 新增 appkey
async def add_appkey(authorization):
    try:  # 新增
        print("新增 appkey")
        url = "https://api.aikanshe.com/user/addAppkey"
        AIKanShe = config['AIKanShe']
        headers = {
            "Content-Type": "application/json",
            "appId": AIKanShe['appId'],
            "authorization": authorization,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to add appkey")
            data = response.json()
            return data
    except Exception as e:  # 新增
        print(f"新增 appkey 發生錯誤: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Failed to add appkey")  # 新增
    
# 刷新 token
async def refresh_token():
    try:  # 新增
        print("刷新 token")
        old_appkey = await get_latest_appkey()
        await update_appkey(old_appkey)
        new_token = await get_new_token()
        await add_appkey(f"Bearer {new_token}")
        return new_token
    except Exception as e:  # 新增
        print(f"刷新 token 發生錯誤: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Failed to refresh token")  # 新增

# 獲取有效的 token
async def get_token():
    try:  # 新增
        token_data = load_token()
        if is_token_valid(token_data):
            print("token 有效，使用現有的 token")
            return token_data['data']['jwt']
        elif needs_refresh(token_data):
            print("token 需要刷新")
            return await refresh_token()
        else:
            print("token 無效，需要重新獲取新 token")
            return await get_new_token()
    except Exception as e:  # 新增
        print(f"獲取 token 發生錯誤: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Failed to get token")  # 新增

# 獲取 user key
async def get_user_key():
    try:  # 新增
        print("獲取 user key")
        url = "https://api.aikanshe.com/account/login?tokenKey=get"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to get user key")
            data = response.json()
            return data
    except Exception as e:  # 新增
        print(f"獲取 user key 發生錯誤: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Failed to get user key")  # 新增


# 比較兩個文件是否相同
def are_files_identical(file1_data: bytes, file2_path: str) -> bool:
    try:
        with open(file2_path, 'rb') as file2:
            file2_data = file2.read()
            return file1_data == file2_data
    except FileNotFoundError:
        return False

# 獲取不重複的文件名
def get_unique_filename(file_path: str,uploaded_file_data) -> str:
    base, extension = os.path.splitext(file_path)
    counter = 1
    new_file_path = file_path

    while os.path.exists(new_file_path):
        if are_files_identical(uploaded_file_data, new_file_path):
            print("上傳的照片與硬碟中的照片相同")
            return None  # 如果文件內容相同，返回 None
        new_file_path = f"{base}({counter}){extension}"
        counter += 1

    return new_file_path


app = FastAPI()

@app.get("/login", response_model=dict)
async def post_login():
    try:  # 新增
        token = await get_token()
        return {"token": token}
    except Exception as e:  # 新增
        print(f"登入失敗: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Login failed")  # 新增


# AI全息舌像分析
@app.post("/agency/quanxi", response_model=dict)
async def quanxi_analysis(
    age: int = Form(35),
    appkey: str = Form(...),
    file: UploadFile = File(...),
    male: int = Form(...),
    methodName: Optional[str] = Form("quanxi"), # 全息
    confidence: Optional[float] = Form(0.7),
    desease: Optional[str] = Form(None),
    frontCamera: Optional[int] = Form(1),
    imageUrl: Optional[str] = Form("http://"),
    isYuejin: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    timestamp: Optional[str] = Form(datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'))
):
    try:  # 新增
        # 讀取上傳的影像文件
        file.file.seek(0)  # 將文件指針移動到文件的開頭
        uploaded_file_data = await file.read()

        # 定義保存影像和 JSON 文件的目錄
        QUANXI_DIR = os.path.join(UPLOAD_DIR, "./quanxi")
        if not os.path.exists(QUANXI_DIR):
            os.makedirs(QUANXI_DIR)

        file_path_on_disk = os.path.join(QUANXI_DIR, file.filename)

        # 獲取不重複的文件名
        unique_file_path = get_unique_filename(file_path_on_disk, uploaded_file_data)

        if unique_file_path is None:
            json_filename = os.path.splitext(file_path_on_disk)[0] + ".json"
            if os.path.exists(json_filename):
                with open(json_filename, "r", encoding="utf-8") as json_file:
                    previous_result = json.load(json_file)
                    print("調取之前的舌診記錄")
                    return JSONResponse(content={"message": "上傳的照片已存在且內容相同", "previous_result": previous_result}, status_code=200)

        print("開始全息舌像分析")
        url = "https://api.aikanshe.com/agency/quanxi"
        headers = {
            "Authorization": f"Bearer {await get_token()}",
            "appId": config['AIKanShe']['appId']
        }
        # 確保前端傳入的值正確轉換
        data = {
            "age": age,
            "appkey": appkey,
            "male": male,
            "methodName": methodName,
            "confidence": confidence,
            "desease": desease,
            "frontCamera": bool(frontCamera),
            "imageUrl": imageUrl,
            "isYuejin": isYuejin,
            "name": name,
            "timestamp": timestamp
        }
        files = {"file": (file.filename, file.file, file.content_type)}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Analysis failed")
            result = response.json()

        # 保存影像文件
        with open(unique_file_path, "wb") as buffer:
            buffer.write(uploaded_file_data)
        print(f"保存全新照片: {unique_file_path}")

        # 創建 JSON 文件
        json_filename = os.path.splitext(unique_file_path)[0] + ".json"
        json_data = {
            "original_filename": file.filename,
            "upload_date": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "analysis_result": result
        }
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)
        print(f"創建 JSON 文件: {json_filename}")

        return JSONResponse(content=result)
    except Exception as e:  # 新增
        print(f"全息舌像分析發生錯誤: {e}")  # 新增
        raise HTTPException(status_code=500, detail="Analysis failed")  # 新增





# 定義自訂的信號處理器來優雅地停止服務
def handle_exit(sig, frame):
    print("收到停止信號，正在停止服務...")
    for task in asyncio.all_tasks():
        task.cancel()
    loop = asyncio.get_event_loop()
    loop.stop()

# 註冊信號處理器
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

if __name__ == "__main__":
    import uvicorn
    
    # uvicorn.run(app, host="localhost", port=8000)
    
    uvicorn_config = uvicorn.Config(app, host="localhost", port=8000)
    server = uvicorn.Server(uvicorn_config)
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(server.serve())
    except (SystemExit, KeyboardInterrupt, asyncio.CancelledError):
        print("服務已停止")
    finally:
        # 確保所有異步生成器都正確關閉
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
