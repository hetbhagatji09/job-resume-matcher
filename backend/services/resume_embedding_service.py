from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy.orm import Session
from langchain_community.embeddings import HuggingFaceEmbeddings
from models.resume_embedding_model import ResumeEmbedding
from models.resume_model import Resume
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import re
import json

# Load environment variables
load_dotenv()

# Initialize Groq model (LLaMA 3.1)
llm = ChatGroq(
    temperature=0.3,
    model_name="llama-3.1-8b-instant"
)

# Import your huggingface embedding model from utils
from utills.hugmodel import model


class ResumeEmbeddingService:
    def __init__(self):
        # Initialize embeddings model (local)
        self.embeddings = model

    def store_resume_embedding(self, db: Session, resume: Resume):
        """
        Generate and store embedding for a single resume
        after cleaning all unwanted symbols/brackets for better embedding quality
        """
        if not resume:
            return {"status": "error", "message": "No resume provided"}

        # --- Helper to safely convert JSON/text fields ---
        def safe_load(val):
            try:
                loaded = json.loads(val)
                if isinstance(loaded, list):
                    return " ".join(map(str, loaded))
                elif isinstance(loaded, dict):
                    return " ".join(map(str, loaded.values()))
                else:
                    return str(loaded)
            except:
                return str(val or "")

        # --- Extract fields ---
        skills = safe_load(resume.skills)
        education = safe_load(resume.education)
        experience = safe_load(resume.experience)
        projects = safe_load(resume.projects)
        certifications = safe_load(resume.certifications)

        # --- Combine all text fields ---
        resume_text = (
            str(skills).replace("{"," ").replace("}"," ").replace("["," ").replace("]"," ").replace("\""," ").replace("'"," ").replace("\\"," ")
            + " " +
            str(experience).replace("{"," ").replace("}"," ").replace("["," ").replace("]"," ").replace("\""," ").replace("'"," ").replace("\\"," ")
            + " " +
            str(projects).replace("{"," ").replace("}"," ").replace("["," ").replace("]"," ").replace("\""," ").replace("'"," ").replace("\\"," ")
            + " " +
            str(certifications).replace("{"," ").replace("}"," ").replace("["," ").replace("]"," ").replace("\""," ").replace("'"," ").replace("\\"," ")
            + " " +
            str(education).replace("{"," ").replace("}"," ").replace("["," ").replace("]"," ").replace("\""," ").replace("'"," ").replace("\\"," ")
        )

        # --- 🧹 Clean the text ---
       
        
        clean_text = re.sub(r"\s+", " ", resume_text).strip()  # collapse multiple spaces
        print(clean_text)

        if not clean_text:
            return {"status": "error", "message": "Empty cleaned resume text"}

        # --- ✅ Generate vector ---
        vector = self.embeddings.encode(clean_text, convert_to_numpy=True)

        # --- ✅ Store in DB ---
        resume_vector_entry = ResumeEmbedding(
            resume_id=resume.id,
            resume_vector=vector
        )
        db.add(resume_vector_entry)
        db.commit()

        print(f"✅ Stored clean resume embedding for {resume.name}")
        return {"status": "success", "resume_id": resume.id}
