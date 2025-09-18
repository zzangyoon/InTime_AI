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
from app.core.config import DEVICE
from app.services.db_service import insert_attendance, update_check_out, check_member_name
from app.core.errors import ErrorCode, ErrorMessage
from datetime import datetime
from zoneinfo import ZoneInfo

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

async def face_detections_from_images(files: list[UploadFile], mode: str):
    print("mode ::: ", mode)
    
    MODE = mode
    mode_msg = "출근"
    SAVE_DIR = "app/data/uploads/" + MODE + "/"
    METHOD = "FC"
    response = []
    cropped_faces = []

    for file in files:
        contents = await file.read()  # fastAPI 에서는 await 넣어주기 (비동기 처리)
        np_arr = np.frombuffer(contents, np.uint8)      # NumPy 배열
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # 이미지로 디코딩
        height, width, _ = img_cv.shape

        if img_cv is None:
            response.append({
                "filename": file.filename,
                "code": ErrorCode.DECODE_FAILED,
                "status": "error",
                "message": ErrorMessage.DECODE_FAILED
            })
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
            response.append({
                "filename": file.filename,
                "code": ErrorCode.FACE_NOT_FOUND,
                "status": "error",
                "message": ErrorMessage.FACE_NOT_FOUND
            })
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

            # -------------------------------
            # 정사각형으로 만들기 (padding 추가)
            # -------------------------------
            h_face, w_face, _ = face_crop.shape
            diff = abs(h_face - w_face)

            if h_face > w_face:
                # 좌우에 padding
                pad_left = diff // 2
                pad_right = diff - pad_left
                face_square = cv2.copyMakeBorder(face_crop, 0, 0, pad_left, pad_right,
                                                cv2.BORDER_CONSTANT, value=[0, 0, 0])  # 검정색 패딩
            elif w_face > h_face:
                # 위아래에 padding
                pad_top = diff // 2
                pad_bottom = diff - pad_top
                face_square = cv2.copyMakeBorder(face_crop, pad_top, pad_bottom, 0, 0,
                                                cv2.BORDER_CONSTANT, value=[0, 0, 0])
            else:
                face_square = face_crop  # 이미 정사각형이면 그대로

            # -------------------------------
            # 모델 입력 크기로 리사이즈 (224x224)
            # -------------------------------
            face_resized = cv2.resize(face_square, (224, 224))
            # print("face_resized.shape ::::: ", face_resized.shape)


            # -------------------------------
            # 분류모델 추론
            # -------------------------------
            id = infer(face_resized)
            print("id ::::: ", id)


            # -------------------------------
            # DB 저장
            # -------------------------------
            if mode == "check_in":      # 출근모드라면 -> insert
                insert_res = insert_attendance(id, METHOD, file_name)

                if insert_res["success"]:
                    print("img 통과")

                else:
                    response.append({
                        "filename": file.filename,
                        "code": ErrorCode.DB_INSERT_FAILED,
                        "status": "error",
                        "message": ErrorMessage.DB_INSERT_FAILED
                    })
                    continue
            elif mode == "check_out":   # 퇴근모드라면 -> update
                mode_msg = "퇴근"
                now = datetime.now(ZoneInfo("Asia/Seoul"))
                now_kst = now.strftime("%Y-%m-%d %H:%M:%S")
                today = now.date()
                update_check_out(now_kst, METHOD, file_name, id, today)
            else:
                response.append({
                    "filename": file.filename,
                    "code": ErrorCode.INVALID_MODE,
                    "status": "error",
                    "message": ErrorMessage.INVALID_MODE
                })
                continue

            # # 파일 저장명 생성
            # ext = file.filename.split(".")[-1]
            # file_name = f"{uuid.uuid4().hex[:9]}.{ext}"
            # save_path = "result_img_test/" + file_name

            # # 저장할 때 다시 BGR로 변환
            # # bgr_face_crop = cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR)
            # bgr_face_crop = cv2.cvtColor(face_resized, cv2.COLOR_RGB2BGR)
            # cv2.imwrite(save_path, bgr_face_crop)
            # print("bgr_face_crop.shape ::::: ", bgr_face_crop.shape)

        # 이름 가져오기
        name = check_member_name(id)

        if name is None:
            response.append({
                "filename": file.filename,
                "code": ErrorCode.NAME_NOT_FOUND,
                "status": "error",
                "message": ErrorMessage.NAME_NOT_FOUND
            })
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

    class_path = "data/dataset/train/"
    class_list = os.listdir(class_path)
    # class_list를 고유한 사원번호로 해야함 (이름일 경우 동명이인 문제 발생)

    with torch.no_grad() :
        pred = model(img_tensor)
        pred_result = torch.max(pred, dim=1)[1].item()
        score = nn.Softmax()(pred)[0]       # 전체를 1로 봤을때 각각의 비율 [0.03, 0.90, 0.07]
        score = float(score[pred_result])
        id = class_list[pred_result]

    return id