import json

with open('scratch/backup_elements.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

found = False
for i, el in enumerate(elems):
    if el['type'] == 'p' and 'SNAPSHOTS OF THE SYSTEM' in el['text']:
        found = True
        print(f'Found at {i}:')
        for j in range(i, min(len(elems), i + 25)):
            if elems[j]['type'] == 'p':
                print(f'  P{j}: {elems[j]["text"][:80]}')
            else:
                print(f'  TBL{j}: {len(elems[j]["data"])} rows')
        break
