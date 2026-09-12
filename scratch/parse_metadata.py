import os
import glob
import re

html_dir = r"d:\LOGSHEILD\gitguardian_specific_detectors"
html_files = glob.glob(os.path.join(html_dir, "*.html"))

def extract_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    text = re.sub('<[^<]+>', ' ', content)
    text = re.sub('\s+', ' ', text)
    
    meta = {}
    
    # Try to extract the structured fields
    family_match = re.search(r'Family:\s*(\S+)', text)
    category_match = re.search(r'Category:\s*(\S+)', text)
    company_match = re.search(r'Company:\s*(\S+)', text)
    prefixed_match = re.search(r'Prefixed:\s*(True|False)', text, re.IGNORECASE)
    
    if family_match: meta['Family'] = family_match.group(1)
    if category_match: meta['Category'] = category_match.group(1)
    if company_match: meta['Company'] = company_match.group(1)
    if prefixed_match: meta['Prefixed'] = prefixed_match.group(1)
    
    # Check if there are clues to the prefix
    prefix_clues = []
    if meta.get('Prefixed', 'False').lower() == 'true':
        # Look for things like "starts with 'xyz'" or "prefix of 'xyz'"
        clues = re.findall(r'(?:starts with|prefix(?:ed)? with|begin with)[\s:]*[\'"]?([a-zA-Z0-9_-]+)[\'"]?', text, re.IGNORECASE)
        if clues:
            prefix_clues.extend(clues)
            
        # Also look for code blocks that might be examples
        codes = re.findall(r'<code[^>]*>(.*?)</code>', content, re.DOTALL | re.IGNORECASE)
        # Filter out the title itself
        codes = [c for c in codes if ' ' not in c and len(c) > 3]
        if codes:
            prefix_clues.append("Codes: " + ", ".join(codes[:3]))
            
    meta['Prefix Clues'] = prefix_clues
    return meta

print("Extracting metadata from a sample of files...\n")
for f in html_files[:10]:
    basename = os.path.basename(f)
    print(f"--- {basename} ---")
    print(extract_metadata(f))
    print()

