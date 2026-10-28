import json

for name in ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7_app']:
    with open(f'scratch/{name}_full.json', 'r', encoding='utf-8') as f:
        elems = json.load(f)
    print(f'=== {name.upper()} TABLES ===')
    for i, el in enumerate(elems):
        if el['type'] == 'tbl':
            prev_p = ''
            for k in range(i-1, -1, -1):
                if elems[k]['type'] == 'p':
                    prev_p = elems[k]['text']
                    break
            print(f'  Table at {i}: "{prev_p}"')
            print(f'    Header: {el["data"][0]}')
            print(f'    Rows: {len(el["data"])}')
