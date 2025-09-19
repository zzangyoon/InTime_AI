from fastapi import FastAPI, UploadFile, File 
from app.api.face_detect_api import router as face_detection_router
from app.api.ocr_api import router as ocr_router

# Server
app = FastAPI(
    title = "InTime_AI",
    description = "근태 관리 시스템",
    version = "1.0.0"
)

# router 등록
print("start App router")
app.include_router(face_detection_router)
app.include_router(ocr_router)
