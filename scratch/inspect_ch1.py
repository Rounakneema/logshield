import json

with open('scratch/backup_elements.json', 'r', encoding='utf-8') as f:
    elems = json.load(f)

# Find all occurrences of CHAPTER 1
indices = [i for i, el in enumerate(elems) if el['type'] == 'p' and el['text'] == 'CHAPTER 1: INTRODUCTION']
print('Indices of CHAPTER 1:', indices)

# Real Chapter 1 starts at indices[1]
ch1_start = indices[1]
ch2_start = [i for i, el in enumerate(elems) if el['type'] == 'p' and el['text'] == 'CHAPTER 2: LITERATURE SURVEY'][1]
ch3_start = [i for i, el in enumerate(elems) if el['type'] == 'p' and el['text'] == 'CHAPTER 3: PROBLEM DEFINITION AND PROPOSED SOLUTION'][1]
ch4_start = [i for i, el in enumerate(elems) if el['type'] == 'p' and el['text'] == 'CHAPTER 4: DESIGN'][1]
ch5_start = [i for i, el in enumerate(elems) if el['type'] == 'p' and el['text'] == 'CHAPTER 5: RESULT ANALYSIS'][1]
ch6_start = [i for i, el in enumerate(elems) if el['type'] == 'p' and el['text'] == 'CHAPTER 6: TESTING'][1]
ch7_start = [i for i, el in enumerate(elems) if el['type'] == 'p' and el['text'] == 'CHAPTER 7: CONCLUSION AND FUTURE WORK'][1]

print(f'Chapter boundaries: 1:{ch1_start}, 2:{ch2_start}, 3:{ch3_start}, 4:{ch4_start}, 5:{ch5_start}, 6:{ch6_start}, 7:{ch7_start}, end:{len(elems)}')
