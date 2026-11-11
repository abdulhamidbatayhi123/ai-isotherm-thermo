"""Paper 3A's one figure style, built to Nature Portfolio's artwork rules (as read live on
2026-11-05 for Paper 2, ai-kinetics-discoverability/p2_figstyle.py, from which this module is
adapted; re-check the target journal's live rules before submission):

- widths for J. Chem. Inf. Model. (ACS, chosen 2026-11-11): 3.33 in single column, 7.0 in double column,
  height at most 170 mm, drawn at 100 %;
- Arial, 5-7 pt (body 7, ticks and legends 6), panel letters 8 pt bold lowercase; the 5 pt floor
  and the size limits are ASSERTED when a figure is saved;
- no gridlines, shadows or coloured text; Okabe-Ito colours with a fixed meaning per model cell
  (CELL), each cell also with its own line style and marker; temperature on one sequential
  colour-blind-safe scale (viridis);
- vector PDF with embedded TrueType fonts (fonttype 42), plus a 600 dpi PNG for review;
- a provenance file per figure: SHA-256 of the drawing script, this module and every input.
"""
import hashlib
import json
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

MM = 1 / 25.4
# ACS (J. Chem. Inf. Model. author guidelines, Appendix 2, read 2026-11-11): single column up to 240 pt (3.33 in),
# double column 300-504 pt (4.167-7 in); lettering >= 4.5 pt (this style keeps 5 pt), lines >= 0.5 pt
W1, W2 = 3.33, 7.0                    # inches
H_MAX = 170 * MM
BODY_PT, SMALL_PT, LETTER_PT, MIN_PT, MAX_PT = 7.0, 6.0, 8.0, 6.0, 8.0   # MIN_PT raised from 5 (review R4)
SUB_MIN_PT = 5.0   # sub- and superscripts (mathtext prints them at about 70 %); JCIM minimum lettering 4.5 pt
PNG_DPI = 600
SCRIPT_SHRINK = 0.85                  # size of sub- and superscripts relative to their text (see apply)

OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
      "yellow": "#F0E442", "blue": "#0072B2", "vermilion": "#D55E00", "purple": "#CC79A7",
      "grey": "#8C8C8C", "light": "#DDDDDD", "dark": "#333333"}

ROLE = {"neutral": OI["dark"], "muted": "#6B6B6B"}
C = {"dark": OI["dark"], "grey": ROLE["muted"]}
# fixed meaning of every model cell in every figure: colour + line style + marker
CELL = {
    "P":      dict(color=OI["blue"], ls="-", marker="o", label="P (potential, van't Hoff)"),
    "V-pen":  dict(color=OI["sky"], ls="--", marker="s", label="V-pen (penalties)"),
    "V-none": dict(color=OI["grey"], ls=":", marker="^", label="V-none (unconstrained)"),
    "F-hard": dict(color=OI["vermilion"], ls="-.", marker="D", label="F-hard (free in T)"),
    "F-none": dict(color=OI["orange"], ls="--", marker="v", label="F-none (MLP)"),
    "F-rel":  dict(color=OI["yellow"], ls=":", marker="<", label="F-rel (MLP, p/p_sat)"),
    "F-pen":  dict(color=OI["orange"], ls="-.", marker=">", label="F-pen (MLP, penalties)"),
    "A-pen":  dict(color=OI["green"], ls="--", marker="h", label="A-pen (characteristic curve, penalty)"),
    "A-hard": dict(color=OI["green"], ls="-", marker="P", label="A-hard (characteristic curve)"),
    "C1":     dict(color=OI["purple"], ls="-.", marker="X", label="C1 (dual-site Sips)"),
}
# temperatures: one sequential, colour-blind-safe scale (viridis), cold = dark
TEMP_CMAP = "viridis"


def temp_colour(T, T_lo=278.0, T_hi=333.0):
    import matplotlib as mpl
    x = min(1.0, max(0.0, (float(T) - T_lo) / (T_hi - T_lo)))
    return mpl.colormaps[TEMP_CMAP](0.05 + 0.85 * x)


def apply():
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold", "mathtext.default": "regular",
        "font.size": BODY_PT, "axes.labelsize": BODY_PT, "axes.titlesize": BODY_PT,
        "xtick.labelsize": SMALL_PT, "ytick.labelsize": SMALL_PT, "legend.fontsize": SMALL_PT,
        "legend.title_fontsize": SMALL_PT, "legend.frameon": False, "legend.handlelength": 1.6,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "lines.linewidth": 1.0,
        "lines.markersize": 3.5, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "axes.edgecolor": OI["dark"], "axes.labelcolor": "#000000",
        "xtick.color": OI["dark"], "ytick.color": OI["dark"], "text.color": "#000000",
        "axes.titlelocation": "left", "axes.titleweight": "normal",
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.dpi": PNG_DPI, "figure.dpi": 150})
    os.environ.setdefault("SOURCE_DATE_EPOCH", "0")
    # Sub- and superscripts: matplotlib draws them at 0.7 of the base size, so a 6 pt label would
    # carry a 4.2 pt subscript, below the 5 pt floor. Scripts are drawn at 0.85 instead (a 6 pt
    # label then has a 5.1 pt subscript). The constant is private, so its presence is asserted,
    # and save() measures every text span in the written PDF, so a change in matplotlib cannot
    # let a too-small script through unnoticed.
    import matplotlib._mathtext as _mt
    assert hasattr(_mt, "SHRINK_FACTOR"), "matplotlib changed: SHRINK_FACTOR not found"
    _mt.SHRINK_FACTOR = SCRIPT_SHRINK


def pdf_min_span_pt(pdf):
    """Smallest font size of any non-blank text span in a written PDF (PyMuPDF)."""
    import fitz
    sizes = [s["size"] for page in fitz.open(pdf) for b in page.get_text("dict")["blocks"]
             for ln in b.get("lines", []) for s in ln["spans"] if s["text"].strip()]
    return min(sizes) if sizes else None


def letter(ax, s, x=-0.16, y=1.02):
    """Panel letter, Nature style: lowercase, bold, 8 pt, top left outside the axes."""
    ax.text(x, y, s, transform=ax.transAxes, fontsize=LETTER_PT, fontweight="bold",
            ha="left", va="bottom", color="#000000")


def font_range(fig):
    from matplotlib.text import Text
    sizes = [t.get_fontsize() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    return (min(sizes), max(sizes)) if sizes else (None, None)


def coloured_text(fig):
    """Visible texts whose colour is not black or the dark grey of axes (Nature: no coloured text)."""
    from matplotlib.colors import to_hex
    from matplotlib.text import Text
    ok = {"#000000", OI["dark"].lower(), ROLE["muted"].lower(), "#ffffff"}
    return [t.get_text()[:30] for t in fig.findobj(Text)
            if t.get_visible() and t.get_text().strip() and to_hex(t.get_color()).lower() not in ok]


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_EXT = (".py", ".json", ".jsonl", ".csv", ".md", ".txt", ".tex")


def _sha(path):
    """SHA-256 of a file; text files with line endings normalised to LF, so a Windows checkout
    (CRLF) and the repository blob give the same hash (lessons file, section 10)."""
    with open(path, "rb") as f:
        b = f.read()
    if path.lower().endswith(TEXT_EXT):
        b = b.replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest()


def _rel(path):
    """Repository-relative path with forward slashes (the provenance must not name the machine)."""
    p = os.path.abspath(path)
    try:
        return os.path.relpath(p, ROOT).replace(os.sep, "/")
    except ValueError:
        return p.replace(os.sep, "/")


def _git_dirty(paths):
    """Files among `paths` with uncommitted changes or untracked (None if git is unavailable)."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--"] + [_rel(p) for p in paths],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode:
        return None
    return sorted(ln[3:].strip() for ln in r.stdout.splitlines() if ln.strip())


def save(fig, stem, inputs=(), allow_coloured_text=()):
    """Check the figure against the rules, then write stem.pdf, stem.png and stem.prov.json.
    Raises AssertionError instead of writing a figure that breaks a rule."""
    w, h = fig.get_size_inches()
    assert w <= W2 + 1e-6, f"{stem}: width {w / MM:.1f} mm > {W2 / MM:.1f} mm (ACS double column)"
    assert h <= H_MAX + 1e-6, f"{stem}: height {h / MM:.1f} mm > 170 mm"
    lo, hi = font_range(fig)
    assert lo is None or lo >= MIN_PT - 1e-9, f"{stem}: text at {lo} pt < {MIN_PT} pt"
    assert hi is None or hi <= MAX_PT + 1e-9, f"{stem}: text at {hi} pt > {MAX_PT} pt"
    bad = [t for t in coloured_text(fig) if t not in allow_coloured_text]
    assert not bad, f"{stem}: coloured text {bad}"
    os.makedirs(os.path.dirname(stem) or ".", exist_ok=True)
    meta = {"CreationDate": None, "ModDate": None}
    fig.savefig(stem + ".pdf", metadata=meta)
    lo_pdf = pdf_min_span_pt(stem + ".pdf")
    if lo_pdf is not None and lo_pdf < SUB_MIN_PT - 0.05:
        os.remove(stem + ".pdf")
        raise AssertionError(f"{stem}: a text span (sub- or superscript?) prints at {lo_pdf:.2f} pt < {SUB_MIN_PT} pt")
    fig.savefig(stem + ".png", dpi=PNG_DPI)
    script = os.path.abspath(sys.argv[0]) if sys.argv and sys.argv[0] else None
    have = script and os.path.exists(script)
    missing = [p for p in inputs if not os.path.exists(p)]
    assert not missing, f"{stem}: inputs not found {missing}"
    tracked = [__file__] + ([script] if have else []) + [p for p in inputs if not _rel(p).startswith("data/raw/")]
    prov = {"figure": os.path.basename(stem), "size_mm": [round(w / MM, 1), round(h / MM, 1)],
            "font_pt": [lo, hi], "made": time.strftime("%Y-%m-%d %H:%M:%S"),
            "hash": "sha256, text files LF-normalised",
            "style": _rel(__file__), "style_sha256": _sha(__file__),
            "script": _rel(script) if have else None,
            "script_sha256": _sha(script) if have else None,
            "inputs": {_rel(p): _sha(p) for p in inputs},
            # data/raw is third-party data kept out of git by design, so it is hashed but not git-checked
            "git_dirty_files": _git_dirty(tracked)}
    with open(stem + ".prov.json", "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=1)
    plt.close(fig)
    return [stem + ".pdf", stem + ".png"]
