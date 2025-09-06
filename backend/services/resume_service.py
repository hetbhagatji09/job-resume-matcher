from fastapi import UploadFile
from PyPDF2 import PdfReader


class ResumeService:
    def extract_resume_text(self, file: UploadFile) -> str:
        reader = PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text