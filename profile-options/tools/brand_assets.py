"""Shared, self-contained SVG components from Ioannis Vlachos's website brand."""
import base64
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BRAND = ROOT / 'assets' / 'profile' / 'brand'
THEMES = {
    'light': dict(paper='#F6F4EE', card='#FBFAF6', ink='#14213A', muted='#56607A', rule='#DCD6C8', accent='#C2412D'),
    'dark': dict(paper='#0D1524', card='#121C2E', ink='#E8E3D6', muted='#9AA3B5', rule='#26324A', accent='#F0785C'),
}
FONTS = {
    'serif': ('Petrona', 'petrona-latin-wght-normal.woff2', '100 900'),
    'sans': ('Source Sans 3', 'source-sans-3-latin-wght-normal.woff2', '200 900'),
    'mono': ('JetBrains Mono', 'jetbrains-mono-latin-wght-normal.woff2', '100 800'),
}

def font_css(kind='serif'):
    """Embed the site's licensed font so SVG images need no external font requests."""
    name, filename, weights = FONTS[kind]
    data = base64.b64encode((BRAND / filename).read_bytes()).decode()
    return f"@font-face{{font-family:'{name}';font-style:normal;font-weight:{weights};src:url(data:font/woff2;base64,{data}) format('woff2');}}"

def logo(x=0, y=0, size=64, theme='light', tile=False):
    """Reuse the exact IV and smile geometry; adapt colour like the website navbar."""
    ns = '{http://www.w3.org/2000/svg}'
    source = ET.parse(BRAND / 'mark.svg').getroot()
    group = source.find(ns + 'g')
    palette = THEMES[theme]
    for element in group.iter():
        element.tag = element.tag.removeprefix(ns)
        kind = element.attrib.pop('class', None)
        if kind == 'iv':
            element.set('fill', palette['ink'])
            element.set('stroke', palette['ink'])
            element.set('stroke-width', '1.5')
            element.set('stroke-linejoin', 'round')
        elif kind == 'smile':
            element.set('stroke', palette['ink'])
            element.set('stroke-opacity', '0.55')
        elif kind == 'dot':
            element.set('fill', palette['accent'])
    background = f'<rect width="64" height="64" rx="14" fill="{palette["paper"]}"/>' if tile else ''
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 64 64" aria-label="Ioannis Vlachos IV monogram">'
            f'{background}{ET.tostring(group, encoding="unicode")}</svg>')
