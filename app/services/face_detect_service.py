# Service (비즈니스 로직)
import cv2
import os
import numpy as np
import mediapipe as mp
import uuid
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from fastapi import UploadFile
from app.core.face_detect import face_detector
from app.core.model_loader import model
from PIL import Image
from app.core.config import DEVICE, CLASS_LIST
from app.services.db_service import insert_attendance, update_check_out, check_member_name
from app.core.errors import ErrorCode, ErrorMessage
from datetime import datetime
from zoneinfo import ZoneInfo

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils


async def face_detections_from_images(files: list[UploadFile], mode: str):
    print("mode ::: ", mode)
    
    MODE = mode
    mode_msg = "출근" if mode == "check_in" else "퇴근"
    SAVE_DIR = f"app/data/uploads/{MODE}/"
    METHOD = "FD"
    response = []
    cropped_faces = []

    for file in files:
        contents = await file.read()  # fastAPI 에서는 await 넣어주기 (비동기 처리)
        np_arr = np.frombuffer(contents, np.uint8)      # NumPy 배열
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # 이미지로 디코딩
        height, width, _ = img_cv.shape

        if img_cv is None:
            response.append(
                create_error_response(file.filename, ErrorCode.DECODE_FAILED, ErrorMessage.DECODE_FAILED)
            )
            continue

        # 파일 저장명 생성
        ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4().hex[:9]}.{ext}"
        save_path = SAVE_DIR + file_name

        # 이미지 저장
        cv2.imwrite(save_path, img_cv)

        image = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

        # face 감지
        results = face_detector.process(image)
        print("results ::: ", results)

        if not results.detections:
            response.append(
                create_error_response(file.filename, ErrorCode.FACE_NOT_FOUND, ErrorMessage.FACE_NOT_FOUND)
            )
            continue

        annotated_img = image.copy()

        for detection in results.detections:
            # 박스 그리기
            mp_drawing.draw_detection(annotated_img, detection)

            # 박스 좌표로 얼굴 잘라내기
            bbox = detection.location_data.relative_bounding_box

            # 정규화된 좌표 → 실제 픽셀 좌표
            x = int(bbox.xmin * width)
            y = int(bbox.ymin * height)
            w = int(bbox.width * width)
            h = int(bbox.height * height)

            # 음수나 경계 초과 방지
            x = max(x, 0)
            y = max(y, 0)
            x2 = min(x + w, width)
            y2 = min(y + h, height)

            face_crop = image[y:y2, x:x2]
            cropped_faces.append(face_crop)

            # 이미지를 정사각형을 만들고, 리사이즈 하는 함수
            face_resized = make_square_and_resize(face_crop, 224)

            # -------------------------------
            # 분류모델 추론
            # -------------------------------
            id = infer(face_resized)
            print("id ::::: ", id)

            # -------------------------------
            # DB 저장
            # -------------------------------
            insert_res = insert_attendance(id, METHOD, file_name, MODE)

            if not insert_res["success"]:
                response.append({
                    "status": "error",
                    "message": insert_res["message"]
                })
                continue

        # 이름 가져오기
        name = check_member_name(id)
        if name is None:
            response.append(
                create_error_response(file.filename, ErrorCode.NAME_NOT_FOUND, ErrorMessage.NAME_NOT_FOUND)
            )
            continue

        response.append({
            "filename": file.filename,
            "cropped_faces": len(cropped_faces),
            "status": "ok",
            "message" : f"{name}님이 {mode_msg}했습니다."
        })

    return response


def infer(image: np.ndarray):

    # transform
    transforms_infer = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 이미 평가모드의 모델을 가져옴 -> model
    pil_img = Image.fromarray(image)
    img_tensor = transforms_infer(pil_img).unsqueeze(0).to(DEVICE)

    class_list = CLASS_LIST
    # class_list를 고유한 사원번호로 해야함 (이름일 경우 동명이인 문제 발생)

    with torch.no_grad() :
        pred = model(img_tensor)
        pred_result = torch.max(pred, dim=1)[1].item()
        score = nn.Softmax()(pred)[0]       # 전체를 1로 봤을때 각각의 비율 [0.03, 0.90, 0.07]
        score = float(score[pred_result])
        id = class_list[pred_result]

    return id


def make_square_and_resize(image:np.ndarray, size:int = 224) -> np.ndarray:
    # 이미지를 정사각형을 만들고, 리사이즈 하는 함수
    # -------------------------------
    # 정사각형으로 만들기 (padding 추가)
    # -------------------------------
    h, w, _ = image.shape
    diff = abs(h - w)

    if h > w:
        # 좌우에 padding
        pad_left = diff // 2
        pad_right = diff - pad_left
        face_square = cv2.copyMakeBorder(image, 0, 0, pad_left, pad_right,
                                        cv2.BORDER_CONSTANT, value=[0, 0, 0])  # 검정색 패딩
    elif w > h:
        # 위아래에 padding
        pad_top = diff // 2
        pad_bottom = diff - pad_top
        face_square = cv2.copyMakeBorder(image, pad_top, pad_bottom, 0, 0,
                                        cv2.BORDER_CONSTANT, value=[0, 0, 0])
    else:
        face_square = image  # 이미 정사각형이면 그대로

    # -------------------------------
    # 모델 입력 크기로 리사이즈 (224x224)
    # -------------------------------
    face_resized = cv2.resize(face_square, (size, size))
    
    return face_resized


def create_error_response(filename, code, message):
    return {
        "filename": filename,
        "code": code,
        "status": "error",
        "message": message
    }