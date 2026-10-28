import re
from sort_references import sorted_refs, old_to_new

# Build clean BibTeX/LaTeX \bibitem entries for all 38 references
tex_bib_entries = []
for idx, r in enumerate(sorted_refs, 1):
    # Create key
    author_first = r["authors"].split(",")[0].split()[-1].lower()
    title_word = re.findall(r'[A-Za-z]+', r["title"])[0].lower()
    key = f"{author_first}{r['year']}{title_word}"
    
    # Clean citation for LaTeX
    c = r["citation"]
    # Replace quotes
    c = re.sub(r'"([^"]*)"', r"``\1,''", c)
    c = c.replace("&", r"\&")
    
    entry = f"\\bibitem{{{key}}}\n{c}\n"
    tex_bib_entries.append(entry)

new_bib_body = "\\begin{thebibliography}{00}\n\n" + "\n".join(tex_bib_entries) + "\\end{thebibliography}\n"

with open(r'd:\LOGSHEILD\paper\logshield_ieee_paper.tex', 'r', encoding='utf-8') as f:
    tex = f.read()

bib_start = tex.find('\\begin{thebibliography}')
if bib_start != -1:
    tex_new = tex[:bib_start] + new_bib_body + "\n\\end{document}\n"
    with open(r'd:\LOGSHEILD\paper\logshield_ieee_paper.tex', 'w', encoding='utf-8') as f:
        f.write(tex_new)
    print("Updated paper/logshield_ieee_paper.tex with 38 chronologically sorted references!")
