from sqlalchemy import Column, Integer, String, Text
from database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # file_name = Column(String(255), nullable=True)    # Name of the uploaded PDF (nullable now)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    # location = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    skills = Column(Text, nullable=True)               # Could store as comma-separated string
    education = Column(Text, nullable=True)           # Could store as comma-separated string
    experience = Column(Text, nullable=True)          # Could store as comma-separated string
    projects = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
