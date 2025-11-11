# from sentence_transformers import SentenceTransformer
# model=SentenceTransformer("hetbhagatji09/Job-resume-match-model")


# # --- Hard Triplet for Java Developer ---

# # 1. Define the anchor, a matching positive, and a tricky "hard" negative
# anchor = "Job Title: Software Engineer (.NET Full stack) Job Experience: 3+ years Job Overview: Build scalable, distributed applications using .NET and React. Job Responsibilities: Design, code, and maintain web apps using C# and JavaScript. Job Requirements: Strong knowledge of .NET, REST APIs, React, and SQL databases."

# positive = "Software Engineer with 4 years of experience in building scalable, distributed applications using .NET and React. Proficient in designing, coding, and maintaining web applications using C# and JavaScript. Successfully delivered multiple projects, including a microservices-based e-commerce platform and a data analytics dashboard. Strong knowledge of .NET, REST APIs, React, and SQL databases, with experience in Azure DevOps, Git, and Agile development methodologies. Proficient in JavaScript frameworks like Redux and React Hooks, and database systems like MySQL and PostgreSQL. Excellent problem-solving skills, with strong communication and collaboration abilities. Notable project: Developed a microservices-based e-commerce platform using .NET Core, React, and SQL Server, resulting in a 30% increase in sales and a 25% reduction in response time. Utilized Azure DevOps for continuous integration and deployment, and implemented caching and load balancing for improved performance. Obtained the Microsoft Certified: Azure Developer Associate certification, demonstrating expertise in developing cloud-based applications using .NET and Azure services. Bachelor of Science in Computer Science from the University of Illinois at Urbana-Champaign, with a GPA of 3.5 and a thesis on Designing Scalable Cloud Architectures for E-commerce Applications."
# negative = "An accomplished Mobile Application Developer with a strong proficiency in Java and the Android SDK. Specialized in creating responsive and user-friendly native Android apps, with experience in managing application lifecycles, integrating third-party libraries, and publishing on the Google Play Store. My focus is on mobile-first design and performance optimization."

# # 2. Encode the text into tensor embeddings
# # (This assumes your 'model' object is already loaded)
# emb_anchor = model.encode(anchor, convert_to_tensor=True)
# emb_positive = model.encode(positive, convert_to_tensor=True)
# emb_negative = model.encode(negative, convert_to_tensor=True)

# # 3. Calculate and print the cosine similarity scores
# from sentence_transformers.util import cos_sim

# print("Anchor (Java Dev) vs Positive:", cos_sim(emb_anchor, emb_positive).item())
# print("Anchor (Java Dev) vs Hard Negative (Android Dev):", cos_sim(emb_anchor, emb_negative).item())
from playwright.sync_api import sync_playwright
from selectorlib import Extractor
import json

# Load YAML config (make sure you name it jeavio.yml)
extractor = Extractor.from_yaml_file("scraper/motadata.yml")

url = "https://www.motadata.com/careers/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_timeout(15000)  # wait for JS to load content fully
    html = page.content()
    browser.close()

data = extractor.extract(html)
print(json.dumps(data, indent=2, ensure_ascii=False))
