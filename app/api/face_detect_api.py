# Controller
from fastapi import APIRouter, UploadFile, File, Form
from app.services.face_detect_service import face_detections_from_images
from app.core.face_detect import face_recognition

router = APIRouter()

############################
# 이미지파일 리스트
############################
@router.post("/detect_face")
async def detect_face(files: list[UploadFile] = File(...), mode: str = Form("check_in")):
    print(f"detect_face start :::::::::::::::::: {files} ::::::::: {mode}")
    mp_results = await face_detections_from_images(files, mode)  # mediapipe
    return mp_results


############################
# face_recognition lib
############################
@router.post("/whoami")
async def face_recognitions(file: UploadFile=File(...), mode: str = Form("check_in")):
    print(f"face_recognitions :::::::::::::::::: {file} ::::::::: {mode}")
    fc_recog = await face_recognition.whoami(file, mode)
    return fc_recog
    
    
