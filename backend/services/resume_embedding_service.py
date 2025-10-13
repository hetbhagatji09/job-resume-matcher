from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy.orm import Session
from langchain_community.embeddings import HuggingFaceEmbeddings
from models.resume_embedding_model import ResumeEmbedding
from models.resume_model import Resume
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
from sentence_transformers import SentenceTransformer
# Initialize Groq model (LLaMA 3.1)
model = ChatGroq(
    temperature=0.3,
    model_name="llama-3.1-8b-instant"
)

class ResumeEmbeddingService:
    def __init__(self):
        # Use HuggingFace embeddings (local & free)
        self.embeddings = SentenceTransformer("all-MiniLM-L6-v2")

    def store_resume_embedding(self, db: Session, resume: Resume):
        """
        Generate and store embedding for a single resume
        based on essential fields for similarity search
        """
        if not resume:
            return {"status": "error", "message": "No resume provided"}

        # Convert JSON fields back to list/str
        def safe_load(val):
            try:
                return " ".join(json.loads(val)) if val else ""
            except:
                return val or ""

        skills = safe_load(resume.skills)
        education = safe_load(resume.education)
        experience = safe_load(resume.experience)
        projects = safe_load(resume.projects)
        certifications = safe_load(resume.certifications)

        # Build a meaningful string for embeddings
        resume_text = f"""
        Skills: {skills}
        Projects: {projects}
        Experience: {experience}
        Certifications: {certifications}
        """

        if not resume_text.strip():
            return {"status": "error", "message": "Empty resume text"}

        # Generate vector
        vector = self.embeddings.encode(
            resume_text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        project_vector=self.embeddings.encode(
            projects,
            normalize_embeddings=True
        )
        exp_vector=self.embeddings.encode(
            experience,
            normalize_embeddings=True
        )
        skill_vector=self.embeddings.encode(
            skills,
            normalize_embeddings=True
        )


        # Store in DB
        resume_vector_entry = ResumeEmbedding(
            resume_id=resume.id,
            resume_vector=vector,
            skill_vector=skill_vector,
            project_vector=project_vector,
            exp_vector=exp_vector
            
        )
        
        db.add(resume_vector_entry)
        db.commit()
        print(f"✅ Stored resume embedding for {resume.name}")

        # return {"status": "success", "resume_id": resume.id}