"""
ReportCheckAI - Main Entry Point
Orchestrates the loading, indexing, and auditing of EdTech reports.
"""

import os
from src.loader import load_all_documents
from src.vector_store import VectorIndex
from src.auditor import ComplianceAuditor


def run_pipeline():
    # 1. Setup Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data")

    print("--- Starting ReportCheckAI Pipeline ---")

    # 2. Load Documents
    lib = load_all_documents(data_path)
    if not lib["rules"] or not lib["reports"]:
        print("Error: Missing data. Please run generate_data.py first.")
        return

    # 3. Build Vector Store (FAISS + OpenAI)
    print("Building FAISS index for compliance rules...")
    v_store = VectorIndex()
    v_store.build_index(lib)

    # 4. Initialize Auditor
    auditor = ComplianceAuditor(v_store)

    # 5. Process and Audit each Report
    print(f"\nProceeding to audit {len(lib['reports'])} reports...\n")
    print(f"{'FILENAME':<30} | {'STATUS':<10} | {'SUMMARY'}")
    print("-" * 80)

    for report in lib["reports"]:
        # Run the audit
        raw_result = auditor.audit_report(report['content'])

        # Parse the JSON string from the auditor
        import json
        res = json.loads(raw_result)

        # Display clean summary
        status = res.get("overall_status", "N/A")
        summary = res.get("summary", "No summary provided.")
        print(f"{report['filename']:<30} | {status:<10} | {summary}")


if __name__ == "__main__":
    run_pipeline()