#!/usr/bin/env python3
# arch-deck.html의 각 슬라이드를 1920x1080 SVG(foreignObject)로 추출한다.
import re, sys

src = open('arch-deck.html', encoding='utf-8').read()

style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
sections = re.findall(r'<section class="slide">.*?</section>', src, re.S)
assert len(sections) == 10, f'expected 10 slides, got {len(sections)}'

FONTS = (
    '@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css");\n'
    '@import url("https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.0.18/index.min.css");\n'
)
OVERRIDE = (
    '\nhtml,body{background:transparent;margin:0;padding:0;}\n'
    '#deck{padding:0;}\n'
    '.slide{margin:0 !important;box-shadow:none !important;border-radius:0 !important;}\n'
)

# style: nbsp 방어 + @import 선두 + override 후미. (svg ns는 손대지 않음)
style_x = FONTS + style.replace('&nbsp;', '&#160;') + OVERRIDE

def fix_frag(frag):
    frag = frag.replace('<br>', '<br/>')
    frag = frag.replace('&nbsp;', '&#160;')
    # foreignObject 내부 인라인 <svg>는 XML에서 XHTML ns를 상속하므로 svg ns 명시
    frag = frag.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ')
    return frag

TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
<foreignObject x="0" y="0" width="1920" height="1080">
<div xmlns="http://www.w3.org/1999/xhtml">
<style><![CDATA[
{style}
]]></style>
{slide}
</div>
</foreignObject>
</svg>
'''

for i, sec in enumerate(sections, 1):
    out = TEMPLATE.format(style=style_x, slide=fix_frag(sec))
    fn = f'arch-deck-{i:02d}.svg'
    open(fn, 'w', encoding='utf-8').write(out)
    print('wrote', fn)
print('done: 10 SVGs')
