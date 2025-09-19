from fastapi import UploadFile
from app.core.ocr import ocr
import cv2
import uuid
import numpy as np
from app.services.db_service import insert_attendance, update_check_out, check_member
from app.core.errors import ErrorCode, ErrorMessage
from datetime import datetime
from zoneinfo import ZoneInfo

async def ocr_idcards(files: list[UploadFile], mode: str):

    MODE = mode
    mode_msg = "출근" if mode == "check_in" else "퇴근"
    SAVE_DIR = f"app/data/uploads/{MODE}/"
    METHOD = "ID"
    response = []

    for file in files:
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
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
        cv2.imwrite(save_path, img)

        # 좌우반전
        img_flipped = cv2.flip(img, 1)

        results = ocr.predict(input = img_flipped)
        
        text_list = results[0]["rec_texts"]

        for text in text_list:
            if "wanted" in text :
                print("wanted")
            elif "ID" in text:
                no_space = "".join(text.split())
                if len(no_space) < 6:
                    response.append({
                        "filename": file.filename,
                        "code": ErrorCode.ID_NOT_FOUND,
                        "status": "error",
                        "message": ErrorMessage.ID_NOT_FOUND
                    })
                    continue
                final_id = no_space[-6:]
            else :
                name = text
        
        print(f"이름 : {name}, 사원번호 : {final_id}")

        ########################################
        # DB 저장
        ########################################
        # 이름, 사원번호가 맞게 있는지 확인 후 insert
        check_rlt = check_member(name, final_id)

        if check_rlt == 0:
            response.append({
                "filename": file.filename,
                "code": ErrorCode.ID_NOT_FOUND,
                "status": "error",
                "message": ErrorMessage.ID_NOT_FOUND
            })
            continue

        # attendance table insert
        insert_res = insert_attendance(final_id, METHOD, file_name, MODE)

        if not insert_res["success"]:
            response.append({
                "status": "error",
                "message": insert_res["message"]
            })
            continue
        
        response.append({
            "filename": file.filename,
            "status": "ok",
            "message" : f"{name}님이 {mode_msg}했습니다."
        })

    return response
