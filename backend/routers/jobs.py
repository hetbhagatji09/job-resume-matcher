from fastapi import APIRouter, Query, HTTPException
from services.scraper_service import scrape_jobs
from sqlalchemy.orm import Session
from crud.job_crud import create_jobs
from database import SessionLocal
router = APIRouter()


@router.get("/jobs")
def get_jobs(url: str = Query(..., description="Website URL to scrape jobs from")):
    try:
        jobs =scrape_jobs(url)
        db: Session = SessionLocal()
        job_entries = create_jobs(db, jobs)
        db.close()
        # return {"url": url, "total_jobs": len(jobs), "jobs": jobs}
        return jobs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
