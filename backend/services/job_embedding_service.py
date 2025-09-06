from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy.orm import Session
from models.job_embedding_model import JobEmbedding
import json
from dotenv import load_dotenv
load_dotenv()

class JobEmbeddingService:
    def __init__(self):
        # Initialize Google Embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    def store_job_embeddings(self, db: Session, jobs: list):
        if not jobs:
            return {"status": "error", "message": "No jobs provided"}

        for job in jobs:
            # ✅ ORM objects → access attributes directly
            job_id = job.id
            job_text = f"{job.job_role or ''} {job.job_location or ''} {job.job_experience or ''}"

            if not job_id or not job_text.strip():
                continue

            # ✅ Generate embedding
            vector = self.embeddings.embed_query(job_text)

            # ✅ Store in DB
            job_vector_entry = JobEmbedding(
                job_id=job_id,
                job_vector=vector
            )
            db.add(job_vector_entry)

        db.commit()
        print("✅ Stored job embeddings")
        #return {"status": "success", "total_vectors": len(jobs)}
