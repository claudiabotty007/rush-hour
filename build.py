import json
t = open('template.html').read()
p = json.load(open('puzzles-6x6.json'))
open('index.html', 'w').write(t.replace('__PUZZLES__', json.dumps(p, separators=(',', ':'))))
print(len(p), 'puzzles embedded')
