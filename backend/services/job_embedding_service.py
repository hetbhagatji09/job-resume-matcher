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
import numpy as np
load_dotenv()

class JobEmbeddingService:
    def __init__(self):
        # Initialize Google Embedding model
        self.embeddings =SentenceTransformer("all-MiniLM-L6-v2")

    def store_job_embeddings(self, db: Session, jobs: list):
        if not jobs:
            return {"status": "error", "message": "No jobs provided"}

        for job in jobs:
            job_id = job.id

            # Build fields
            role = job.job_role or ""
            requirements = job.job_requirements or ""
            responsibilities = job.job_responsibilities or ""
            experience = job.job_experience or ""
            overview = job.job_overview or ""

            # Whole text
            job_text = f"""
                Role: {role}
                Experience: {experience}
                Responsibilities: {responsibilities}
                Requirements: {requirements}
                Overview: {overview}
            """

            if not job_id or not job_text.strip():
                continue

            # Encode
            job_vector = self.embeddings.encode(job_text, convert_to_numpy=True, normalize_embeddings=True)
            role_vector = self.embeddings.encode(role, convert_to_numpy=True, normalize_embeddings=True)
            requirements_vector = self.embeddings.encode(requirements, convert_to_numpy=True, normalize_embeddings=True)
            responsibilities_vector = (
                self.embeddings.encode(responsibilities, convert_to_numpy=True, normalize_embeddings=True)
                if responsibilities else None
            )
            exp_vector = self.embeddings.encode(experience, convert_to_numpy=True, normalize_embeddings=True)

            # Store
            job_vector_entry = JobEmbedding(
                job_id=job_id,
                job_vector=job_vector,
                role_vector=role_vector,
                requirements_vector=requirements_vector,
                responsibilities_vector=responsibilities_vector,
                exp_vector=exp_vector
            )

            db.add(job_vector_entry)

        db.commit()
        print("✅ Stored job embeddings")

        #return {"status": "success", "total_vectors": len(jobs)}
        
    def match_resumes(self, db: Session, job_id: int, top_k: int = 5):
        """
        Compare a job (by job_id → JobEmbedding) to all resume embeddings.
        Weighted scoring:
        - requirements ↔ skills (0.4)
        - responsibilities ↔ (exp+projects)/2 (0.3)
        - exp ↔ exp (0.2)
        - role ↔ resume (0.1)
        """
        # 1️⃣ Get the job embedding
        job_embedding = db.query(JobEmbedding).filter(JobEmbedding.job_id == job_id).first()
        if not job_embedding:
            return {"status": "error", "message": f"No embeddings found for job_id {job_id}"}

        # 2️⃣ Get all resumes
        resumes = db.query(ResumeEmbedding).all()
        results = []

        # 3️⃣ Compute similarity scores
        for resume in resumes:
            skills_similarity = self.cosine_sim(job_embedding.requirements_vector, resume.skill_vector)
            exp_similarity = self.cosine_sim(job_embedding.exp_vector, resume.exp_vector)
            project_similarity = self.cosine_sim(job_embedding.responsibilities_vector, resume.project_vector)
            role_similarity = self.cosine_sim(job_embedding.role_vector, resume.resume_vector)

            final_score = (
                0.5 * skills_similarity +           # 0.4 / 1.1
                0.3 * (project_similarity) +  # 0.4 / 1.1
                0.2 * exp_similarity            # 0.2 / 11
            )

            results.append({
                "resume_id": resume.resume_id,
                "score": final_score,
                "breakdown": {
                "skills_similarity": skills_similarity,
                "exp_similarity": exp_similarity,
                "project_similarity": project_similarity
            }
        })

        # 4️⃣ Sort and return top_k
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        return {"status": "success", "matches": results[:top_k]}
    @staticmethod
    def cosine_sim(vec1, vec2):
        """Cosine similarity between two vectors (handle None gracefully)."""
        if vec1 is None or vec2 is None:
            return 0.0
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
