# job-resume-match

A powerful backend system built with **FastAPI**, **LangChain**, **Selenium**, **pgvector**, and **vector embeddings** to intelligently match job descriptions with resumes.  
It supports text extraction, embedding generation, similarity search, scraping tools, and robust database storage using PostgreSQL.

---

## 🚀 Getting Started

Follow the steps below to set up and run the backend locally.

---

## 1️⃣ Navigate to the backend folder

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

