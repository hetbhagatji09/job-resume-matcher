from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

class JobEmbedding(Base):
    __tablename__ = "job_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    job_vector = Column(Vector(768))   # ✅ pgvector type
    role_vector = Column(Vector(768))       # Role/title
    requirements_vector = Column(Vector(768))  # Requirements / skills
    responsibilities_vector = Column(Vector(768)) # Responsibilities
    exp_vector = Column(Vector(768))        # Required experience
    

    # Optional relationship if you want
    # job = relationship("Job", back_populates="embedding")
