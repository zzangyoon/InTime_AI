# mediapipe 모델 객체 생성 / 보관
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

face_detector = mp_face_detection.FaceDetection(
    model_selection=0, 
    min_detection_confidence=0.5
)