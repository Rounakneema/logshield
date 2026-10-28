import json

with open('scratch/backup_elements.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

table_idx = 1
for i, el in enumerate(elems):
    if el['type'] == 'tbl':
        prev_p = ''
        for k in range(i-1, -1, -1):
            if elems[k]['type'] == 'p':
                prev_p = elems[k]['text']
                break
        headers = el['data'][0] if el['data'] else []
        num_rows = len(el['data'])
        print(f'Table {table_idx:2d} (Rows: {num_rows:2d}): Preceded by: "{prev_p[:80]}"')
        print(f'         Headers: {headers}')
        table_idx += 1
