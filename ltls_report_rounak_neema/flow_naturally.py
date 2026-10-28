with open('ltls_report_rounak_neema/tune_report_pages.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's remove forced page breaks on Chapter 2, Chapter 5, Chapter 8, Chapter 9
text = text.replace('add_heading_1("CHAPTER 2: THEORETICAL FOUNDATIONS AND CONCEPTUAL FRAMEWORKS", page_break=True)',
                    'add_heading_1("CHAPTER 2: THEORETICAL FOUNDATIONS AND CONCEPTUAL FRAMEWORKS", page_break=False)')

text = text.replace('add_heading_1("CHAPTER 5: EMPIRICAL FINDINGS: IN-DEPTH JOHARI WINDOW ASSESSMENT", page_break=True)',
                    'add_heading_1("CHAPTER 5: EMPIRICAL FINDINGS: IN-DEPTH JOHARI WINDOW ASSESSMENT", page_break=False)')

text = text.replace('add_heading_1("CHAPTER 8: CONCLUSION AND TRANSFORMATIVE COMMITMENTS", page_break=True)',
                    'add_heading_1("CHAPTER 8: CONCLUSION AND TRANSFORMATIVE COMMITMENTS", page_break=False)')

with open('ltls_report_rounak_neema/tune_report_pages.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Flow updated")
