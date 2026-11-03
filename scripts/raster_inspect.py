"""Inspection helper for raster figures (not part of any result).

Lists the embedded images on a PDF page, saves one at native resolution, and saves a copy
with a labelled pixel grid so tick and legend positions can be read by eye. Also prints
automatically detected frame lines and tick marks for a given crop.

Usage:
  python scripts/raster_inspect.py <pdf> <page_1based>                     list images
  python scripts/raster_inspect.py <pdf> <page> <xref> <outdir> [step]     save native + grid
"""
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw


def main():
    pdf, page_no = sys.argv[1], int(sys.argv[2])
    doc = fitz.open(pdf)
    page = doc[page_no - 1]
    if len(sys.argv) == 3:
        for img in page.get_images(full=True):
            xref = img[0]
            rects = page.get_image_rects(xref)
            print("xref", xref, "size", img[2], "x", img[3], "on page at", [tuple(round(v) for v in r) for r in rects])
        return
    xref, outdir = int(sys.argv[3]), Path(sys.argv[4])
    step = int(sys.argv[5]) if len(sys.argv) > 5 else 50
    outdir.mkdir(parents=True, exist_ok=True)
    pix = fitz.Pixmap(doc, xref)
    if pix.n - pix.alpha != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    stem = f"{Path(pdf).stem}_p{page_no}_x{xref}"
    im.save(outdir / f"{stem}.png")
    g = im.copy()
    d = ImageDraw.Draw(g)
    for x in range(0, g.width, step):
        d.line((x, 0, x, g.height), fill=(255, 0, 255) if x % (step * 2) == 0 else (255, 180, 255), width=1)
        d.text((x + 2, 2), str(x), fill=(200, 0, 200))
    for y in range(0, g.height, step):
        d.line((0, y, g.width, y), fill=(0, 160, 255) if y % (step * 2) == 0 else (170, 220, 255), width=1)
        d.text((2, y + 2), str(y), fill=(0, 100, 200))
    g.save(outdir / f"{stem}_grid.png")
    print("saved", outdir / f"{stem}.png", pix.width, "x", pix.height)


if __name__ == "__main__":
    main()
