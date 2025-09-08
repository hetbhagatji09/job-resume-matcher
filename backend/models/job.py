from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine,Text

from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_role = Column(String(255), nullable=False)        # Role (e.g., Software Engineer)
    job_location = Column(String(255), nullable=True)     # Location (e.g., Bangalore)
    job_experience = Column(String(100), nullable=True)   # Experience (e.g., 2-4 years)
    job_overview= Column(Text,nullable=True)
    job_responsibilities= Column(Text,nullable=True)
    job_requirements= Column(Text,nullable=True)