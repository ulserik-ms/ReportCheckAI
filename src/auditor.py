"""
Auditor Module for ReportCheckAI.
Performs the actual compliance check using RAG (Retrieved Rules + LLM).
"""

from openai import OpenAI
import os


class ComplianceAuditor:
    def __init__(self, vector_store):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_store = vector_store

    def audit_report(self, report_content):
        """
        Retrieves relevant rules and checks the report against them.
        """
        # 1. Retrieve the rules from FAISS (RAG step)
        # We query the vector store using the report's content to find applicable rules
        relevant_rules = self.vector_store.search(report_content, n_results=1)
        rules_context = relevant_rules[0] if relevant_rules else "No specific rules found."

        # 2. Construct the Audit Prompt
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

        # 3. Call the LLM for the verdict
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a strict compliance auditor."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}  # Ensures we get clean JSON
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    # Integration test with your loader and vector store
    from loader import load_all_documents
    from vector_store import VectorIndex

    # Load data
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib = load_all_documents(os.path.join(project_root, "data"))

    # Setup Vector Store
    v_store = VectorIndex()
    v_store.build_index(lib)

    # Audit the first report
    if lib["reports"]:
        auditor = ComplianceAuditor(v_store)
        report = lib["reports"][0]
        print(f"\nAuditing: {report['filename']}...")
        result = auditor.audit_report(report['content'])
        print(result)