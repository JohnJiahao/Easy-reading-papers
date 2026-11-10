"""Extract figures (and their captions) from a PDF into PNG files.

Usage:
    python extract_figures.py paper.pdf figures/ [--dpi 216]

Outputs fig-01.png, fig-02.png ... plus manifest.csv (fig,page,caption,file,w,h,status).
Preference order: embedded raster images + clustered vector drawings that sit
directly above a caption; falls back to the column band above the caption.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

import fitz

CAP_RE = re.compile(r"^\s*(?:Fig(?:ure)?\.?|图)\s*(\d+)", re.I)
SKIP_RE = re.compile(
    r"^\s*(?:Fig\.?|图)\s*\d+\s*(?:illustrates|shows|presents|displays|depicts|gives|所示|展示|给出)",
    re.I,
)


def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("outdir")
    ap.add_argument("--dpi", type=int, default=216)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    try:
        fitz.TOOLS.mupdf_display_errors(False)
        fitz.TOOLS.mupdf_display_warnings(False)
    except Exception:
        pass
    zoom = args.dpi / 72.0
    rows = {}

    for pno in range(doc.page_count):
        page = doc[pno]
        width, height = page.rect.width, page.rect.height
        blocks = page.get_text("dict")["blocks"]

        caps = []
        for b in blocks:
            if b["type"] != 0:
                continue
            text = " ".join(s["text"] for l in b["lines"] for s in l["spans"]).strip()
            m = CAP_RE.match(text)
            if not m or SKIP_RE.match(text):
                continue
            caps.append({"no": int(m.group(1)), "bbox": b["bbox"], "text": text})

        if not caps:
            continue

        cands = [b["bbox"] for b in blocks if b["type"] == 1 and b["bbox"][3] - b["bbox"][1] > 18]
        try:
            for r in page.cluster_drawings():
                if r.width > 18 and r.height > 18:
                    cands.append((r.x0, r.y0, r.x1, r.y1))
        except Exception:
            pass

        for cap in sorted(caps, key=lambda c: c["bbox"][1]):
            cx0, cy0, cx1, cy1 = cap["bbox"]
            clip, status = None, "ok"

            above = [
                c
                for c in cands
                if c[3] <= cy0 + 6 and c[1] >= cy0 - 520 and overlap(c[0], c[2], cx0, cx1) > 8
            ]
            above.sort(key=lambda c: c[3], reverse=True)

            if above and cy0 - above[0][3] <= 40:
                x0, y0, x1, y1 = above[0]
                for c in above[1:]:
                    if y0 - c[3] > 24:
                        break
                    if overlap(c[0], c[2], x0, x1) <= 0:
                        continue
                    x0, y0 = min(x0, c[0]), min(y0, c[1])
                    x1, y1 = max(x1, c[2]), max(y1, c[3])
                clip = fitz.Rect(x0 - 5, y0 - 5, x1 + 5, cy1 + 3)

            if clip is not None and clip.width < (cx1 - cx0) * 0.6:
                clip.x0 = max(20, min(clip.x0, cx0 - 6))
                clip.x1 = min(width - 20, max(clip.x1, cx1 + 6))
                status = "check-crop"

            if clip is None or clip.height < 45 or clip.width < 55:
                mid = width / 2
                left = (cx0 + cx1) / 2 < mid
                x0, x1 = (30, mid + 8) if left else (mid - 8, width - 30)
                clip = fitz.Rect(x0, max(30, cy0 - 280), x1, cy1 + 3)
                status = "fallback"

            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
            file = f"fig-{cap['no']:02d}.png"
            if pix.width < 300 or pix.height < 120:
                status = "check-crop" if status == "ok" else status
            prev = rows.get(cap["no"])
            if prev and prev["w"] * prev["h"] >= pix.width * pix.height:
                continue
            pix.save(outdir / file)
            rows[cap["no"]] = {
                "fig": cap["no"],
                "page": pno + 1,
                "caption": cap["text"].replace("\n", " "),
                "file": file,
                "w": pix.width,
                "h": pix.height,
                "status": status,
            }

    with (outdir / "manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["fig", "page", "caption", "file", "w", "h", "status"])
        writer.writeheader()
        for key in sorted(rows):
            writer.writerow(rows[key])

    print(f"{len(rows)} figures -> {outdir}")


if __name__ == "__main__":
    sys.exit(main())
