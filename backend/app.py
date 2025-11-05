from sentence_transformers import SentenceTransformer
model=SentenceTransformer("hetbhagatji09/Job-resume-match-model")


# --- Hard Triplet for Java Developer ---

# 1. Define the anchor, a matching positive, and a tricky "hard" negative
anchor = "Seeking an experienced Java Developer to design and build high-performance, scalable backend services. The role involves developing RESTful APIs using the Spring Boot framework, working with microservices architecture, and integrating with PostgreSQL databases. The ideal candidate will have a strong understanding of object-oriented principles, experience with JPA/Hibernate, and a commitment to writing clean, testable code."

positive = "A results-oriented Java Developer with extensive experience in building robust backend systems using the Spring Boot framework. Proficient in designing and implementing RESTful APIs for microservices, with deep expertise in data persistence using JPA and Hibernate with PostgreSQL. Committed to best practices in software development, including TDD and agile methodologies."

negative = "An accomplished Mobile Application Developer with a strong proficiency in Java and the Android SDK. Specialized in creating responsive and user-friendly native Android apps, with experience in managing application lifecycles, integrating third-party libraries, and publishing on the Google Play Store. My focus is on mobile-first design and performance optimization."

# 2. Encode the text into tensor embeddings
# (This assumes your 'model' object is already loaded)
emb_anchor = model.encode(anchor, convert_to_tensor=True)
emb_positive = model.encode(positive, convert_to_tensor=True)
emb_negative = model.encode(negative, convert_to_tensor=True)

# 3. Calculate and print the cosine similarity scores
from sentence_transformers.util import cos_sim

print("Anchor (Java Dev) vs Positive:", cos_sim(emb_anchor, emb_positive).item())
print("Anchor (Java Dev) vs Hard Negative (Android Dev):", cos_sim(emb_anchor, emb_negative).item())