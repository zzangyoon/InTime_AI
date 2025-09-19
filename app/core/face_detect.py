# mediapipe 모델 객체 생성 / 보관
# FaceRecognition

import mediapipe as mp
import pickle
from app.services.face_recognition_service import FaceRecognition
from app.core.config import RECOGNITION_MODEL

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

face_detector = mp_face_detection.FaceDetection(
    model_selection=0, 
    min_detection_confidence=0.5
)

# FaceRecognition - Full Model
# with open(RECOGNITION_MODEL, "rb") as f:
#     face_recognition = pickle.load(f)


# FaceRecognition - 가중치만 저장한 Model
with open("app/models/FRModel_20250918_state.pkl", "rb") as f:
    model_data = pickle.load(f)
face_recognition = FaceRecognition()
face_recognition._encodings = model_data["_encodings"]
face_recognition._labels = model_data["_labels"]
face_recognition._names = model_data["_names"]