import __init__
import sys
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime, timezone

import os
import httpx
import json

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# # 添加项目根目录到 sys.path
# sys.path.append(project_root)

from models.schemas.fastapi import LoginInModel, QuanxiRequest
from .utils import get_new_token, get_token, get_unique_filename, load_token, config, process_file

api_router = APIRouter()

UPLOAD_DIR = __init__.trim_path(os.path.join(__init__.ROOT_DIR, "uploads"))
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@api_router.get("/")
async def read_main():
    return {"message": "Hello from FastAPI"}

@api_router.get("/account/login")
async def get_account_login():
    try:
        token = await get_new_token()
        return {"token": token}
    except Exception as e:
        print(f"登入失敗: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@api_router.get("/login", response_model=dict)
async def post_login():
    try:
        token = await get_token()
        return {"token": token}
    except Exception as e:
        print(f"登入失敗: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    
@api_router.post("/agency/quanxi", response_model=dict)
async def quanxi_analysis_api(
    age: int = Form(35),
    appkey: str = Form('v1eaevl3dum3i9g46ar5c8cghd8cle7t'),
    file: UploadFile = File(...),
    male: int = Form(...),
    methodName: Optional[str] = Form("quanxi"),
    confidence: Optional[float] = Form(0.7),
    desease: Optional[str] = Form(None),
    frontCamera: Optional[int] = Form(1),
    imageUrl: Optional[str] = Form("http://"),
    isYuejin: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    timestamp: Optional[str] = Form(datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'))
):
    try:
        file.file.seek(0)
        uploaded_file_data = await file.read()
        result = await process_file(
            uploaded_file_data,
            file.filename,
            age,
            appkey,
            male,
            methodName,
            confidence,
            desease,
            frontCamera,
            imageUrl,
            isYuejin,
            name,
            timestamp
        )
        return JSONResponse(content=result)
    except Exception as e:
        print(f"全息舌像分析發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")
    
async def quanxi_analysis_local_file(
    file_path: str,
    age: int = 35,
    appkey: str = "v1eaevl3dum3i9g46ar5c8cghd8cle7t" ,
    male: int = 1,
    methodName: str = "quanxi",
    confidence: float = 0.7,
    desease: Optional[str] = None,
    frontCamera: int = 1,
    imageUrl: str = "http://",
    isYuejin: Optional[int] = None,
    name: Optional[str] = None,
    timestamp: Optional[str] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
):
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        result = await process_file(
            file_data,
            os.path.basename(file_path),
            age,
            appkey,
            male,
            methodName,
            confidence,
            desease,
            frontCamera,
            imageUrl,
            isYuejin,
            name,
            timestamp
        )
        return result
    except HTTPException as e:
        print(f"處理檔案發生錯誤: {e.detail}")
        raise
    except Exception as e:
        print(f"處理本地檔案發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")


# @api_router.post("/agency/quanxi", response_model=dict)
# async def quanxi_analysis(
#     age: int = Form(35),
#     appkey: str = Form(...),
#     file: UploadFile = File(...),
#     male: int = Form(...),
#     methodName: Optional[str] = Form("quanxi"),
#     confidence: Optional[float] = Form(0.7),
#     desease: Optional[str] = Form(None),
#     frontCamera: Optional[int] = Form(1),
#     imageUrl: Optional[str] = Form("http://"),
#     isYuejin: Optional[int] = Form(None),
#     name: Optional[str] = Form(None),
#     timestamp: Optional[str] = Form(datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'))
# ):
#     try:
#         file.file.seek(0)
#         uploaded_file_data = await file.read()

#         QUANXI_DIR = os.path.join(UPLOAD_DIR, "quanxi")
#         if not os.path.exists(QUANXI_DIR):
#             os.makedirs(QUANXI_DIR)

#         file_path_on_disk = os.path.join(QUANXI_DIR, file.filename)
#         unique_file_path = get_unique_filename(file_path_on_disk, uploaded_file_data)

#         if unique_file_path is None:
#             json_filename = os.path.splitext(file_path_on_disk)[0] + ".json"
#             if os.path.exists(json_filename):
#                 with open(json_filename, "r", encoding="utf-8") as json_file:
#                     previous_result = json.load(json_file)
#                     print("調取之前的舌診記錄")
#                     return JSONResponse(content={"message": "上傳的照片已存在且內容相同", "previous_result": previous_result}, status_code=200)

#         print("開始全息舌像分析")
#         url = "https://api.aikanshe.com/agency/quanxi"
#         headers = {
#             "Authorization": f"Bearer {await get_token()}",
#             "appId": config['AIKanShe']['appId']
#         }
#         data = QuanxiRequest(
#             age= age,
#             appkey= appkey,
#             male= male,
#             methodName= methodName,
#             confidence= confidence,
#             desease= desease,
#             frontCamera= bool(frontCamera),
#             imageUrl= imageUrl,
#             isYuejin= isYuejin,
#             name= name,
#             timestamp= timestamp
#         ).model_dump()
        
#         files = {"file": (file.filename, file.file, file.content_type)}
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, headers=headers, data=data, files=files)
#             if response.status_code != 200:
#                 raise HTTPException(status_code=response.status_code, detail="Analysis failed")
#             result = response.json()

#         with open(unique_file_path, "wb") as buffer:
#             buffer.write(uploaded_file_data)
#         print(f"保存全新照片: {unique_file_path}")

#         json_filename = os.path.splitext(unique_file_path)[0] + ".json"
#         json_data = {
#             "original_filename": file.filename,
#             "upload_date": datetime.now().strftime("%Y%m%d%H%M%S%f"),
#             "analysis_result": result
#         }
#         with open(json_filename, "w", encoding="utf-8") as json_file:
#             json.dump(json_data, json_file, ensure_ascii=False, indent=4)
#         print(f"創建 JSON 文件: {json_filename}")

#         return JSONResponse(content=result)
#     except Exception as e:
#         print(f"全息舌像分析發生錯誤: {e}")
#         raise HTTPException(status_code=500, detail="Analysis failed")
