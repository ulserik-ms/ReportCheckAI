"""
ReportCheckAI - Main Entry Point
Orchestrates the loading, indexing, and auditing of EdTech reports.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from src.auditor import ComplianceAuditor
from src.config import RESULTS_PATH
from src.loader import load_all_documents
from src.vector_store import VectorIndex

load_dotenv()


def run_pipeline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data")

    print("--- Starting ReportCheckAI Pipeline ---")

    lib = load_all_documents(data_path)
    if not lib["rules"] or not lib["reports"]:
        print("Error: Missing data. Please run generate_data.py first.")
        return

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    v_store = VectorIndex(client=client)
    if v_store.load():
        print("Loaded existing FAISS index from disk.")
    else:
        print("Building FAISS index for compliance rules...")
        v_store.build_index(lib)

    auditor = ComplianceAuditor(v_store, client=client)

    print(f"\nProceeding to audit {len(lib['reports'])} reports...\n")
    print(f"{'FILENAME':<35} | {'STATUS':<10} | {'SUMMARY'}")
    print("-" * 90)

    results = []
    for report in lib["reports"]:
        if report["content"] is None:
            print(f"{report['filename']:<35} | {'ERROR':<10} | Could not extract PDF text.")
            results.append({"filename": report["filename"], "overall_status": "ERROR", "summary": "Could not extract PDF text."})
            continue

        raw_result = auditor.audit_report(report["content"])

        try:
            res = json.loads(raw_result)
        except json.JSONDecodeError:
            print(f"{report['filename']:<35} | {'ERROR':<10} | LLM returned malformed JSON.")
            results.append({"filename": report["filename"], "overall_status": "ERROR", "summary": "LLM returned malformed JSON."})
            continue

        status = res.get("overall_status", "N/A")
        summary = res.get("summary", "No summary provided.")
        print(f"{report['filename']:<35} | {status:<10} | {summary}")
        results.append({"filename": report["filename"], **res})

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    run_pipeline()
