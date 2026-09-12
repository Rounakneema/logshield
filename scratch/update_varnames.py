import sys
import glob
import os

html_dir = r"d:\LOGSHEILD\gitguardian_specific_detectors"
html_files = glob.glob(os.path.join(html_dir, "*.html"))

names_to_add = set()
for file in html_files:
    basename = os.path.basename(file).replace(".html", "")
    names_to_add.add(basename.lower())
    names_to_add.add(basename.replace("_", ""))

varname_file = r"d:\LOGSHEILD\sidecar\logmask\factors\varname_factor.py"
with open(varname_file, 'r', encoding='utf-8') as f:
    content = f.read()

# We'll just dump the new names into the set definition of HIGH_RISK_VARNAMES
new_lines = [f'        "{name}",' for name in names_to_add]

# find the end of HIGH_RISK_VARNAMES = { ... }
insert_idx = content.find('    }')
if insert_idx != -1:
    content = content[:insert_idx] + "\n        # auto-generated from 400+ detectors\n" + "\n".join(new_lines) + "\n" + content[insert_idx:]
    with open(varname_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Added {len(names_to_add)} varnames to varname_factor.py")
else:
    print("Could not find insertion point!")
