import spacy
import PyPDF2

# ✅ Load your trained spaCy model
nlp = spacy.load(r"ner_models\content\education_ruler_model")

# ✅ Read PDF
with open('data/Bank Relationship Manager.pdf', 'rb') as pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(reader.pages)
    print(f"Number of pages: {num_pages}")

    # Extract text from all pages
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

# ✅ Process the text using spaCy
doc = nlp(text)

# ✅ Print detected entities
for ent in doc.ents:
    print(ent.text, "->", ent.label_)
