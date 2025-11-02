from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

class JobEmbedding(Base):
    __tablename__ = "job_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    job_vector = Column(Vector(384))   # ✅ pgvector type

    # Optional relationship if you want
    # job = relationship("Job", back_populates="embedding")
