from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.resume_model import Resume
from services.resume_service import ResumeService
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
import json
from services.resume_embedding_service import ResumeEmbeddingService
router = APIRouter(
    prefix="/resume",
    tags=["resumes"]
)

# Initialize service
service = ResumeService()
embedding_service=ResumeEmbeddingService()

# Initialize LLM model
model = ChatGroq(
    temperature=0.7,
    model_name="llama-3.3-70b-versatile"  # Make sure this model is available in your Groq dashboard
)

# Endpoint: Extract plain text from PDF
@router.post("/extract_resume")
async def extract_resume(file: UploadFile = File(...)):
    text = service.extract_resume_text(file)
    return {"text": text}


# Endpoint: Extract structured resume info and store in DB
@router.post("/resume_obj", response_model=dict)
async def extract_resume_obj(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1️⃣ Extract raw text from PDF
    resume_text = service.extract_resume_text(file)

    # 2️⃣ Define strict JSON prompt
    prompt_template = """
    You are an AI assistant. Extract structured information from the following resume.
    ⚠️ Return ONLY valid JSON. Do NOT include explanations, markdown, or extra text.
    Takes All points of skills and responsibilities of projects as descreption

    Resume:
    {resume}

    Return JSON with keys:
    name, email, phone, skills, education, experience, projects,certifications
    """
    prompt = PromptTemplate(input_variables=["resume"], template=prompt_template)
    chain = LLMChain(llm=model, prompt=prompt)

    # 3️⃣ Get raw output from LLM
    raw_output = chain.run({"resume": resume_text[:6000]})  # Slice to prevent overflow

    # 4️⃣ Parse JSON safely
    parser = JsonOutputParser()
    try:
        data = parser.parse(raw_output)
    except Exception:
        # fallback in case LLM output is malformed
        data = {
            "name": None,
            "email": None,
            "phone": None,
            "skills": None,
            "education": None,
            "experience": None,
            "projects": None,
            "certifications":None
        }

    # 5️⃣ Create Resume object with null-safe values
    resume_obj = Resume(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        skills=json.dumps(data.get("skills") or []),        # Convert dict/list to string
        education=json.dumps(data.get("education") or []),
        experience=json.dumps(data.get("experience") or []),
        projects=json.dumps(data.get("projects") or []),  # Keep commented if your model/table doesn’t have this
        certifications=json.dumps(data.get("certifications") or [])
    )
    
    # 6️⃣ Store in DB
    db.add(resume_obj)
    db.commit()
    db.refresh(resume_obj)
    
    embedding_service.store_resume_embedding(db,resume_obj)
    

    # 7️⃣ Return structured object
    return {
        "name": resume_obj.name,
        "email": resume_obj.email,
        "phone": resume_obj.phone,
        "skills": resume_obj.skills,
        "education": resume_obj.education,
        "experience": resume_obj.experience,
        "projects": resume_obj.projects,
        "certifications":resume_obj.certifications
    }

@router.post("/resume_test", response_model=dict)
async def extract_resume_obj(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1️⃣ Extract raw text from PDF
    resume_text = service.extract_resume_text(file)

    # 2️⃣ Define strict JSON prompt
    prompt_template = """
    You are an AI assistant. Extract structured information from the following resume.
    ⚠️ Return ONLY valid JSON. Do NOT include explanations, markdown, or extra text.
    Takes All points of skills and responsibilities of projects as descreption

    Resume:
    {resume}

    Return JSON with keys:
    name, email, phone, skills, education, experience, projects,certifications
    """
    prompt = PromptTemplate(input_variables=["resume"], template=prompt_template)
    chain = LLMChain(llm=model, prompt=prompt)

    # 3️⃣ Get raw output from LLM
    raw_output = chain.run({"resume": resume_text[:6000]})  # Slice to prevent overflow

    # 4️⃣ Parse JSON safely
    parser = JsonOutputParser()
    try:
        data = parser.parse(raw_output)
    except Exception:
        # fallback in case LLM output is malformed
        data = {
            "name": None,
            "email": None,
            "phone": None,
            "skills": None,
            "education": None,
            "experience": None,
            "projects": None,
            "certifications":None
        }

    # 5️⃣ Create Resume object with null-safe values
    resume_obj = Resume(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        skills=json.dumps(data.get("skills") or []),        # Convert dict/list to string
        education=json.dumps(data.get("education") or []),
        experience=json.dumps(data.get("experience") or []),
        projects=json.dumps(data.get("projects") or []),  # Keep commented if your model/table doesn’t have this
        certifications=json.dumps(data.get("certifications") or [])
    )
    

    # 7️⃣ Return structured object
    return {
        "name": resume_obj.name,
        "email": resume_obj.email,
        "phone": resume_obj.phone,
        "skills": resume_obj.skills,
        "education": resume_obj.education,
        "experience": resume_obj.experience,
        "projects": resume_obj.projects,
        "certifications":resume_obj.certifications
    }
