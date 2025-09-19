import os, json
import face_recognition
import numpy as np
from typing import List, Dict
from fastapi import UploadFile
from app.core.errors import ErrorCode, ErrorMessage
from app.services.db_service import insert_attendance, check_member
import numpy as np
import cv2
import uuid

'''
사용법
face_model = FaceRecognition()
face_model.fit(image_folder_name)
name = face_model.whoami(image_file)
name : 이미지 폴더에서 학습한 결과에 따른 일치하는 사람 이름

규칙
1. 이미지명 : 반드시 코드명으로
2. json 파일 : 반드시 하나의 파일 작성
3. json 파일 구성 : '코더':'이름' 형식으로 작성
예)
{
    "1":"Joe Biden",
    "2":"Barack Obama"
}
'''
class FaceRecognition:
    def __init__(self) -> None:
        self._encodings = []
        self._labels = []
        self._names = None
    '''
    이미지 폴더를 이용 학습
    이미지 폴더의 이미지 파일들 읽어서 인코딩 테이블, 레이블 테이블, 레이블의 이름 테이블 생성
    '''
    def fit(self,train_folder:str):
        print(f'1. load train folder : {train_folder}')
        train_files = os.listdir(train_folder)
        for step, file in enumerate(train_files):
            print(f'2 - {step+1}. train file : {file} ')
            file_name,file_ext = os.path.splitext(file)
            # Json 파일 일경우 이름 테이블 생성
            if file_ext == '.json':
                print(f'2 - {step+1} *. name table')
                if self._names is None:
                    with open(os.path.join(train_folder,file), encoding='utf-8') as f:
                        self._names = json.load(f)
                continue
            encoding = self.__face_encoding(os.path.join(train_folder,file))
            self._labels.append(file_name)
            self._encodings.append(encoding)
        print(f'3. train completed!')
        print('encoding : ',len(self._encodings))
        print('labels : ',self._labels)
        print('names : ',self._names)
        
    # 이미지의 인코딩 구하기
    def __face_encoding(self,image_file:np.ndarray) -> np.ndarray:
        # image = face_recognition.load_image_file(image_file)
        encoding = face_recognition.face_encodings(image_file)
        if len(encoding) >= 1:
            encoding = encoding[0]
        return encoding
    
    # 학습된 인코딩 테이블
    def encodings(self) -> List[np.ndarray]:
        return self._encodings
    
    # 학습된 레이블
    def labels(self) -> List[str]:
        return self._labels
    
    def names(self) -> Dict[str,str]:
        return self._names
    
    # 이미지 파일과 학습된 인코딩과의 거리
    def distance(self,image_file:str) -> np.ndarray:
        return face_recognition.face_distance(self._encodings,self.__face_encoding(image_file))
    
    # 이미지 파일과 학습된 인코딩과의 일치 여부
    # def compare(self,image_file:str) -> List[np.bool_]:
    def compare(self,image_file:np.ndarray) -> List[np.bool_]:
        encoding = self.__face_encoding(image_file)
        return face_recognition.compare_faces(self._encodings,encoding)
    
    def create_error_response(self, code, message):
        return {
            "code": code,
            "status": "error",
            "message": message
        }
    
    # 이미지와 일치하는 이름 혹은 코드
    # def whoami(self,image_file:str, is_name=True)->str | None:
    #     _distance = self.distance(image_file)   # 이미지와 등록된 얼굴들과의 거리 계산
    #     _compare = self.compare(image_file)     # 이미지가 등록된 얼굴들과 일치하는지 비교 결과 (True/False)
    #     idx = np.argmin(_distance)              # 거리값 중 가장 작은 (가장 비슷한) 얼굴의 인덱스를 구함
    #     label_idx = -1                          # 초기값 : 아직 일치하는게 없다고 가정
    #     if _compare[idx]:                       # 가장 비슷한 얼굴이 진짜로 일치한다면
    #         label_idx = idx                     # 그 인덱스를 라벨 인덱스로 설정
    #     if label_idx == -1:                     # 여전히 일치하는 얼굴이 없다면
    #         return None                         # 결과 없음 -> None 반환
    #     if (self._names is None) or (not is_name):  # 이름 정보가 없거나, 이름을 원하지 않으면
    #         return self._labels[label_idx]          # 그냥 라벨 ('1', '2') 반환
    #     return self._names[self._labels[label_idx]] # 이름 정보를 원한다면 이름 반환


    async def whoami(self, image_file: UploadFile, mode: str, is_name=True)->str | None:
        print("!!! def whoami")
        # print(f"[DEBUG] image_file type: {type(image_file)}")
        
        MODE = mode
        mode_msg = "출근" if mode == "check_in" else "퇴근"
        SAVE_DIR = f"app/data/uploads/{MODE}/"
        METHOD = "FR"
        response = []

        print("!!! def whoami 1")
        contents = await image_file.read()
        image_array = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        print("!!! def whoami 2")

        # 파일 저장명 생성
        ext = image_file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4().hex[:9]}.{ext}"
        save_path = SAVE_DIR + file_name

        print("!!! def whoami 3")

        # 이미지 저장
        cv2.imwrite(save_path, image)

        print("!!! def whoami 4")

        _distance = self.distance(image)
        _compare = self.compare(image)

        print("!!! def whoami 5")

        idx = np.argmin(_distance)
        label_idx = -1

        print("!!! def whoami 6")

        if _compare[idx]:
            label_idx = idx

        if label_idx == -1:
            # create_error_response(filename, code, message)
            response.append(
                self.create_error_response(ErrorCode.FACE_NOT_FOUND, ErrorMessage.FACE_NOT_FOUND)
            )
            return response
        
        if (self._names is None) or (not is_name):
            response.append(
                self.create_error_response(ErrorCode.NAME_NOT_FOUND, ErrorMessage.NAME_NOT_FOUND)
            )
            return response
        
        name = self._names[self._labels[label_idx]]
        id = self._labels[label_idx]

        print(f"before check_rlt ::: {name} / {id}")

        # attendance table insert 하기 전 이름, 사원번호 확인
        check_rlt = check_member(name, id)

        print(f"check_rlt result ::: {check_rlt}")
        if check_rlt == 0:
            response.append(
                self.create_error_response(ErrorCode.ID_NOT_FOUND, ErrorMessage.ID_NOT_FOUND)
            )
            return response
        
        # attendance table insert
        insert_res = insert_attendance(id, METHOD, file_name, MODE)

        if not insert_res["success"]:
            response.append({
                "status": "error",
                "message": insert_res["message"]
            })
            return response
        
        response.append({
            "status": "ok",
            "message" : f"{name}님이 {mode_msg}했습니다."
        })

        return response
    