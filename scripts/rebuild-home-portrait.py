"""
Rebuild images/portrait.png from portrait-checker-source.png.

Only removes fake “checkerboard transparency” pixels from the export. Every other pixel is
kept exactly as in the source photo (same RGB, fully opaque). No inpainting, no nearest-
neighbor fill, no median blends — checked tiles → transparent only.

Does not change portfolio.html or CSS. Optional: run fix-eyes-brows.py if you want sclera
touch-ups (see bottom of rebuild()).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "portrait.png"
BACKUP = ROOT / "images" / "portrait-checker-source.png"

CHECKER_TILES = tuple((c, c, c) for c in range(192, 256, 4)) + ((255, 255, 255),)


def neutral_mask(r: np.ndarray, g: np.ndarray, b: np.ndarray, max_ch: int = 22) -> np.ndarray:
    return (np.abs(r.astype(np.int32) - g.astype(np.int32)) <= max_ch) & (
        np.abs(g.astype(np.int32) - b.astype(np.int32)) <= max_ch
    )


def flood_checker_from_edges(chk: np.ndarray) -> np.ndarray:
    """
    Checker pixels that are 4-connected to the *outer border* (top row + left/right sides).
    This lets us clear the checker background from the edges only, without touching
    any checker-like pixels that are fully inside the photo area (chest, eyes, etc.).
    """
    h, w = chk.shape
    bg = np.zeros((h, w), dtype=bool)

    # Seed from top edge and left/right sides (not the bottom edge).
    ys = [0]
    xs = list(range(w))
    # Top row
    for x in xs:
        if chk[0, x] and not bg[0, x]:
            bg[0, x] = True
    # Left/right columns
    for y in range(h):
        if chk[y, 0] and not bg[y, 0]:
            bg[y, 0] = True
        if chk[y, w - 1] and not bg[y, w - 1]:
            bg[y, w - 1] = True

    # Simple flood fill.
    stack = [(y, x) for y in range(h) for x in range(w) if bg[y, x]]
    while stack:
        y, x = stack.pop()
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and chk[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True
                stack.append((ny, nx))
    return bg


def checker_mask(r: np.ndarray, g: np.ndarray, b: np.ndarray, tol: int = 36) -> np.ndarray:
    """Pixels that match the gray/white checker tiles (not your subject)."""
    lum = (r.astype(np.int32) + g.astype(np.int32) + b.astype(np.int32)) / 3
    tile = np.zeros(r.shape, dtype=bool)
    for cr, cg, cb in CHECKER_TILES:
        tile |= (np.abs(r - cr) <= tol) & (np.abs(g - cg) <= tol) & (np.abs(b - cb) <= tol)
    neu = neutral_mask(r, g, b)
    return (tile & (lum >= 158)) | (neu & (lum >= 145) & (lum <= 255))


def rebuild() -> None:
    if not BACKUP.exists():
        raise SystemExit(f"Missing source {BACKUP}")

    ref = np.array(Image.open(BACKUP).convert("RGBA"), dtype=np.uint8)
    h, w = ref.shape[:2]
    r, g, b = ref[:, :, 0], ref[:, :, 1], ref[:, :, 2]
    chk = checker_mask(r, g, b)

    data = ref.copy()
    # Only edge-connected checker tiles (sides + top) become transparent;
    # all interior pixels, including chest and eyes, keep their original RGB/alpha.
    edge_chk = flood_checker_from_edges(chk)
    data[:, :, 3] = 255
    data[edge_chk, 3] = 0

    Image.fromarray(data, "RGBA").save(OUT, optimize=True)

    print(f"Wrote {OUT} ({w}x{h}) - checker tiles -> transparent only; photos intact.")


if __name__ == "__main__":
    rebuild()
