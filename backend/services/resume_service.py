from PyPDF2 import PdfReader
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from database import get_db
from sqlalchemy.orm import Session
from models.resume_model import Resume
from dotenv import load_dotenv
import os
load_dotenv()
model = ChatGroq(
    temperature=0.3,
    model_name="llama-3.1-8b-instant"
)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # read key from .env
print("Loaded Groq API Key:", GROQ_API_KEY)
model = ChatGroq(
            temperature=0.7,
            model_name="llama-3.1-8b-instant"
        )
class ResumeService:

    def extract_resume_text(self, file) -> str:
        """Extract text from PDF file"""
        pdf_reader = PdfReader(file.file)
        text = " ".join([page.extract_text() or "" for page in pdf_reader.pages])
        return text

    def extract_resume_info_and_store(self, file, db: Session):
        """Extract structured resume info via LLM and store in DB"""

        # 1️⃣ Extract raw text
        resume_text = self.extract_resume_text(file)

        # 2️⃣ Build LLM prompt for structured info extraction
        prompt = PromptTemplate(
            input_variables=["resume"],
            template="""
            You are an AI assistant. Extract structured information from the following resume:

            Resume Text:
            {resume}

            Task:
            - Name
            - Email
            - Phone
            - Skills (comma separated)
            - Education (brief)
            - Work Experience (brief)
            Return as a JSON object with keys:
            name, email, phone, skills, education, experience
            """
        )
        chain = LLMChain(llm=model, prompt=prompt)
        result_json_str = chain.run({"resume": resume_text[:6000]})  # prevent overflow

        # 3️⃣ Convert result to dict
        import json
        try:
            data = json.loads(result_json_str)
        except:
            # fallback if LLM output is not proper JSON
            data = {
                "name": None,
                "email": None,
                "phone": None,
                "skills": None,
                "education": None,
                "experience": None,
                # "projects": None
            }

        # 4️⃣ Create Resume object
        resume_obj = Resume(
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            skills=data.get("skills"),
            education=data.get("education"),
            experience=data.get("experience"),
            # projects=data.get("projects"),
            # raw_text=resume_text,
            # metadata=data
        )
        print("This is my object")
        print(resume_obj)
        # 5️⃣ Store in DB
        db.add(resume_obj)
        db.commit()
        db.refresh(resume_obj)

        return resume_obj
    
    