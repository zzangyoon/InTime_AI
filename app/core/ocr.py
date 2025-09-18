# ocr 모델 객체 생성 / 보관
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="korean",
    use_doc_orientation_classify = False,
    use_doc_unwarping = False,
    use_textline_orientation = False
)