with open('ltls_report_rounak_neema/tune_report_pages.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Make figure width 3.7 inches so figures fit comfortably alongside tables and text without pushing single paragraphs over page breaks
text = text.replace('def build_tuned_report(fig_w=4.1, p_after=2, p_space=1.10):',
                    'def build_tuned_report(fig_w=3.7, p_after=2, p_space=1.10):')

with open('ltls_report_rounak_neema/tune_report_pages.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Tuned fig_w to 3.7")
