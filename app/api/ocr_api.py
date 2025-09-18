# Controller
from fastapi import APIRouter, UploadFile, File, Form
from app.services.ocr_service import ocr_idcards

router = APIRouter()

@router.post("/ocr")
async def ocr(files: list[UploadFile] = File(...), mode: str = Form("check_in")):
    ocr_result = await ocr_idcards(files, mode)
    return ocr_result