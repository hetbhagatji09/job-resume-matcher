from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://bunny0901:0901@localhost:5434/job-resume-match?sslmode=disable"


engine = create_engine(DATABASE_URL,echo=True   )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
