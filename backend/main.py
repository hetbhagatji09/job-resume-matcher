from fastapi import FastAPI
from routers import jobs
from database import Base,engine
from routers.resume_router import router as resume_router
app = FastAPI(title="Job Resume Matcher API")
Base.metadata.create_all(bind=engine)
# Register routers
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(resume_router,prefix="/api",tags=["resumes"])
