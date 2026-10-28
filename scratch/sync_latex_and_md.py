import re

# 1. Update LaTeX file
with open('paper/logshield_ieee_paper.tex', 'r', encoding='utf-8') as f:
    tex = f.read()

# Replace title & author
old_author_pattern = r'\\title\{LogShield: In-Pod Secret Sanitization and Autonomous Closed-Loop Containment for Kubernetes Log Streams.*?\\maketitle'
new_author_latex = r'''\title{LogShield: In-Pod Secret Sanitization and Autonomous Closed-Loop Containment for Kubernetes Log Streams}

\author{\IEEEauthorblockN{Rounak Neema\IEEEauthorrefmark{1}, Manas Borse\IEEEauthorrefmark{1}, Arnab Chowdhury\IEEEauthorrefmark{1}, Prince Roy\IEEEauthorrefmark{1}, Rudrani Ingle\IEEEauthorrefmark{2}}
\IEEEauthorblockA{\textit{Department of Computer Engineering} \\
\textit{Mukesh Patel School of Technology Management \& Engineering, NMIMS University} \\
Mumbai, India \\
\IEEEauthorrefmark{1}\{rounak.neema046, manas.borse057, arnab.chowdhury032, prince.roy031\}@nmims.in, \IEEEauthorrefmark{2}Rudrani.Ingle@nmims.edu}
}

\maketitle'''

tex_updated = re.sub(old_author_pattern, lambda m: new_author_latex, tex, flags=re.DOTALL)

# Replace Acknowledgment
old_ack_pattern = r'\\section\*\{Acknowledgment\}\s*.*?(?=\\balance|\\bibliographystyle)'
new_ack_latex = r'''\section*{Acknowledgment}
The authors thank the maintainers of SecretBench, TruffleHog, and Gitleaks for open-sourcing their detection datasets and rule engines. We also thank the Department of Computer Engineering at NMIMS University for providing computing facilities and laboratory infrastructure for our Kubernetes testbed cluster.

'''

tex_updated = re.sub(old_ack_pattern, lambda m: new_ack_latex, tex_updated, flags=re.DOTALL)

with open('paper/logshield_ieee_paper.tex', 'w', encoding='utf-8') as f:
    f.write(tex_updated)
print("Updated paper/logshield_ieee_paper.tex successfully")

# 2. Update Markdown file
with open('paper/logshield_ieee_paper.md', 'r', encoding='utf-8') as f:
    md = f.read()

# Remove capstone note in md
md_updated = re.sub(r'This study was conducted as part of the Capstone Project.*?\n\n', '', md)

# Update author block in md
new_md_auth = '''**Rounak Neema**, **Manas Borse**, **Arnab Chowdhury**, **Prince Roy**, and **Rudrani Ingle**  
Department of Computer Engineering, Mukesh Patel School of Technology Management & Engineering  
NMIMS University, Mumbai, India  
`{rounak.neema046, manas.borse057, arnab.chowdhury032, prince.roy031}@nmims.in`, `Rudrani.Ingle@nmims.edu`

'''
md_updated = re.sub(r'Rounak Neema\s*\n\s*Department of Computer Engineering.*?(?=Abstract—)', lambda m: new_md_auth, md_updated, flags=re.DOTALL)

# Update Acknowledgment in md
new_ack_md = '''ACKNOWLEDGMENT

The authors thank the maintainers of SecretBench, TruffleHog, and Gitleaks for open-sourcing their detection datasets and rule engines. We also thank the Department of Computer Engineering at NMIMS University for providing computing facilities and laboratory infrastructure for our Kubernetes testbed cluster.

'''
md_updated = re.sub(r'ACKNOWLEDGMENT\s*\n\s*The authors thank.*?(?=REFERENCES)', lambda m: new_ack_md, md_updated, flags=re.DOTALL)

with open('paper/logshield_ieee_paper.md', 'w', encoding='utf-8') as f:
    f.write(md_updated)
print("Updated paper/logshield_ieee_paper.md successfully")
