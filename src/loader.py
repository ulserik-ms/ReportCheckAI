"""
ReportCheckAI - Loader Module
Responsible for extracting and structuring text from PDF reports and handbooks.
"""

import os
import fitz

def extract_text_from_pdf(file_path):
    """
    Opens a PDF and returns the full text as a string.
    """
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text("text")  # "text" ensures standard layout extraction
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error extracting {file_path}: {e}")
        return None


def load_all_documents(data_dir):
    """
    Scans rules and reports folders to build a structured library.
    """
    library = {"rules": {}, "reports": []}

    # 1. Load Compliance Rules (The Handbook)
    rules_path = os.path.join(data_dir, "rules")
    if os.path.exists(rules_path):
        for file in os.listdir(rules_path):
            if file.endswith(".pdf"):
                content = extract_text_from_pdf(os.path.join(rules_path, file))
                library["rules"][file] = content

    # 2. Load Reports (The Audit Subjects)
    reports_path = os.path.join(data_dir, "reports")
    if os.path.exists(reports_path):
        for file in os.listdir(reports_path):
            if file.endswith(".pdf"):
                content = extract_text_from_pdf(os.path.join(reports_path, file))
                library["reports"].append({
                    "filename": file,
                    "content": content
                })

    return library


if __name__ == "__main__":
    # Quick Verification
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    base_data = os.path.join(project_root, "data")

    print(f"Searching for data in: {base_data}")

    data = load_all_documents(base_data)
    print(f"Loaded {len(data['rules'])} rule files and {len(data['reports'])} reports.")