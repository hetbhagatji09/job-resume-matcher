import os
from sentence_transformers import SentenceTransformer

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "FineTuneModel")

model = SentenceTransformer(model_path)
