from sqlalchemy.orm import Session
from models.job import Job

def create_job(db: Session, job_data: dict):
    """Insert a single job into DB"""
    job = Job(
        job_role=job_data.get("job_role", ""),
        job_location=job_data.get("job_location", ""),
        job_experience=job_data.get("job_experience", "")
    )
    db.add(job)
def create_jobs(db: Session, jobs: list[dict]):
    """Insert multiple jobs into DB"""
    job_entries = []
    for j in jobs:
        job_entries.append(create_job(db, j))
    db.commit()
    return job_entries