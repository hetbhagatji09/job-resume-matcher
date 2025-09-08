from sqlalchemy.orm import Session
from models.job import Job

def create_job(db: Session, job_data: dict):
    """Insert a single job into DB"""
    job = Job(
        job_role=job_data.get("job_role", ""),
        job_location=job_data.get("job_location", ""),
        job_experience=job_data.get("job_experience", ""),
        job_responsibilities=job_data.get("job_responsibilities",""),
        job_requirements=job_data.get("job_requirements",""),
        job_overview=job_data.get("job_overview","")
    )
    db.add(job)
    db.flush()  # ✅ get auto-generated ID without committing yet
    return job  # ✅ return ORM object


def create_jobs(db: Session, jobs: list[dict]):
    """Insert multiple jobs into DB"""
    job_entries = []
    for j in jobs:
        job_entries.append(create_job(db, j))
    db.commit()
    return job_entries
