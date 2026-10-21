"""Embed puzzles into template.html.

usage: python3 build.py SIZE PUZZLES.json OUT.html
"""
import json, sys

size = int(sys.argv[1])
puzzles = json.load(open(sys.argv[2]))
html = open('template.html').read()
html = (html.replace('__PUZZLES__', json.dumps(puzzles, separators=(',', ':')))
            .replace('__EXIT_ROW__', str(size // 2 - 1))
            .replace('__SIZE__', str(size)))
open(sys.argv[3], 'w').write(html)
print(len(puzzles), 'puzzles embedded,', size, 'x', size)
