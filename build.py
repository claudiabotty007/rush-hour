"""Embed puzzles into template.html and write a complete standalone page.

usage: python build.py SIZE PUZZLES.json OUT.html

The output is a full HTML document (doctype, viewport, reset) with the Barlow
fonts embedded from fonts/fonts.css, so it needs no network. Run
fetch_fonts.py once to create fonts/fonts.css; without it the page falls back
to the Google Fonts link in the template.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_MARKER = '<div class="page">'

SKELETON_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
:root { color-scheme: light; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; }
* { -webkit-tap-highlight-color: transparent; }
[hidden] { display: none !important; }
</style>
"""


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def main():
    size = int(sys.argv[1])
    puzzles = json.load(open(sys.argv[2], encoding='utf-8'))
    out_path = sys.argv[3]

    html = read(os.path.join(HERE, 'template.html'))
    html = (html.replace('__PUZZLES__', json.dumps(puzzles, separators=(',', ':')))
                .replace('__EXIT_ROW__', str(size // 2 - 1))
                .replace('__SIZE__', str(size)))
    html = html.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')

    fonts_css = os.path.join(HERE, 'fonts', 'fonts.css')
    embedded = os.path.exists(fonts_css)
    if embedded:
        css = read(fonts_css)
        html, n = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>',
                          lambda m: '<style>\n' + css + '</style>', html)
        if n != 1:
            sys.exit('expected exactly one Google Fonts link in template.html, found %d' % n)

    i = html.index(PAGE_MARKER)
    page = SKELETON_HEAD + html[:i] + '</head>\n<body>\n' + html[i:].rstrip() + '\n</body>\n</html>\n'

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)
    print('%d puzzles embedded, %dx%d, fonts %s, %d KB' % (
        len(puzzles), size, size, 'embedded' if embedded else 'linked', len(page.encode('utf-8')) // 1024))


main()
