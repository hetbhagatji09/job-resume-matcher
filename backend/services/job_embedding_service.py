from sqlalchemy.orm import Session
from models.job_embedding_model import JobEmbedding
from services.nltk_service import TextCleaningService
from utills.hugmodel import model  # Your HF embedding model
from dotenv import load_dotenv
import json

load_dotenv()

cleaner = TextCleaningService()


class JobEmbeddingService:
    def __init__(self):
        # HuggingFace embedding model (384 dim)
        self.embeddings = model

    # -------------------------------------------------------------
    # STORE ATTRIBUTE-WISE JOB EMBEDDINGS
    # -------------------------------------------------------------
    def store_job_embeddings(self, db: Session, jobs: list):

        if not jobs:
            return {"status": "error", "message": "No jobs provided"}

        for job in jobs:

            job_id = job.id

            # ---------- CLEAN EACH FIELD SEPARATELY ----------
            role = cleaner.clean(str(job.job_role or ""))
            experience = cleaner.clean(str(job.job_experience or ""))
            overview = cleaner.clean(str(job.job_overview or ""))
            responsibilities = cleaner.clean(str(job.job_responsibilities or ""))
            requirements = cleaner.clean(str(job.job_requirements or ""))

            # Skip empty job
            if not job_id:
                continue

            # ---------- ENCODE EACH ATTRIBUTE ----------
            role_vec = self.embeddings.encode(role, convert_to_numpy=True) if role.strip() else None
            exp_vec = self.embeddings.encode(experience, convert_to_numpy=True) if experience.strip() else None
            overview_vec = self.embeddings.encode(overview, convert_to_numpy=True) if overview.strip() else None
            resp_vec = self.embeddings.encode(responsibilities, convert_to_numpy=True) if responsibilities.strip() else None
            req_vec = self.embeddings.encode(requirements, convert_to_numpy=True) if requirements.strip() else None

            # ---------- STORE IN DATABASE ----------
            job_vec_entry = JobEmbedding(
                job_id=job_id,
                job_role_vector=role_vec,
                job_experience_vector=exp_vec,
                job_overview_vector=overview_vec,
                job_responsibilities_vector=resp_vec,
                job_requirements_vector=req_vec
            )

            db.add(job_vec_entry)

        db.commit()
        print("✅ Stored attribute-level job embeddings")

