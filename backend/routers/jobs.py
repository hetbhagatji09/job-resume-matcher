from fastapi import APIRouter, Query, HTTPException,Depends
from database import get_db
from services.scraper_service import scrape_jobs
from sqlalchemy.orm import Session
from crud.job_crud import create_jobs
from database import SessionLocal
from services.job_embedding_service import JobEmbeddingService
router = APIRouter()
from fastapi import Path
from models.job import Job 
embedding_service = JobEmbeddingService()

@router.get("/jobs")
def get_jobs(url: str = Query(..., description="Website URL to scrape jobs from")):
    try:
        jobs =scrape_jobs(url)
        print("Job  type is ")
        print(type(jobs))
        if isinstance(jobs, dict):
            jobs = [jobs]
        db: Session = SessionLocal()
        job_entries = create_jobs(db, jobs)
        embedding_service.store_job_embeddings(db, job_entries)
        db.close()
        return {"url": url, "total_jobs": len(jobs), "jobs": jobs}
        # return job_entries
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scraped")
def getget_scrapedjobs(url: str = Query(..., description="Website URL to scrape jobs from")):
    jobs =scrape_jobs(url)
    print(jobs)
    return jobs

@router.post("/match_resumes")
async def match_resumes(
    job_data: dict,
    top_k: int = Query(5, description="Number of resumes to return"),
    db: Session = Depends(get_db)
):
    """
    Match resumes for a given job object
    """
    return embedding_service.match_resumes(db, job_data, top_k)
@router.get("/job_text/{job_id}")
def get_job_text(
    job_id: int = Path(..., description="Job ID to get job text for"),
    db: Session = Depends(get_db)
):
    """
    Return the concatenated job_text for a given job_id
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Build the job_text (same as in JobEmbeddingService)
    job_text = (
        f"Job Title: {job.job_role or ''} "
        f"Job Experience: {job.job_experience or ''} "
        f"Job Overview: {job.job_overview or ''} "
        f"Job Responsibilities: {job.job_responsibilities or ''} "
        f"Job Requirements: {job.job_requirements or ''}"
    )

    return {"job_id": job.id, "job_text": job_text}
@router.get("/match_resumes_by_job/{job_id}")
def match_resumes_by_job(
    job_id: int = Path(..., description="Job ID to match resumes for"),
    top_k: int = Query(10, description="Number of top resumes to return"),
    db: Session = Depends(get_db)
):
    """
    Fetch a job by job_id and find the top_k best matching resumes for it
    """
    # 1️⃣ Fetch job from database
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2️⃣ Build job_data dictionary (same as expected by match_resumes)
    job_data = {
        "job_role": job.job_role,
        "job_experience": job.job_experience,
        "job_overview": job.job_overview,
        "job_responsibilities": job.job_responsibilities,
        "job_requirements": job.job_requirements
    }

    # 3️⃣ Use embedding service to find matching resumes
    result = embedding_service.match_resumes(db, job_id, top_k)

    return result
@router.post("/create_job")
def create_job(job_data: dict, db: Session = Depends(get_db)):
    """
    Create a new job manually by passing job details in JSON body.
    """
    try:
        new_job = Job(
            job_role=job_data.get("job_role"),
            job_experience=job_data.get("job_experience"),
            job_overview=job_data.get("job_overview"),
            job_responsibilities=job_data.get("job_responsibilities"),
            job_requirements=job_data.get("job_requirements")
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        # ✅ Store embeddings for this job
        embedding_service.store_job_embeddings(db, [new_job])

        return {"message": "Job created successfully", "job": new_job}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
