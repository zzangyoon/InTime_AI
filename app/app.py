from fastapi import FastAPI, UploadFile, File 
from app.api.face_detect_api import router as face_detection_router
from app.api.ocr_api import router as ocr_router

# Server
app = FastAPI()

# router 등록
print("start App router")
app.include_router(face_detection_router)
app.include_router(ocr_router)
