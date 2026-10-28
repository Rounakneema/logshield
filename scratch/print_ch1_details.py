import json

with open('scratch/ch1_full.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

for i, el in enumerate(elems):
    if el['type'] == 'p':
        print(f'{i:2d} [{el.get("style")}]: {el["text"][:70]}')
    elif el['type'] == 'tbl':
        print(f'{i:2d} [TBL]: {len(el["data"])} rows x {len(el["data"][0])} cols')
