with open('ltls_report_rounak_neema/tune_report_pages.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's remove page break for Chapter 9
text = text.replace('add_heading_1("CHAPTER 9: ACADEMIC REFERENCES AND APPENDICES", page_break=True)',
                    'add_heading_1("CHAPTER 9: ACADEMIC REFERENCES AND APPENDICES", page_break=False)')

with open('ltls_report_rounak_neema/tune_report_pages.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced successfully")
