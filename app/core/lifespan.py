from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.face_detect_service import create_face_detector, set_face_detector

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작시 Mediapipe 모델 생성
    print("!!! lifespan start")
    detector = create_face_detector()
    set_face_detector(detector)
    print("!!! lifespan end")

    yield
    
    # 앱 종료시