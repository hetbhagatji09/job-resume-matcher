from pydantic import BaseModel
from typing import Optional

class JobCreate(BaseModel):
    job_role: str
    job_location: Optional[str] = None
    job_experience: Optional[str] = None
    job_overview: Optional[str] = None
    job_responsibilities: Optional[str] = None
    job_requirements: Optional[str] = None
