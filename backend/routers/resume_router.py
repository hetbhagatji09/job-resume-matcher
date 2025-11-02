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
import json
from fastapi import APIRouter, UploadFile, File, Depends
# Assuming necessary imports like Session, get_db, Resume, etc. are defined elsewhere
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models import Resume
# from app.services import service, embedding_service
# from langchain.prompts import PromptTemplate
# from langchain.llms import ... as model # Your LLM instance
# from langchain.chains import LLMChain
# from langchain.output_parsers import JsonOutputParser

# router = APIRouter() # Assuming this is the router instance

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
    name, email, phone, skills, education, experience, projects, certifications
    """
    prompt = PromptTemplate(input_variables=["resume"], template=prompt_template)
    chain = LLMChain(llm=model, prompt=prompt)

    # 3️⃣ Get raw output from LLM
    raw_output = chain.run({"resume": resume_text[:6000]})  # Slice to prevent overflow

    # 4️⃣ Parse JSON safely (Updated logic for robustness)
    parser = JsonOutputParser()
    
    # Define a safe fallback dictionary
    fallback_data = {
        "name": None,
        "email": None,
        "phone": None,
        "skills": [],         # Use empty lists for fields expected to be lists/arrays
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": []
    }
    
    try:
        # Attempt to parse the LLM output
        parsed_data = parser.parse(raw_output)
        
        # Ensure parsed_data is a dictionary, otherwise use fallback
        data = parsed_data if isinstance(parsed_data, dict) else fallback_data
        
    except Exception:
        # If parsing fails entirely, use the defined fallback
        data = fallback_data

    # 5️⃣ Create Resume object with null-safe values
    # The .get(key) method is now guaranteed to work because 'data' is always a dictionary.
    # The (value or []) ensures that json.dumps receives a list if the key was missing or None.
    resume_obj = Resume(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        skills=json.dumps(data.get("skills") or []),
        education=json.dumps(data.get("education") or []),
        experience=json.dumps(data.get("experience") or []),
        projects=json.dumps(data.get("projects") or []),
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
