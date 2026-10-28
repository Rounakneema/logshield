import json

with open('scratch/backup_elements.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

# Find all headings (paragraphs with style like 'heading' or starting with numbers / bold)
for i, el in enumerate(elems):
    if el['type'] == 'p':
        style = el.get('style', '')
        txt = el['text']
        if 'Heading' in style or txt.startswith('CHAPTER') or (len(txt) < 80 and txt.isupper()) or (len(txt) < 60 and txt[0].isdigit() and (txt[1] == '.' or txt[2] == '.')):
            print(f'{i:3d} [{style}]: {txt}')
