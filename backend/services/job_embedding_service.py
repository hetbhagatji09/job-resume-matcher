from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from sqlalchemy.orm import Session
from models.job_embedding_model import JobEmbedding
import json
from sqlalchemy import select
from models.resume_embedding_model import ResumeEmbedding
from models.resume_model import Resume
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from utills.hugmodel import model
load_dotenv()
from services.nltk_service import TextCleaningService
cleaner=TextCleaningService()
class JobEmbeddingService:
    def __init__(self):
        # Initialize Google Embedding model
        self.embeddings =model

    def store_job_embeddings(self, db: Session, jobs: list):
        if not jobs:
            return {"status": "error", "message": "No jobs provided"}

        for job in jobs:
            # ✅ ORM objects → access attributes directly
            job_id = job.id
            job_text = (
                str(job.job_role or "") + " " +
                str(job.job_experience or "") + " " +
                str(job.job_overview or "") + " " +
                str(job.job_responsibilities or "") + " " +
                str(job.job_requirements or "")
            )

            job_text=cleaner.clean(job_text)


            if not job_id or not job_text.strip():
                continue

            # ✅ Generate embedding
            vector = self.embeddings.encode(job_text, convert_to_numpy=True)

            # ✅ Store in DB
            job_vector_entry = JobEmbedding(
                job_id=job_id,
                job_vector=vector
            )
            db.add(job_vector_entry)

        db.commit()
        print("✅ Stored job embeddings")
        #return {"status": "success", "total_vectors": len(jobs)}
        
    def match_resumes(self, db: Session, job_data: dict, top_k: int = 5):
        """
        Generate embedding for a given job object (not yet in DB)
        and return top_k most similar resumes
        """
        # 1️⃣ Build job text
        job_text = f"""
        Role: {job_data.get("job_role", "")}
        Overview: {job_data.get("job_overview", "")}
        Experience: {job_data.get("job_experience", "")}
        Responsibilities: {job_data.get("job_responsibilities", "")}
        Requirements: {job_data.get("job_requirements", "")}
        """

        if not job_text.strip():
            return {"status": "error", "message": "Empty job data provided"}

        # 2️⃣ Generate job vector
        job_vector = self.embeddings.encode(job_text, convert_to_numpy=True)

        # 3️⃣ Query resumes with similarity search
        stmt = (
            select(Resume, ResumeEmbedding.resume_vector.cosine_distance(job_vector).label("score"))
            .join(ResumeEmbedding, Resume.id == ResumeEmbedding.resume_id)
            .order_by("score")
            .limit(top_k)
        )

        results = db.execute(stmt).all()

        # 4️⃣ Format results
        top_resumes = []
        for resume, score in results:
            top_resumes.append({
                "resume_id": resume.id,
                "name": resume.name,
                "email": resume.email,
                "phone": resume.phone,
                "similarity_score": float(1 - score)  # convert distance → similarity
            })

        return {"status": "success", "matches": top_resumes}
