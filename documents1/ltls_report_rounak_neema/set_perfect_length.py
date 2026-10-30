import re

with open('ltls_report_rounak_neema/tune_report_pages.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Adjust margins to 0.75 in
text = text.replace('top_margin = Inches(0.8)', 'top_margin = Inches(0.75)')
text = text.replace('bottom_margin = Inches(0.8)', 'bottom_margin = Inches(0.75)')
text = text.replace('left_margin = Inches(0.85)', 'left_margin = Inches(0.8)')
text = text.replace('right_margin = Inches(0.85)', 'right_margin = Inches(0.8)')

# Adjust heading spacing
text = text.replace('p.paragraph_format.space_before = Pt(14)', 'p.paragraph_format.space_before = Pt(10)')
text = text.replace('p.paragraph_format.space_after = Pt(4)', 'p.paragraph_format.space_after = Pt(2)')
text = text.replace('p.paragraph_format.space_before = Pt(10)', 'p.paragraph_format.space_before = Pt(8)')
text = text.replace('p.paragraph_format.space_after = Pt(3)', 'p.paragraph_format.space_after = Pt(2)')

# In Chapter 9 references spacing
text = text.replace('space_before, p_r.paragraph_format.space_after = Pt(1), Pt(2)',
                    'space_before, p_r.paragraph_format.space_after = Pt(0.5), Pt(1)')

with open('ltls_report_rounak_neema/tune_report_pages.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated parameters for exact length")
