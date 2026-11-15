"""Build the profile header: an implied-volatility surface beside the name.

The surface is stylised, not fitted to market data. The animated files draw
the front smile, extend the surface from it, then drop the accent dot from the
top of the card: it falls under gravity, lands on the smile and slides along
it with friction until it rests at the minimum. Nothing moves after that.

Writes assets/profile/header-{light,dark}.svg (animated) and
header-static-{light,dark}.svg (finished state, for reduced motion).
"""
import math
import sys
from pathlib import Path

from brand_assets import THEMES, font_css

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'assets' / 'profile'
W, H = 800, 250
NAME = 'Ioannis Vlachos'
HANDLE = 'vlachosi@github'
N_K, N_T = 17, 9                       # mesh nodes along strike and maturity
X0, Y0, W_K, S_Z = 448, 189, 204, 134  # front-left origin, strike width, height scale
T_X, T_Y = 118, 60                     # oblique offset of the longest maturity
DOT_R = 5.4
DROP_AT = 2.3                          # seconds before the dot is released
DROP_K = -0.74                         # moneyness above which the dot is released
GRAVITY, FRICTION, GRIP = 1500.0, 3.6, 0.65  # units/s^2, 1/s, share of speed kept on landing
FPS = 60


def smile(k, f):
    """Stylised implied volatility at moneyness k in [-1, 1] and maturity f in [0, 1].

    The short end is steep and skewed towards low strikes; the long end sits
    higher at the money and is flatter and rounder. Heights lie in [0, 1].
    """
    rho = -0.22
    s = 0.38 + 0.38 * f
    amp = 1.0 - 0.72 * f ** 0.8
    x = k - 0.12
    g = rho * x + math.sqrt(x * x + s * s) - s * math.sqrt(1 - rho * rho)
    return 0.10 * f ** 0.9 + amp * g / 1.06


def project(k, f):
    return (X0 + (k + 1) / 2 * W_K + f * T_X, Y0 - smile(k, f) * S_Z - f * T_Y)


def front_y(x):
    """Height of the front smile on screen (y grows downwards) at screen x."""
    return project((x - X0) / W_K * 2 - 1, 0)[1]


def drop():
    """Positions of the dot at FPS frames per second, ending at the smile's minimum.

    Free fall from just above the card, then a bead sliding on the front smile
    under gravity with linear friction, integrated in small steps.
    """
    rest_x = max((X0 + W_K * j / 4000 for j in range(4001)), key=front_y)
    dt, h = 1 / (FPS * 20), 0.05
    x, y, vy = X0 + (DROP_K + 1) / 2 * W_K, -DOT_R - 2, 0.0
    frames, step = [], 0
    while y < front_y(x):                       # free fall
        if step % 20 == 0:
            frames.append((x, y))
        vy += GRAVITY * dt
        y += vy * dt
        step += 1
    slope = (front_y(x + h) - front_y(x - h)) / (2 * h)
    vx = GRIP * vy * slope / (1 + slope * slope)  # keep the part of the speed along the curve
    while True:                                 # slide along the smile
        if step % 20 == 0:
            frames.append((x, front_y(x)))
            if abs(x - rest_x) < 0.2 and abs(vx) < 2:
                break
        slope = (front_y(x + h) - front_y(x - h)) / (2 * h)
        curve = (front_y(x + h) - 2 * front_y(x) + front_y(x - h)) / (h * h)
        vx += ((GRAVITY * slope - slope * curve * vx * vx) / (1 + slope * slope) - FRICTION * vx) * dt
        x += vx * dt
        step += 1
    frames.append((rest_x, front_y(rest_x)))
    return frames


def n(v):
    text = f'{v:.1f}'
    return text[:-2] if text.endswith('.0') else text


def line(points):
    return 'M' + 'L'.join(f'{n(x)} {n(y)}' for x, y in points)


def row_cells(i):
    """One maturity row of the mesh as closed cells, in relative coordinates."""
    rows = N_T - 1
    f0, f1 = i / rows, (i + 1) / rows
    parts = []
    for j in range(N_K - 1):
        k0, k1 = -1 + 2 * j / (N_K - 1), -1 + 2 * (j + 1) / (N_K - 1)
        a, b, c, d = project(k0, f0), project(k1, f0), project(k1, f1), project(k0, f1)
        parts.append(f'M{n(a[0])} {n(a[1])}l{n(b[0] - a[0])} {n(b[1] - a[1])} {n(c[0] - b[0])} {n(c[1] - b[1])} {n(d[0] - c[0])} {n(d[1] - c[1])}z')
    return ''.join(parts)


def build(theme, animated):
    p = THEMES[theme]
    rows = N_T - 1
    path = drop()
    rest = path[-1]
    css = [font_css('serif', NAME), font_css('mono', HANDLE)]
    dot_motion, dot_start = '', ''
    if animated:
        css.append('.smile{stroke-dasharray:1;animation:draw 1.1s cubic-bezier(.45,0,.2,1) .25s both}'
                   '.row{animation:show .45s ease-out both}'
                   + ''.join(f'.r{i}{{animation-delay:{1.4 + 0.13 * i:.2f}s}}' for i in range(rows))
                   + '@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}'
                   '@keyframes show{from{opacity:0}to{opacity:1}}')
        timing = f'dur="{(len(path) - 1) / FPS:.2f}s" begin="{DROP_AT}s" fill="freeze"'
        dot_start = ' opacity="0"'
        dot_motion = (f'<set attributeName="opacity" to="1" begin="{DROP_AT}s" fill="freeze"/>'
                      f'<animate attributeName="cx" {timing} values="{";".join(n(x) for x, _ in path)}"/>'
                      f'<animate attributeName="cy" {timing} values="{";".join(n(y) for _, y in path)}"/>')
    motion = ('The front smile draws once and the surface extends from it; a dot then falls from the top, lands on the smile and settles at its minimum.'
              if animated else 'This static version is selected when reduced motion is preferred.')
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{NAME}</title>',
        f'<desc id="desc">The name Ioannis Vlachos and the handle vlachosi@github beside a wireframe implied volatility surface over strike and maturity. {motion}</desc>',
        f'<style>{"".join(css)}</style>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{p["paper"]}" stroke="{p["rule"]}" stroke-width="2"/>',
    ]
    # Mesh rows are painted back to front so nearer cells hide farther ones.
    for i in reversed(range(rows)):
        out.append(f'<path class="row r{i}" fill="{p["card"]}" stroke="{p["ink"]}" stroke-opacity="{0.72 - 0.44 * i / rows:.2f}" '
                   f'stroke-linejoin="round" d="{row_cells(i)}"/>')
    front = [project(-1 + 2 * j / 40, 0) for j in range(41)]
    out += [
        f'<path class="smile" pathLength="1" d="{line(front)}" fill="none" stroke="{p["ink"]}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<circle cx="{n(rest[0])}" cy="{n(rest[1])}" r="{DOT_R}" fill="{p["accent"]}"{dot_start}>{dot_motion}</circle>',
        f'<text x="44" y="124" font-family="Petrona,Georgia,serif" font-size="52" font-weight="700" letter-spacing="-0.7" fill="{p["ink"]}">{NAME}</text>',
        f'<text x="46" y="164" font-family="\'JetBrains Mono\',ui-monospace,monospace" font-size="17" letter-spacing="0.6" fill="{p["muted"]}">vlachosi<tspan fill="{p["accent"]}">@</tspan>github</text>',
        '</svg>',
    ]
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT / f'header-{theme}.svg').write_text(build(theme, True))
        (OUT / f'header-static-{theme}.svg').write_text(build(theme, False))
    print('Built four profile headers.')
