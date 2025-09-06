from fastapi import FastAPI
from routers import jobs
from database import Base,engine

app = FastAPI(title="Job Resume Matcher API")
Base.metadata.create_all(bind=engine)
# Register routers
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
