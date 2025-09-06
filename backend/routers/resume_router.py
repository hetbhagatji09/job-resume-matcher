from fastapi import APIRouter, UploadFile, File
from models.resume_model import Resume
from services.resume_service import ResumeService

router = APIRouter(
    prefix="/resume",
    tags=["resumes"]
)
service = ResumeService()

@router.post("/extract_resume")
async def extract_resume(file: UploadFile = File(...)):
    text = service.extract_resume_text(file)
    return text
