"""
ReportCheckAI - Main Entry Point
Orchestrates the loading, indexing, and auditing of EdTech reports.
"""

import os
import json
from dotenv import load_dotenv
from src.loader import load_all_documents
from src.vector_store import VectorIndex
from src.auditor import ComplianceAuditor

load_dotenv()


def run_pipeline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data")

    print("--- Starting ReportCheckAI Pipeline ---")

    lib = load_all_documents(data_path)
    if not lib["rules"] or not lib["reports"]:
        print("Error: Missing data. Please run generate_data.py first.")
        return

    print("Building FAISS index for compliance rules...")
    v_store = VectorIndex()
    v_store.build_index(lib)

    auditor = ComplianceAuditor(v_store)

    print(f"\nProceeding to audit {len(lib['reports'])} reports...\n")
    print(f"{'FILENAME':<35} | {'STATUS':<10} | {'SUMMARY'}")
    print("-" * 90)

    for report in lib["reports"]:
        if report["content"] is None:
            print(f"{report['filename']:<35} | {'ERROR':<10} | Could not extract PDF text.")
            continue

        raw_result = auditor.audit_report(report["content"])

        try:
            res = json.loads(raw_result)
        except json.JSONDecodeError:
            print(f"{report['filename']:<35} | {'ERROR':<10} | LLM returned malformed JSON.")
            continue

        status = res.get("overall_status", "N/A")
        summary = res.get("summary", "No summary provided.")
        print(f"{report['filename']:<35} | {status:<10} | {summary}")


if __name__ == "__main__":
    run_pipeline()
