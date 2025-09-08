from fastapi import APIRouter, Query, HTTPException,Depends
from database import get_db
from services.scraper_service import scrape_jobs
from sqlalchemy.orm import Session
from crud.job_crud import create_jobs
from database import SessionLocal
from services.job_embedding_service import JobEmbeddingService
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