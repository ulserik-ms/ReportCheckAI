"""
ReportCheckAI - Loader Module
Responsible for extracting and structuring text from PDF reports and handbooks.
"""

import os
import fitz


def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text("text")
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error extracting {file_path}: {e}")
        return None


def load_all_documents(data_dir):
    library = {"rules": {}, "reports": []}

    rules_path = os.path.join(data_dir, "rules")
    if os.path.exists(rules_path):
        for file in sorted(os.listdir(rules_path)):
            if file.endswith(".pdf"):
                content = extract_text_from_pdf(os.path.join(rules_path, file))
                library["rules"][file] = content

    reports_path = os.path.join(data_dir, "reports")
    if os.path.exists(reports_path):
        for file in sorted(os.listdir(reports_path)):
            if file.endswith(".pdf"):
                content = extract_text_from_pdf(os.path.join(reports_path, file))
                library["reports"].append({
                    "filename": file,
                    "content": content,
                })

    return library


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data = load_all_documents(os.path.join(project_root, "data"))
    print(f"Loaded {len(data['rules'])} rule files and {len(data['reports'])} reports.")
