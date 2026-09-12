import os
import sys
import glob
import re

sys.path.insert(0, r"d:\LOGSHEILD")
try:
    from sidecar.logmask.catalog import ALL_SPECIFIC_DETECTORS
    implemented_names = {d[1].lower() for d in ALL_SPECIFIC_DETECTORS if d[3] != 'generated'} 
    # exclude the ones we just generated so we can overwrite them
except Exception as e:
    print(f"Error importing catalog: {e}")
    implemented_names = set()

# Wait, we want to exclude anything that is currently in generated_specifics.py 
# from the 'implemented_names' set, so we can re-generate them.
# The easiest way is to just use a hardcoded set of the core ones, or since ALL_SPECIFIC_DETECTORS 
# currently includes the generated ones, we can just regenerate everything that was missing initially.
# Actually, the original missing count was 401. Let's just regenerate all 464, but only output 
# the ones that are NOT in the original core categories. 
# Better: just read ALL_SPECIFIC_DETECTORS from the original files if possible, 
# but they are merged in __init__.py. 

html_dir = r"d:\LOGSHEILD\gitguardian_specific_detectors"
html_files = glob.glob(os.path.join(html_dir, "*.html"))

generated_code = [
    '"""',
    'Generated Specific Detectors V2',
    '================================',
    'Auto-generated from 464 specific detector profiles using exact HTML metadata.',
    'Uses KV-bound regexes to prevent Pass 2 False Positives.',
    '"""',
    '',
    'import re',
    '',
    'GENERATED_SPECIFIC_DETECTORS = ['
]

def extract_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    text = re.sub('<[^<]+>', ' ', content)
    text = re.sub('\s+', ' ', text)
    
    meta = {
        'Category': 'generic',
        'Company': 'Unknown',
        'High recall': 'False'
    }
    
    cat_m = re.search(r'Category:\s*(\S+)', text)
    comp_m = re.search(r'Company:\s*([A-Za-z0-9\-]+)', text)
    recall_m = re.search(r'High recall:\s*(True|False)', text, re.IGNORECASE)
    
    if cat_m: meta['Category'] = cat_m.group(1).lower()
    if comp_m: meta['Company'] = comp_m.group(1)
    if recall_m: meta['High recall'] = recall_m.group(1)
    
    return meta

# Original core detectors (heuristically excluding generated ones by looking at the source)
core_detectors = set()
for m in ["ai", "cloud", "database", "messaging", "payment", "private_keys", "vcs_cicd"]:
    try:
        mod = __import__(f"sidecar.logmask.catalog.{m}", fromlist=["*"])
        for var in dir(mod):
            if var.endswith("_DETECTORS"):
                for entry in getattr(mod, var):
                    core_detectors.add(entry[1].lower())
    except:
        pass

missing_count = 0
for file in html_files:
    basename = os.path.basename(file).replace(".html", "")
    name = basename.replace("_", " ").title()
    
    if name.lower() in core_detectors:
        continue
        
    missing_count += 1
    meta = extract_metadata(file)
    
    cat = meta['Category']
    company = meta['Company']
    confidence = 0.85 if meta['High recall'].lower() == 'true' else 0.80
    
    var_prefix = basename.replace("_", ".*?")
    pattern = f'(?i)(?:{var_prefix})[\\s=:]+([a-zA-Z0-9_\\-]{{16,}})'
    
    line = f'    (re.compile(r"{pattern}"), "{name}", "{company}", "{cat}", {confidence}),'
    generated_code.append(line)

generated_code.append(']')
generated_code.append('')

out_path = r"d:\LOGSHEILD\sidecar\logmask\catalog\generated_specifics.py"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(generated_code))
    
print(f"Generated {missing_count} metadata-accurate detectors to {out_path}")
