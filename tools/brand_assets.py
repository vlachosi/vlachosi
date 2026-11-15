"""Shared, self-contained SVG components from Ioannis Vlachos's website brand."""
import base64
from io import BytesIO
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
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

def subset_font(data, text):
    """Reduce a WOFF2 font to the glyphs `text` needs, keeping its weight axis."""
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError as error:
        raise SystemExit('Font subsetting needs fontTools and brotli: pip install -r tools/requirements.txt') from error
    # A fixed timestamp keeps rebuilt assets byte-identical.
    font = TTFont(BytesIO(data), recalcTimestamp=False)
    subsetter = subset.Subsetter(subset.Options(flavor='woff2'))
    subsetter.populate(text=text)
    subsetter.subset(font)
    output = BytesIO()
    font.flavor = 'woff2'
    font.save(output)
    return output.getvalue()

def font_css(kind='serif', text=None):
    """Embed the site's licensed font so SVG images need no external font requests.

    Pass `text` to embed only the glyphs an image uses instead of the whole font.
    """
    name, filename, weights = FONTS[kind]
    font = (BRAND / filename).read_bytes()
    if text is not None:
        font = subset_font(font, text)
    data = base64.b64encode(font).decode()
    return f"@font-face{{font-family:'{name}';font-style:normal;font-weight:{weights};src:url(data:font/woff2;base64,{data}) format('woff2');}}"

def logo(x=0, y=0, size=64, theme='light'):
    """The site's circular IV monogram, coloured to stand out on a `theme` background.

    The disc takes the opposite theme's palette, so the navy button shows the
    ivory favicon as the site serves it and the ivory button shows it inverted.
    """
    ns = '{http://www.w3.org/2000/svg}'
    source = ET.parse(BRAND / 'mark.svg').getroot()
    group = source.find(ns + 'g')
    palette = THEMES['dark' if theme == 'light' else 'light']
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
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 64 64" aria-label="Ioannis Vlachos IV monogram">'
            f'<circle cx="32" cy="32" r="32" fill="{palette["paper"]}"/>{ET.tostring(group, encoding="unicode")}</svg>')
