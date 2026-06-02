# ReportCheckAI: RAG-Powered EdTech Compliance Auditor

**ReportCheckAI** is a prototype automated auditing system designed for the Science EdTech sector.
It leverages **Retrieval-Augmented Generation (RAG)** to verify that expert content review reports (Grades 7-9) adhere to internal compliance standards and scientific accuracy.


## Project Overview
In EdTech, human experts review AI-generated educational content. To ensure these reviews are consistent and reliable, they must be audited against a "Compliance Handbook."

**This project solves two main problems:**
1. **Compliance Drift:** Ensuring auditors don't miss fields (like Contract IDs) or incorrect formats (dates/citations).
2. **Hallucination Control:** By using RAG, the LLM is grounded in reliable internal resources rather than relying on its internal training data.

## Why RAG?
Standard LLMs can struggle with specific, evolving internal rules. This system uses RAG because:
* **Reliable Resources:** It checks educational content against specific, vetted curriculum standards.
* **Deterministic Grounding:** It uses internal rule documents as a "Source of Truth" to verify report identity and structure.
* **Traceability:** The system retrieves the exact rule being violated before issuing a verdict.

## Technical Stack
* **Language:** Python 3.10+
* **LLM:** OpenAI `gpt-4o-mini`
* **Vector Store:** FAISS (Facebook AI Similarity Search)
* **Embeddings:** OpenAI `text-embedding-3-small`
* **PDF Processing:** PyMuPDF (`fitz`)

## Project Structure
```text
ReportCheckAI/
├── data/
│   ├── reports/           # Synthetic expert reports (PDF)
│   ├── rules/             # Compliance Handbook (PDF)
│   ├── faiss.index        # Persisted FAISS index (auto-generated)
│   ├── faiss_docs.json    # Persisted index documents (auto-generated)
│   └── results.json       # Audit results from the last pipeline run
├── src/
│   ├── config.py          # Central config: models, paths, audit queries
│   ├── loader.py          # PDF text extraction
│   ├── vector_store.py    # FAISS index and embedding logic
│   └── auditor.py         # LLM audit logic
├── main.py                # Pipeline orchestrator
├── generate_data.py       # Synthetic dataset generator
└── requirements.txt       # Project dependencies
```

## Pipeline Behaviour

1. **Load** — PDFs from `data/rules/` and `data/reports/` are extracted into plain text.
2. **Index** — Rule chunks are embedded and stored in a FAISS index. The index is persisted to `data/faiss.index` so subsequent runs skip re-embedding entirely.
3. **Audit** — For each report, six targeted RAG queries retrieve the most relevant rule chunks across every compliance dimension. The assembled context and report are sent to the LLM for a structured verdict.
4. **Output** — Results are printed to the console and written to `data/results.json`.

## Getting Started

### 1. Prerequisites
You will need an OpenAI API key. Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_api_key_here
```

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/ulserik-ms/ReportCheckAI.git
cd ReportCheckAI
pip install -r requirements.txt
```

### 3. Usage
Generate the synthetic test data (only needed once):
```bash
python generate_data.py
```

Run the full audit pipeline:
```bash
python main.py
```

On first run the FAISS index is built and saved to disk. Every subsequent run loads the cached index, so no embedding calls are made for the rules — only the reports are sent to the LLM.

Audit results are saved to `data/results.json` after each run for programmatic inspection.
