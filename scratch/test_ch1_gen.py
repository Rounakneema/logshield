import json
import re

def clean_text(t):
    if not t:
        return ""
    # Replace em dashes and en dashes
    t = t.replace('—', ' - ').replace('–', ' - ')
    # Clean quotes and escapes for JS template string or double-quoted string
    t = t.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    return t

with open('scratch/ch1_full.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

print(f'Total elements in ch1: {len(elems)}')
