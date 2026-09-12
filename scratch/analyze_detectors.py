import os
import re
import sys
import glob

# Add logshield to path to import catalog
sys.path.insert(0, r"d:\LOGSHEILD")
try:
    from sidecar.logmask.catalog import ALL_SPECIFIC_DETECTORS
    implemented_names = {d[1].lower() for d in ALL_SPECIFIC_DETECTORS}
except Exception as e:
    print(f"Error importing catalog: {e}")
    implemented_names = set()

html_dir = r"d:\LOGSHEILD\gitguardian_specific_detectors"
html_files = glob.glob(os.path.join(html_dir, "*.html"))

target_detectors = set()
for file in html_files:
    basename = os.path.basename(file).replace(".html", "")
    # naive name parsing
    name = basename.replace("_", " ").title()
    target_detectors.add(name.lower())
    
missing = target_detectors - implemented_names
print(f"Total HTML files: {len(html_files)}")
print(f"Total implemented detectors: {len(implemented_names)}")
print(f"Total target detectors: {len(target_detectors)}")
print(f"Total missing detectors: {len(missing)}")
print("\nSample missing detectors:")
for m in list(missing)[:20]:
    print(f" - {m}")

# Also try to extract any <code> blocks from one of the files to see if prefixes are there
import html
with open(html_files[0], 'r', encoding='utf-8') as f:
    content = f.read()
    codes = re.findall(r'<code[^>]*>(.*?)</code>', content, re.DOTALL | re.IGNORECASE)
    print("\nCode blocks in first file:")
    for c in codes[:5]:
        print(" ->", html.unescape(c))
