import json

with open('scratch/ch7_app_full.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

for i, el in enumerate(elems):
    if el['type'] == 'p':
        txt = el['text']
        if txt.startswith('CHAPTER') or txt.startswith('REFERENCES') or txt.startswith('APPENDIX') or (len(txt) < 60 and txt.isupper()):
            print(f'{i:3d}: {txt}')
    elif el['type'] == 'tbl':
        prev = elems[i-1]['text'] if i > 0 and elems[i-1]['type'] == 'p' else ''
        print(f'{i:3d} [TBL]: {len(el["data"])} rows x {len(el["data"][0])} cols | Prev: "{prev[:60]}"')
