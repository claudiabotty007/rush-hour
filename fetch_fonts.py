"""Download the Barlow fonts used by the page and write fonts/fonts.css.

usage: python fetch_fonts.py

Fetches the Latin subset of Barlow (400, 500, 600) and Barlow Condensed
(600, 700) from Google Fonts and embeds each woff2 file in the stylesheet as a
data URI, so the page and the Android app work without a network connection.
Both families are licensed under the SIL Open Font License 1.1.
"""
import base64, os, re, sys, urllib.request

CSS_URL = ('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700'
           '&family=Barlow:wght@400;500;600&display=swap')
# A current Chrome user agent makes Google Fonts answer with woff2 files.
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    css = get(CSS_URL).decode('utf-8')
    blocks = re.findall(r'/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})', css, re.S)
    latin = [b for name, b in blocks if name == 'latin']
    if len(latin) != 5:
        sys.exit('expected 5 latin font faces, found %d' % len(latin))

    out = []
    total = 0
    for block in latin:
        m = re.search(r'url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', block)
        if not m:
            sys.exit('no woff2 url in block:\n' + block)
        data = get(m.group(1))
        total += len(data)
        uri = 'data:font/woff2;base64,' + base64.b64encode(data).decode('ascii')
        out.append(block.replace(m.group(0), 'url(' + uri + ')'))

    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, 'fonts'), exist_ok=True)
    path = os.path.join(here, 'fonts', 'fonts.css')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('/* Barlow and Barlow Condensed, Latin subset. SIL Open Font License 1.1. */\n')
        f.write('\n'.join(out) + '\n')
    print('wrote %s: %d faces, %d KB of font data' % (path, len(out), total // 1024))


main()
