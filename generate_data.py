'''
This script automates the generation of a synthetic testing data for an AI-powered
compliance auditor. It simulates the workflow of a Science EdTech company (Grade 7-9)
where human experts review AI-generated content.

The script generates:
1. A formal Compliance Handbook (The Source of Truth).
2. A set of Expert Review Reports (2 'Pass', 2 'Fail') with intentional rule violations
   to test the accuracy of the RAG auditing system.
'''

import os
import fitz
from openai import OpenAI

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_text(prompt,temp=0.7):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=temp
    )
    return response.choices[0].message.content


def save_data(folder, filename, text):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{filename}.pdf")

    doc = fitz.open()
    page = doc.new_page()

    rect = fitz.Rect(50, 50, 550, 800)
    html_content = f"<p style='font-family:sans-serif; font-size:11pt; text-align:justify;'>{text.replace(chr(10), '<br>')}</p>"

    page.insert_htmlbox(rect, html_content)

    doc.save(file_path)
    doc.close()
    return file_path


# 1. Generate and save rules
rules_prompt = f"""
Create a 'Content Review Compliance Handbook' for an EdTech company. 
The handbook must list 6 strict requirements for expert review reports on Grade 7-9 Science content:

1. DATE: Must be in format DD/MM/YYYY.
2. IDENTITY: Full name of the expert, their institution (affiliation), and Contract ID.
3. SUBJECT: Must specify if the content is Physics, Chemistry, Biology, or Math.
4. CORRECTIONS: A detailed list of specific mistakes or inconsistencies found in the AI content.
5. REFERENCES: List of specific textbooks or scientific sources used to verify the corrections.
6. RECOMMENDATIONS: Clear pedagogical advice for improving the content for students.

Format this as a formal document.
Keep it under 300 words.
"""

print("Generating Compliance Rules...")
rules_content = generate_text(rules_prompt)
save_data("data/rules", "educational_compliance_rules", rules_content)

# 2. Generate 4 Synthetic Reports (2 Pass, 2 Fail)
input_data = {
    "expert_names": ["Adam Sach", "Julia Smith", "Bob Fisher", "Kate Goldman"],
    "affiliations": ["School-1", "School-2", "School-3", "School-4"],
    "contract_IDs": ["A-123", "B-456", "C-789", "D-012"],
    "grades": [8, 7, 8, 9],
    "subjects": ['physics', 'math', 'chemistry', 'biology'],
    "topics": ['Internal energy', 'Ratios and Proportions', 'Periodic Table', 'Photosynthesis and Respiration']
}

# 2. Define Scenarios
report_scenarios = [
    {"desc": "A perfect report satisfying all rules.", "label": "pass"},
    {"desc": "A faulty report where the 'References' section is entirely missing.", "label": "fail_missing_ref"},
    {"desc": "A faulty report where the Contract ID is missing and the date format is wrong.", "label": "fail_incomplete_id"},
    {"desc": "A perfect report satisfying all rules.", "label": "pass"}
]

for i, scenario in enumerate(report_scenarios):
    sub = input_data["subjects"][i]
    name = input_data["expert_names"][i]
    aff = input_data["affiliations"][i]
    cid = input_data["contract_IDs"][i]
    topic = input_data["topics"][i]
    grade = input_data["grades"][i]

    # date formatting
    day = (i + 1) * 2
    fake_date = f"{day:02d}/02/2025"

    # Generate 2 specific fake references for this subject
    ref_list = [f"{sub}_book-{j}" for j in range(1, 3)]

    print(f"Generating Report {i + 1}: {scenario['label']}...")

    prompt = f"""
    Act as a Subject Matter Expert for an EdTech company. 
    TASK: Write a formal 'Content Review Report'.
    SCENARIO: {scenario['desc']}

    REPORT DATA (Use these unless the SCENARIO requires omission):
    - TITLE: {sub.capitalize()} Content Review Report
    - EXPERT: {name}
    - AFFILIATION: {aff}
    - CONTRACT ID: {cid}
    - DATE: {fake_date}
    - GRADE: {grade}
    - TOPIC: {topic}
    - REFERENCES TO USE: {', '.join(ref_list)}

    STRUCTURE:
    - SECTION 1: Executive Summary. Provide a brief overview of the {topic} content.
    - SECTION 2: Detailed Corrections. List 2-3 technical mistakes found in the AI content.
    - SECTION 3: Verification References. List the specific references provided above.
    - SECTION 4: Pedagogical Recommendations. How to improve the lesson for Grade {grade} students.

    STRICT RULES:
    1. If the SCENARIO says the report is 'faulty' or 'missing' a section, you MUST omit that section.
    2. Maintain a professional, critical, and academic tone.
    3. Keep the total length under 300 words.
    """

    content = generate_text(prompt)
    save_data("data/reports", f"report_{i + 1}_{scenario['label']}", content)

print("\nDone! Check the 'data/' folder.")