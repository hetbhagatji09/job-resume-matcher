from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

class ResumeEmbedding(Base):
    __tablename__ = "resume_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    resume_vector = Column(Vector(768))   # ✅ pgvector type
    skill_vector= Column(Vector(768))
    project_vector =Column(Vector(768))
    exp_vector =Column(Vector(768))
