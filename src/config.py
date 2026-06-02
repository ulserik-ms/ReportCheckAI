import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
FAISS_INDEX_PATH = os.path.join(_PROJECT_ROOT, "data", "faiss.index")
FAISS_DOCS_PATH = os.path.join(_PROJECT_ROOT, "data", "faiss_docs.json")
RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.json")
MAX_REPORT_CHARS = 8_000

AUDIT_QUERIES = [
    "expert identity full name institution affiliation Contract ID",
    "date format DD/MM/YYYY requirement",
    "references textbooks scientific sources verification",
    "corrections mistakes inconsistencies detailed list",
    "subject specification Physics Chemistry Biology Math",
    "recommendations pedagogical advice improving content",
]
