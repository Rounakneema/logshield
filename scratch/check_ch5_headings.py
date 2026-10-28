import json

with open('scratch/ch5_full.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

for i, el in enumerate(elems):
    if el['type'] == 'p' and el.get('style') in ('Heading 2', 'Heading 3'):
        print(f'{i:2d} [{el.get("style")}]: {el["text"]}')
