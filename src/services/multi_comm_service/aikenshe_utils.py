import __init__
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Optional
import httpx
from fastapi import HTTPException

from src.schemas.fastapi import LoginInModel, QuanxiRequest
from src.utils.config.manager import ConfigManager
from src.utils.log import logger
config = ConfigManager()
aikanshe_config = config.aikanshe

# 定義 token 文件路徑
TOKEN_FILE = os.path.join(__init__.ROOT_DIR, "src","data","json","token_info.json")

def save_token(token_data):
    logger.info("保存 token 資訊到本地文件")
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)

def load_token():
    if not os.path.exists(TOKEN_FILE):
        logger.info("token 文件不存在")
        return None
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            token_data['meta']['timestamp'] = datetime.fromisoformat(token_data['meta']['timestamp'])
            token_data['data']['user']['createTime'] = datetime.fromisoformat(token_data['data']['user']['createTime'])
            return token_data
    except (json.JSONDecodeError, KeyError):
        logger.info("token 文件無效或損壞")
        return None

def is_token_valid(token_data):
    if not token_data:
        return False
    valid = datetime.now(timezone.utc) < token_data['meta']['timestamp'] + timedelta(hours=10)
    logger.info(f"token 是否有效: {valid}")
    return valid

def needs_refresh(token_data):
    if not token_data:
        return False
    now = datetime.now(timezone.utc)
    token_age = now - token_data['meta']['timestamp']
    refresh_needed = 10 < token_age.total_seconds() / 3600 < 20
    logger.info(f"token 是否需要刷新: {refresh_needed}")
    return refresh_needed

async def get_new_token():
    try:
        logger.info("獲取新 token")
        login_url = "https://api.aikanshe.com/account/login"
        headers = {"Content-Type": "application/json"}
        userKeyRes = await get_user_key()
        userKey = userKeyRes['data']['userKey']
        timestamp = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        body = LoginInModel(
            appId= aikanshe_config.appid,
            methodName="login",
            password= aikanshe_config.password,
            timestamp=timestamp,
            userKey=userKey
        ).model_dump()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(login_url, json=body, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Login failed")
            data = response.json()
            data['meta']['timestamp'] = datetime.now(timezone.utc).isoformat()
            save_token(data)
            return data['data']['jwt']
    except Exception as e:
        logger.info(f"獲取新 token 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to get new token")

async def get_user_key():
    try:
        logger.info("獲取 user key")
        url = "https://api.aikanshe.com/account/login?tokenKey=get"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to get user key")
            data = response.json()
            return data
    except Exception as e:
        logger.info(f"獲取 user key 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user key")

async def get_latest_appkey():
    try:
        logger.info("獲取最新的 appkey")
        token_data = load_token()
        appkey_url = "https://api.aikanshe.com/user/getAppkey"
        headers = {
            "appId":  token_data['data']['user']['uid'],
            "authorization": token_data['data']['jwt']
            }
        async with httpx.AsyncClient() as client:
            response = await client.get(appkey_url, headers=headers)
            if response.status_code != 200:
                await get_new_token()
                raise HTTPException(status_code=response.status_code, detail="Failed to get appkey")
            data = response.json()
            if not data or 'data' not in data or not data['data']:
                raise HTTPException(status_code=500, detail="Invalid response data from getAppkey API")
            latest_appkey = max(data['data'], key=lambda x: x['createTime'])['appkey']
            return latest_appkey
    except Exception as e:
        logger.info(f"獲取最新的 appkey 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to get latest appkey")

async def update_appkey(old_appkey):
    try:
        logger.info("更新 appkey")
        token_data = load_token()
        update_url = "https://api.aikanshe.com/user/updateAppkey"
        headers = {"Authorization": f"Bearer {token_data['data']['jwt']}", "Content-Type": "application/json"}
        body = {
            "appkey": old_appkey
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(update_url, json=body, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to update appkey")
            return response.json()
    except Exception as e:
        logger.info(f"更新 appkey 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appkey")

async def add_appkey(authorization):
    try:
        logger.info("新增 appkey")
        url = "https://api.aikanshe.com/user/addAppkey"
        headers = {
            "Content-Type": "application/json",
            "appId": aikanshe_config.appid,
            "authorization": authorization,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to add appkey")
            data = response.json()
            return data
    except Exception as e:
        logger.info(f"新增 appkey 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to add appkey")

async def refresh_token():
    try:
        logger.info("刷新 token")
        old_appkey = await get_latest_appkey()
        await update_appkey(old_appkey)
        new_token = await get_new_token()
        await add_appkey(f"Bearer {new_token}")
        return new_token
    except Exception as e:
        logger.info(f"刷新 token 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh token")

async def get_token():
    try:
        token_data = load_token()
        if is_token_valid(token_data):
            logger.info("token 有效，使用現有的 token")
            return token_data['data']['jwt']
        elif needs_refresh(token_data):
            logger.info("token 需要刷新")
            return await refresh_token()
        else:
            logger.info("token 無效，需要重新獲取新 token")
            return await get_new_token()
    except Exception as e:
        logger.info(f"獲取 token 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to get token")

def are_files_identical(file1_data: bytes, file2_path: str) -> bool:
    try:
        with open(file2_path, 'rb') as file2:
            file2_data = file2.read()
            return file1_data == file2_data
    except FileNotFoundError:
        return False

def get_unique_filename(file_path: str, uploaded_file_data) -> str:
    base, extension = os.path.splitext(file_path)
    counter = 1
    new_file_path = file_path

    while os.path.exists(new_file_path):
        if are_files_identical(uploaded_file_data, new_file_path):
            logger.info("上傳的照片與硬碟中的照片相同")
            return None
        new_file_path = f"{base}({counter}){extension}"
        counter += 1

    return new_file_path

async def process_file(
    file_data: bytes,
    filename: str,
    age: int,
    appkey: str,
    male: int,
    methodName: str,
    confidence: float,
    desease: Optional[str],
    frontCamera: int,
    imageUrl: str,
    isYuejin: Optional[int],
    name: Optional[str],
    timestamp: Optional[str]
):
    try:
        UPLOAD_DIR = os.path.join(__init__.SRC_DIR, "uploads")
        QUANXI_DIR = os.path.join(UPLOAD_DIR, "quanxi")
        
        # UPLOAD_DIR = os.path.join(__init__.ROOT_DIR, "uploads")
        if not os.path.exists(QUANXI_DIR):
            os.makedirs(QUANXI_DIR)

        file_path_on_disk = os.path.join(QUANXI_DIR, filename)
        unique_file_path = get_unique_filename(file_path_on_disk, file_data)

        if unique_file_path is None:
            json_filename = os.path.splitext(file_path_on_disk)[0] + ".json"
            if os.path.exists(json_filename):
                with open(json_filename, "r", encoding="utf-8") as json_file:
                    previous_result = json.load(json_file)
                    logger.info("調取之前的舌診記錄")
                    return {"message": "上傳的照片已存在且內容相同", "previous_result": previous_result}

        logger.info("開始全息舌像分析")
        url = "https://api.aikanshe.com/agency/quanxi"
        headers = {
            "Authorization": f"Bearer {await get_token()}",
            "appId": aikanshe_config.appid
        }
        data = QuanxiRequest(
            age= age,
            appkey= appkey,
            male= male,
            methodName= methodName,
            confidence= confidence,
            desease= desease,
            frontCamera= bool(frontCamera),
            imageUrl= imageUrl,
            isYuejin= isYuejin,
            name= name,
            timestamp= timestamp
        ).model_dump()
        
        files = {"file": (filename, file_data, "application/octet-stream")}
        timeout = httpx.Timeout(30.0, read=30.0)  # 增加超時時間
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Analysis failed")
            result = response.json()

        with open(unique_file_path, "wb") as buffer:
            buffer.write(file_data)
        logger.info(f"保存全新照片: {unique_file_path}")

        json_filename = os.path.splitext(unique_file_path)[0] + ".json"
        json_data = {
            "original_filename": filename,
            "upload_date": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "analysis_result": result
        }
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)
        logger.info(f"創建 JSON 文件: {json_filename}")

        return result
    except HTTPException as e:
        logger.info(f"處理檔案發生錯誤: {e.detail}")
        raise
    except Exception as e:
        logger.info(f"處理檔案發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")
