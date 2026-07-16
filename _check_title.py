import json
d = json.load(open('tem_ex_qhc.json', encoding='utf-8'))
t = d['excel_templates'][0]['sheets'][0]['title_block']
print('lines count:', len(t['lines']))
print('lines:')
for i, l in enumerate(t['lines']):
    print(f'  {i}: {l}')
