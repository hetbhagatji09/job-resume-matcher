from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

class JobEmbedding(Base):
    __tablename__ = "job_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    # --- Separate vectors for each attribute ---
    job_role_vector = Column(Vector(384), nullable=True)
    job_experience_vector = Column(Vector(384), nullable=True)
    job_overview_vector = Column(Vector(384), nullable=True)
    job_responsibilities_vector = Column(Vector(384), nullable=True)
    job_requirements_vector = Column(Vector(384), nullable=True)

    # Optional relationship
    job = relationship("Job")
