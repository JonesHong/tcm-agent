import __init__
import os
from fastapi import APIRouter, FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timezone

from src.utils.log import logger
from src.services.multi_comm_service.aikenshe_utils import get_new_token, get_token,  process_file

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_router = APIRouter()

# FastAPI 路由
app.include_router(api_router)
UPLOAD_DIR = os.path.join(__init__.SRC_DIR, "uploads")
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
        logger.info(f"登入失敗: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@api_router.get("/login", response_model=dict)
async def post_login():
    try:
        token = await get_token()
        return {"token": token}
    except Exception as e:
        logger.info(f"登入失敗: {e}")
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
        logger.info(f"全息舌像分析發生錯誤: {e}")
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
        logger.info(f"處理檔案發生錯誤: {e.detail}")
        raise
    except Exception as e:
        logger.info(f"處理本地檔案發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")

