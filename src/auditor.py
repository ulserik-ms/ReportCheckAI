"""
Auditor Module for ReportCheckAI.
Performs the actual compliance check using RAG (Retrieved Rules + LLM).
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from src.config import CHAT_MODEL

load_dotenv()

_AUDIT_QUERIES = [
    "expert identity full name institution affiliation Contract ID",
    "date format DD/MM/YYYY requirement",
    "references textbooks scientific sources verification",
    "corrections mistakes inconsistencies detailed list",
    "subject specification Physics Chemistry Biology Math",
    "recommendations pedagogical advice improving content",
]


class ComplianceAuditor:
    def __init__(self, vector_store):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_store = vector_store

    def _retrieve_rules(self, n_results=2):
        """
        Runs one targeted search per compliance dimension and deduplicates results.
        This ensures every rule area is represented in the context, not just the
        ones that happen to be closest to the full report embedding.
        """
        seen = set()
        chunks = []
        for query in _AUDIT_QUERIES:
            for chunk in self.vector_store.search(query, n_results=n_results):
                if chunk not in seen:
                    seen.add(chunk)
                    chunks.append(chunk)
        return chunks

    def audit_report(self, report_content):
        if not report_content:
            raise ValueError("Report content is empty or None.")

        rules_chunks = self._retrieve_rules()
        rules_context = "\n\n---\n\n".join(rules_chunks) if rules_chunks else "No specific rules found."

        prompt = f"""
        You are an automated Compliance Auditor for an EdTech company.
        Your task is to verify if a 'Content Review Report' follows the official 'Compliance Handbook'.

        ### OFFICIAL COMPLIANCE RULES:
        {rules_context}

        ### REPORT TO AUDIT:
        {report_content}

        ### INSTRUCTIONS:
        - Check if the report follows every rule in the handbook.
        - Pay close attention to Identity (Contract ID), Date format (DD/MM/YYYY), and References.
        - Identify any missing sections or formatting errors.

        ### OUTPUT FORMAT (JSON):
        {{
          "overall_status": "PASS" or "FAIL",
          "violations": ["List specific rules broken, or 'None'"],
          "summary": "Short explanation of the audit result"
        }}
        """

        response = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a strict compliance auditor."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    from src.loader import load_all_documents
    from src.vector_store import VectorIndex

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib = load_all_documents(os.path.join(project_root, "data"))

    v_store = VectorIndex()
    v_store.build_index(lib)

    if lib["reports"]:
        auditor = ComplianceAuditor(v_store)
        report = lib["reports"][0]
        print(f"\nAuditing: {report['filename']}...")
        print(auditor.audit_report(report["content"]))
