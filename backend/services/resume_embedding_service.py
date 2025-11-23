from sqlalchemy.orm import Session
import json
import re

from models.resume_embedding_model import ResumeEmbedding
from models.resume_model import Resume

from utills.hugmodel import model   # your HuggingFace embedding model
from services.nltk_service import TextCleaningService

# Initialize text cleaner
cleaner = TextCleaningService()


class ResumeEmbeddingService:
    def __init__(self):
        # Load local HF embedding model
        self.embeddings = model

    def store_resume_embedding(self, db: Session, resume: Resume):
        """
        Generate section-wise embeddings for a resume.
        Clean every field, convert JSON to text, and store 5 vectors.
        """

        if not resume:
            return {"status": "error", "message": "No resume provided"}

        # ---------- Safe JSON Loader ----------
        def safe_load(val):
            try:
                loaded = json.loads(val)
                if isinstance(loaded, list):
                    return " ".join(map(str, loaded))
                elif isinstance(loaded, dict):
                    return " ".join(map(str, loaded.values()))
                else:
                    return str(loaded)
            except:
                return str(val or "")

        # ---------- Extract raw text fields ----------
        raw_skills = safe_load(resume.skills)
        raw_education = safe_load(resume.education)
        raw_experience = safe_load(resume.experience)
        raw_projects = safe_load(resume.projects)
        raw_certifications = safe_load(resume.certifications)

        # ---------- Clean each section ----------
        skills_text = cleaner.clean(raw_skills)
        education_text = cleaner.clean(raw_education)
        experience_text = cleaner.clean(raw_experience)
        projects_text = cleaner.clean(raw_projects)
        certifications_text = cleaner.clean(raw_certifications)

        # If everything is empty → skip
        combined = (
            skills_text + education_text + experience_text +
            projects_text + certifications_text
        ).strip()

        if not combined:
            return {"status": "error", "message": "Empty resume data"}

        # ---------- Encode each section ----------
        skills_vec = self.embeddings.encode(skills_text, convert_to_numpy=True) if skills_text else None
        education_vec = self.embeddings.encode(education_text, convert_to_numpy=True) if education_text else None
        experience_vec = self.embeddings.encode(experience_text, convert_to_numpy=True) if experience_text else None
        projects_vec = self.embeddings.encode(projects_text, convert_to_numpy=True) if projects_text else None
        certifications_vec = self.embeddings.encode(certifications_text, convert_to_numpy=True) if certifications_text else None

        # ---------- Save to Database ----------
        resume_vector_entry = ResumeEmbedding(
            resume_id=resume.id,
            skills_vector=skills_vec,
            education_vector=education_vec,
            experience_vector=experience_vec,
            projects_vector=projects_vec,
            certifications_vector=certifications_vec
        )

        db.add(resume_vector_entry)
        db.commit()

        print(f"✅ Stored section-wise resume embeddings for {resume.name}")

        return {"status": "success", "resume_id": resume.id}
