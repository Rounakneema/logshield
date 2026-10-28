with open('ltls_report_rounak_neema/tune_report_pages.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's adjust fig_w slightly to 4.1 inches so figures don't push extra blank space
text = text.replace('def build_tuned_report(fig_w=4.3, p_after=2.5, p_space=1.12):',
                    'def build_tuned_report(fig_w=4.1, p_after=2, p_space=1.10):')

# Let's also ensure Chapter 8 and Chapter 9 fit neatly
text = text.replace('space_before=12, space_after=14', 'space_before=8, space_after=8')

with open('ltls_report_rounak_neema/tune_report_pages.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Tuned parameters saved")
