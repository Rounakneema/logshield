import json

with open('scratch/backup_elements.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

bounds = [
    ('ch1', 134, 174),
    ('ch2', 174, 218),
    ('ch3', 218, 264),
    ('ch4', 264, 318),
    ('ch5', 318, 351),
    ('ch6', 351, 375),
    ('ch7_app', 375, 558)
]

for name, start, end in bounds:
    ch_elems = elems[start:end]
    with open(f'scratch/{name}_full.json', 'w', encoding='utf-8') as out:
        json.dump(ch_elems, out, ensure_ascii=False, indent=2)
    print(f'Wrote scratch/{name}_full.json: {len(ch_elems)} elements')
