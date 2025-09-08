from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy.orm import Session
from models.resume_embedding_model import ResumeEmbedding
from models.resume_model import Resume
import json
from dotenv import load_dotenv
load_dotenv()

class ResumeEmbeddingService:
    def __init__(self):
        # Initialize Google Embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

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
        Education: {education}
        Experience: {experience}
        Projects: {projects}
        Certifications: {certifications}
        """

        if not resume_text.strip():
            return {"status": "error", "message": "Empty resume text"}

        # Generate vector
        vector = self.embeddings.embed_query(resume_text)

        # Store in DB
        resume_vector_entry = ResumeEmbedding(
            resume_id=resume.id,
            resume_vector=vector
        )
        db.add(resume_vector_entry)
        db.commit()
        print(f"✅ Stored resume embedding for {resume.name}")

        # return {"status": "success", "resume_id": resume.id}