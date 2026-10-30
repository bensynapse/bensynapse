#!/usr/bin/env python3
"""Render the profile artwork using a local Geist font and fonttools[woff]."""

import argparse
import math
from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


def lettering(font, value, x, y, size, fill, weight=500):
    face = font[weight]
    glyphs = face.getGlyphSet()
    mapping = face.getBestCmap()
    scale = size / face["head"].unitsPerEm
    parts = []
    cursor = 0
    for character in value:
        name = mapping[ord(character)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        if pen.getCommands():
            parts.append(f'<path transform="translate({cursor:.2f} 0)" d="{pen.getCommands()}"/>')
        cursor += face["hmtx"][name][0]
    return (
        f'<g aria-label="{escape(value, quote=True)}" fill="{fill}" '
        f'transform="translate({x} {y}) scale({scale:.6f} {-scale:.6f})">'
        + "".join(parts) + "</g>"
    )


def ball(cx, cy, radius, accent, base):
    return f'''<g transform="translate({cx} {cy})">
  <circle r="{radius}" fill="{accent}"/>
  <path d="M {-radius*.68} {-radius*.73} C {radius*.1} {-radius*.36} {radius*.1} {radius*.36} {-radius*.68} {radius*.73}
           M {radius*.68} {-radius*.73} C {-radius*.1} {-radius*.36} {-radius*.1} {radius*.36} {radius*.68} {radius*.73}"
        fill="none" stroke="{base}" stroke-width="{radius*.11}"/>
</g>'''


def sculpture(cx, cy, radius, palette):
    p = palette
    paths = []
    # The path family joins the tennis seam to a stream of data connections.
    for index in range(23):
        offset = (index - 11) / 11
        start_x = cx - radius * 1.4
        start_y = cy + offset * radius * .58
        end_x = cx + radius * .88 * math.cos(offset * math.pi / 2)
        end_y = cy + radius * .96 * math.sin(offset * math.pi / 2)
        stroke = p["tennis"] if index % 4 == 0 else p["wire"]
        paths.append(
            f'<path d="M {start_x:.2f} {start_y:.2f} '
            f'C {cx-radius*.15:.2f} {cy+offset*radius*1.7:.2f}, '
            f'{cx-radius*.45:.2f} {cy-offset*radius*1.8:.2f}, {end_x:.2f} {end_y:.2f}" '
            f'fill="none" stroke="{stroke}" stroke-width="1.3" opacity="{.65 if index % 4 == 0 else .48}"/>'
        )
    for index, angle in enumerate([-.94, -.3, .55, 1.32, 2.48, 3.37, 4.35]):
        x, y = cx + radius*math.cos(angle), cy+radius*math.sin(angle)
        paths.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{3 if index%2 else 4.5}" fill="{p["tennis"]}"/>')
    paths.append(
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{p["wire"]}" stroke-width="1.3"/>'
    )
    for rotation in [-36, -18, 0, 18, 36]:
        paths.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{radius*.37}" ry="{radius}" '
                     f'transform="rotate({rotation} {cx} {cy})" fill="none" '
                     f'stroke="{p["wire"]}" stroke-width="1" opacity=".6"/>')
    paths.append(ball(cx, cy, radius*.27, p["tennis"], p["base"]))
    return "".join(paths)


def artwork(font, mobile):
    p = {name: f"var(--{name})" for name in ("base", "text", "muted", "synapse", "tennis", "wire", "edge")}
    width, height = (720, 710) if mobile else (1200, 410)
    body = [f'<rect width="{width}" height="{height}" rx="14" fill="{p["base"]}"/>']
    if mobile:
        body.append(sculpture(497, 412, 176, p))
        body.append(lettering(font, "Ben Abulafia", 42, 113, 73, p["text"], 650))
        body.append(lettering(font, "Software, AI &", 45, 175, 40, p["muted"]))
        body.append(lettering(font, "live tennis data.", 45, 225, 40, p["muted"]))
        body.append(lettering(font, "Synapse", 45, 548, 44, p["synapse"], 600))
        body.append(lettering(font, "Live Tennis API", 45, 608, 44, p["text"], 600))
        body.append(lettering(font, "Fax for Agents", 45, 668, 44, p["text"], 600))
        body.append(f'<path d="M 45 257 L 171 257" stroke="{p["synapse"]}" stroke-width="3"/>')
    else:
        body.append(sculpture(961, 206, 164, p))
        body.append(lettering(font, "Ben Abulafia", 52, 137, 85, p["text"], 650))
        body.append(lettering(font, "Software, AI & live tennis data.", 56, 195, 30, p["muted"]))
        body.append(f'<path d="M 56 239 L 182 239" stroke="{p["synapse"]}" stroke-width="3"/>')
        body.append(lettering(font, "Synapse", 56, 314, 30, p["synapse"], 600))
        body.append(lettering(font, "Live Tennis API", 231, 314, 30, p["text"], 600))
        body.append(lettering(font, "Fax for Agents", 501, 314, 30, p["text"], 600))
        for divider in (203, 473):
            body.append(f'<path d="M {divider} 289 L {divider} 318" stroke="{p["edge"]}" stroke-width="2"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
<title id="title">Ben Abulafia. Synapse, Live Tennis API and Fax for Agents.</title>
<desc id="description">Software, AI and live tennis data. A tennis ball at the center of connected data paths.</desc>
<style>
svg {{ --base:#f5f8f6; --text:#15261d; --muted:#50645a; --synapse:#087a57; --tennis:#138139; --wire:#459467; --edge:#dce6de; }}
@media (prefers-color-scheme:dark) {{
  svg {{ --base:#090a0c; --text:#ffffff; --muted:#acb9b2; --synapse:#10b981; --tennis:#00ff41; --wire:#36bb79; --edge:#26372d; }}
}}
</style>
{"".join(body)}
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, required=True, help="Local Geist variable font, WOFF2 or TTF")
    args = parser.parse_args()
    source = TTFont(args.font)
    font = {weight: instantiateVariableFont(source, {"wght": weight}, inplace=False) for weight in (500, 600, 650)}
    output = Path(__file__).resolve().parent.parent / "assets"
    for mobile in (False, True):
        name = "profile" + ("-mobile" if mobile else "") + ".svg"
        path = output / name
        path.write_text(artwork(font, mobile))
        print(path.relative_to(output.parent))


if __name__ == "__main__":
    main()
