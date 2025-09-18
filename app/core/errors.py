# ERROR 정리
class ErrorCode:
    DECODE_FAILED = "E001"
    FACE_NOT_FOUND = "E002"
    DB_INSERT_FAILED = "E003"
    INVALID_MODE = "E004"
    NAME_NOT_FOUND = "E005"
    ID_NOT_FOUND = "E006"
    UNKNOWN_ERROR = "E999"


class ErrorMessage:
    DECODE_FAILED = "이미지를 디코딩할 수 없습니다."
    FACE_NOT_FOUND = "얼굴 감지를 실패했습니다."
    DB_INSERT_FAILED = "DB 입력을 실패했습니다."
    INVALID_MODE = "유효하지 않은 모드입니다."
    NAME_NOT_FOUND = "이름을 찾을 수 없습니다."
    ID_NOT_FOUND = "ID 인식을 실패했습니다."
    UNKNOWN_ERROR = "알 수 없는 에러입니다."