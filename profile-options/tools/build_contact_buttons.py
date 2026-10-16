"""Build the terminal profile's self-contained contact buttons.

Icon sources and the Bootstrap Icons licence are recorded in
assets/profile/brand/CONTACT-SOURCES.md. No network is needed to regenerate.
"""
from html import escape
from pathlib import Path

from brand_assets import THEMES, font_css, logo

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets' / 'profile'
LINKEDIN_PATH = 'M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854zm4.943 12.248V6.169H2.542v7.225zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248S2.4 3.226 2.4 3.934c0 .694.521 1.248 1.327 1.248zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016l.016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225z'
ORCID_CONTENT = '<circle cx="128" cy="128" r="128" fill="#A6CE39"/><g fill="#fff"><rect x="70" y="102" width="18" height="84" rx="1"/><circle cx="79" cy="79" r="11.5"/><path d="M108 102h44c26 0 46 18.5 46 42s-20 42-46 42h-44zM126 118v52h25c17 0 29-11 29-26s-12-26-29-26z"/></g>'
SSRN_CONTENT = '<rect width="64" height="64" rx="6" fill="#2A63AB"/><rect x="4" y="4" width="56" height="56" rx="3" fill="none" stroke="#fff" stroke-opacity="0.55" stroke-width="1.5"/><text x="32" y="40" text-anchor="middle" font-family="Petrona, Georgia, serif" font-size="20" font-weight="700" fill="#fff" letter-spacing="-0.5">SSRN</text>'


def icon(slug, theme):
    if slug == 'website':
        return logo(8, 3, 30, theme)
    viewbox, content = {
        'linkedin': ('0 0 16 16', f'<path fill="{THEMES[theme]["ink"]}" d="{LINKEDIN_PATH}"/>'),
        'orcid': ('0 0 256 256', ORCID_CONTENT),
        'ssrn': ('0 0 64 64', SSRN_CONTENT),
    }[slug]
    return f'<svg x="10" y="7" width="22" height="22" viewBox="{viewbox}" aria-hidden="true">{content}</svg>'


def build():
    for slug, label, width in [
        ('website', 'Website', 120),
        ('linkedin', 'LinkedIn', 120),
        ('orcid', 'ORCID', 104),
        ('ssrn', 'SSRN', 98),
    ]:
        styles = font_css('sans') + (font_css('serif') if slug == 'ssrn' else '')
        for theme, palette in THEMES.items():
            # Transparent gutters keep wrapped buttons spaced on GitHub without custom CSS.
            canvas_width = width + 16
            source = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="44" '
                f'viewBox="0 0 {canvas_width} 44" role="img" aria-labelledby="title desc">\n'
                f'<title id="title">{escape(label)}</title>\n'
                f'<desc id="desc">{escape(label)} contact button for Ioannis Vlachos, with its identifying icon; {theme} page theme.</desc>\n'
                '<!-- Icon attribution and licence: brand/CONTACT-SOURCES.md -->\n'
                f'<style>{styles}</style>\n'
                '<g transform="translate(8 4)">\n'
                f'<rect x=".5" y=".5" width="{width-1}" height="35" rx="8" fill="{palette["paper"]}" stroke="{palette["muted"]}"/>\n'
                f'{icon(slug, theme)}\n'
                f'<text x="43" y="23" fill="{palette["ink"]}" font-family="\'Source Sans 3\',Arial,sans-serif" '
                f'font-size="15" font-weight="600">{escape(label)}</text>\n'
                '</g>\n'
                '</svg>\n'
            )
            (OUT / f'contact-{slug}-{theme}.svg').write_text(source)
    # The explicitly themed assets replace the original, unthemed button files.
    for slug in ('website', 'linkedin', 'orcid', 'ssrn'):
        (OUT / f'contact-{slug}.svg').unlink(missing_ok=True)
    print('Built eight light/dark contact buttons with horizontal and vertical spacing.')


if __name__ == '__main__':
    build()
