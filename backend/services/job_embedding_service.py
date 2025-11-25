from sqlalchemy.orm import Session
from models.job_embedding_model import JobEmbedding
from services.nltk_service import TextCleaningService
from utills.hugmodel import model  # Your HF embedding model
from dotenv import load_dotenv
import json
from models.resume_model import Resume
from sqlalchemy import select
from models.resume_embedding_model import ResumeEmbedding

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

    # -------------------------------------------------------------
    # MATCH RESUMES WITH ATTRIBUTE-LEVEL SCORING (UPDATED VERSION)
    # -------------------------------------------------------------
    def match_resumes(self, db: Session, job_id: int, top_k: int = 5):
        """
            Compare stored job vectors with stored resume vectors
            and return top_k most similar resumes.
        """

        if not job_id:
            return {"status": "error", "message": "job_id is required"}

        # 1️⃣ Fetch job embedding from DB
        job_embed = db.query(JobEmbedding).filter(JobEmbedding.job_id == job_id).first()

        if not job_embed:
            return {"status": "error", "message": "No embeddings found for this job_id"}

        # 2️⃣ Extract job vectors from DB
        job_role_vec = job_embed.job_role_vector
        job_overview_vec = job_embed.job_overview_vector
        job_experience_vec = job_embed.job_experience_vector
        job_responsibilities_vec = job_embed.job_responsibilities_vector
        job_requirements_vec = job_embed.job_requirements_vector

        # 3️⃣ Fetch all resumes + their embeddings
        stmt = select(
            Resume,
            ResumeEmbedding.skills_vector,
            ResumeEmbedding.education_vector,
            ResumeEmbedding.experience_vector,
            ResumeEmbedding.projects_vector,
            ResumeEmbedding.certifications_vector
        ).join(ResumeEmbedding, Resume.id == ResumeEmbedding.resume_id)

        rows = db.execute(stmt).all()

        results = []

        # 4️⃣ Weights
        W_SKILLS = 0.35
        W_EXPERIENCE = 0.30
        W_PROJECTS = 0.15
        W_ROLE = 0.10
        W_CERTIFICATIONS = 0.05
        W_EDUCATION = 0.05

        # 5️⃣ Cosine similarity function
        from numpy import dot
        from numpy.linalg import norm

        def cosine(a, b):
            if a is None or b is None:
                return 0.0
            return float(dot(a, b) / (norm(a) * norm(b) + 1e-10))

        # 6️⃣ Calculate similarity for each resume
        for resume, skills_vec, edu_vec, exp_vec, proj_vec, cert_vec in rows:

            s1 = cosine(skills_vec, job_requirements_vec)          # Skills ↔ Requirements
            s2 = cosine(exp_vec, job_responsibilities_vec)         # Experience ↔ Responsibilities
            s3 = cosine(proj_vec, job_overview_vec)                # Projects ↔ Overview
            s4 = cosine(exp_vec, job_role_vec)                     # Experience ↔ Role
            s5 = cosine(cert_vec, job_requirements_vec)            # Certifications ↔ Requirements
            s6 = cosine(edu_vec, job_requirements_vec)             # Education ↔ Requirements

            final_score = (
                W_SKILLS * s1 +
                W_EXPERIENCE * s2 +
                W_PROJECTS * s3 +
                W_ROLE * s4 +
                W_CERTIFICATIONS * s5 +
                W_EDUCATION * s6
            )

            results.append({
                "resume_id": resume.id,
                "name": resume.name,
                "email": resume.email,
                "phone": resume.phone,
                "similarity_score": float(final_score),
                # Debug values
                "s1_skills_vs_requirements": float(s1),
                "s2_experience_vs_responsibilities": float(s2),
                "s3_projects_vs_overview": float(s3),
                "s4_experience_vs_role": float(s4),
                "s5_certifications_vs_requirements": float(s5),
                "s6_education_vs_requirements": float(s6)
            })

        # 7️⃣ Sort and return
        results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)

        return {
            "status": "success",
            "matches": results[:top_k]
        }
