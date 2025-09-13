from fastapi import APIRouter, Query, HTTPException,Depends,Path
from database import get_db
from services.scraper_service import scrape_jobs
from sqlalchemy.orm import Session
from models.job import Job
from crud.job_crud import create_jobs,create_job
from database import SessionLocal
from services.job_embedding_service import JobEmbeddingService
from schema.JobCreate import JobCreate
router = APIRouter()


embedding_service = JobEmbeddingService()

@router.get("/jobs")
def get_jobs(url: str = Query(..., description="Website URL to scrape jobs from")):
    try:
        jobs =scrape_jobs(url)
        db: Session = SessionLocal()
        job_entries = create_jobs(db, jobs)
        embedding_service.store_job_embeddings(db, job_entries)
        db.close()
        #return {"url": url, "total_jobs": len(jobs), "jobs": jobs}
        return job_entries
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scraped")
def getget_scrapedjobs(url: str = Query(..., description="Website URL to scrape jobs from")):
    jobs =scrape_jobs(url)
    print(jobs)
    return jobs

@router.get("/jobs/{job_id}/match_resumes")
async def match_resumes_for_job(
    job_id: int = Path(..., description="Job ID to match resumes against"),
    top_k: int = Query(5, description="Number of resumes to return"),
    db: Session = Depends(get_db)
):
    """
    Match resumes for a given job (by job_id)
    """
    # 1️⃣ Get job from DB
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # 2️⃣ Pass the job object directly to the service
    return embedding_service.match_resumes(db, job_id, top_k)
@router.post("/jobs")
def create_job_endpoint(job_data: JobCreate, db: Session = Depends(get_db)):
    try:
        # 1️⃣ Save job in DB
        job = create_job(db, job_data.dict())

        # 2️⃣ Store embeddings
        embedding_service.store_job_embeddings(db, [job])

        return {"status": "success", "job_id": job.id, "job": job_data.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))