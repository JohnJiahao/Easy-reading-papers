"""Export a Markdown paper report to Word (.docx).

Usage:
    python export_docx.py <report.md> [report.docx]

LaTeX math is rendered to images and embedded, so Word shows formulas
instead of $...$ source. Images referenced by the report are embedded too.
"""

import argparse
import re
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

BODY_FONT = "仿宋_GB2312"
LATIN_FONT = "Times New Roman"
MAX_WIDTH_CM = 15.5
BODY_SIZE = 14
INDENT = Pt(BODY_SIZE * 2)
HIGHLIGHT = "FFF2A8"
KEY_RE = re.compile(
    r"(\d+(?:\.\d+)?\s*%|\d+(?:\.\d+)?\s*(?:亿|万)\s*元|P\s*[<>=]\s*[0-9.]+|"
    r"OR\s*=\s*\d+(?:\.\d+)?|±\s*\d+(?:\.\d+)?|不一致|矛盾|显著|但是|然而|局限)"
)


def set_run_font(run, name=BODY_FONT, size=BODY_SIZE, bold=None, color=None, highlight=False):
    run.font.name = LATIN_FONT
    rfonts = run._element.rPr.rFonts
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:ascii"), LATIN_FONT)
    rfonts.set(qn("w:hAnsi"), LATIN_FONT)
    run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor(*color)
    if highlight:
        r_pr = run._element.get_or_add_rPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), HIGHLIGHT)
        r_pr.append(shd)


def shade(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def add_bottom_border(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "D0D7DE")
    borders.append(bottom)
    p_pr.append(borders)


def split_row(line):
    line = line.strip().strip("|")
    line = line.replace(r"\|", "\x00")
    cells = [c.strip().replace("\x00", "|") for c in line.split("|")]
    return cells


class Exporter:
    def __init__(self, md_path):
        self.md_path = Path(md_path)
        self.base = self.md_path.parent
        self.tmp = tempfile.TemporaryDirectory()
        self.eq_cache = {}
        self.highlight_next = False
        self.doc = Document()
        self._setup_page()

    def _setup_page(self):
        section = self.doc.sections[0]
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.2)
        section.bottom_margin = Cm(2.2)
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)

        style = self.doc.styles["Normal"]
        style.font.name = LATIN_FONT
        style.font.size = Pt(BODY_SIZE)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
        style._element.rPr.rFonts.set(qn("w:ascii"), LATIN_FONT)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), LATIN_FONT)
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_after = Pt(4)

    def render_math(self, latex, display=False):
        key = ("D" if display else "I") + latex
        if key in self.eq_cache:
            return self.eq_cache[key]
        fontsize = 16 if display else 14
        fig = plt.figure(figsize=(0.01, 0.01))
        try:
            fig.text(0, 0, "$" + latex + "$", fontsize=fontsize)
            path = Path(self.tmp.name) / f"eq_{len(self.eq_cache)}.png"
            fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.02, transparent=True)
        except Exception:
            plt.close(fig)
            fig = plt.figure(figsize=(0.01, 0.01))
            plain = re.sub(r"\\[a-zA-Z]+", "", latex).replace("{", "").replace("}", "")
            fig.text(0, 0, plain, fontsize=fontsize)
            path = Path(self.tmp.name) / f"eq_{len(self.eq_cache)}.png"
            fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.02, transparent=True)
        plt.close(fig)
        self.eq_cache[key] = path
        return path

    def add_math(self, paragraph, latex, display=False):
        path = self.render_math(latex, display)
        width_px, height_px = Image.open(path).size
        max_h = Cm(1.1) if display else Cm(0.6)
        max_w = Cm(MAX_WIDTH_CM if display else 8.5)
        height = max_h
        width = int(height * width_px / height_px)
        if width > max_w:
            width = max_w
            height = int(width * height_px / width_px)
        run = paragraph.add_run()
        run.add_picture(str(path), width=width, height=height)

    def add_text(self, paragraph, text, size, bold=False, highlight=False, color=None):
        run = paragraph.add_run(text)
        set_run_font(run, size=size, bold=bold or None, color=color, highlight=highlight)
        return run

    def add_inline(self, paragraph, text, size=BODY_SIZE, base_bold=False, highlight=False, key_highlight=True):
        tokens = re.split(r"(\$[^$]+\$|\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))", text)
        for token in tokens:
            if not token:
                continue
            if token.startswith("$") and token.endswith("$") and len(token) > 2:
                self.add_math(paragraph, token[1:-1].strip())
            elif token.startswith("**") and token.endswith("**"):
                self.add_text(paragraph, token[2:-2], size, bold=True, highlight=highlight)
            elif token.startswith("`") and token.endswith("`"):
                self.add_text(paragraph, token[1:-1], size - 0.5)
            elif token.startswith("[") and "](" in token:
                m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", token)
                self.add_text(paragraph, m.group(1), size, color=(11, 92, 173))
            elif key_highlight:
                parts = KEY_RE.split(token)
                for part in parts:
                    if not part:
                        continue
                    self.add_text(
                        paragraph,
                        part,
                        size,
                        bold=base_bold,
                        highlight=highlight or bool(KEY_RE.fullmatch(part)),
                    )
            else:
                self.add_text(paragraph, token, size, bold=base_bold, highlight=highlight)

    def heading(self, text, level):
        self.highlight_next = level == 2 and ("一句话结论" in text or "One-sentence" in text)
        if level == 1:
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text)
            set_run_font(run, BODY_FONT, 22, bold=True)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(14)
        elif level == 2:
            p = self.doc.add_paragraph()
            run = p.add_run(text)
            set_run_font(run, BODY_FONT, 16, bold=True, color=(31, 78, 121))
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            add_bottom_border(p)
        else:
            p = self.doc.add_paragraph()
            run = p.add_run(text)
            set_run_font(run, BODY_FONT, 14, bold=True, color=(46, 117, 182))
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)

    def paragraph(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = INDENT
        highlight = self.highlight_next
        self.highlight_next = False
        self.add_inline(p, text, highlight=highlight)
        return p

    def quote(self, lines):
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.right_indent = Cm(0.5)
        p.paragraph_format.first_line_indent = INDENT
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        p_pr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "F3F8FE")
        p_pr.append(shd)
        self.add_inline(p, " ".join(lines), size=BODY_SIZE)

    def bullet(self, text):
        p = self.doc.add_paragraph(style="List Bullet")
        self.add_inline(p, text)

    def numbered(self, text):
        p = self.doc.add_paragraph(style="List Number")
        self.add_inline(p, text)

    def code(self, lines):
        for line in lines:
            p = self.doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(line if line else " ")
            set_run_font(run, BODY_FONT, 10.5)
            p_pr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:fill"), "F6F8FA")
            p_pr.append(shd)

    def image(self, alt, src):
        path = (self.base / src).resolve()
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if path.exists():
            with Image.open(path) as im:
                w, h = im.size
            width = Cm(MAX_WIDTH_CM)
            if width * h / w > Cm(11):
                width = Cm(11) * w / h
            p.add_run().add_picture(str(path), width=width)
            cap = self.doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = cap.add_run(alt)
            set_run_font(run, BODY_FONT, 10.5, color=(87, 96, 106))
        else:
            run = p.add_run(f"[图片缺失：{src}]")
            set_run_font(run, BODY_FONT, 10.5, color=(180, 0, 0))

    def table(self, rows):
        if not rows:
            return
        ncols = len(rows[0])
        table = self.doc.add_table(rows=len(rows), cols=ncols)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r, row in enumerate(rows):
            for c in range(ncols):
                cell = table.cell(r, c)
                cell.text = ""
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(0)
                text = row[c] if c < len(row) else ""
                self.add_inline(p, text, size=10.5, key_highlight=False)
                if r == 0:
                    for run in p.runs:
                        run.font.bold = True
                    shade(cell, "DEEAF6")

    def hr(self):
        p = self.doc.add_paragraph()
        add_bottom_border(p)

    def convert(self):
        text = self.md_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            end = 1
            while end < len(lines) and lines[end].strip() != "---":
                end += 1
            meta = lines[1:end]
            body = lines[end + 1 :]
        else:
            meta, body = [], lines

        title = ""
        for line in meta:
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip()
                break
        if title:
            self.heading(title, 1)
        title_is_cjk = bool(re.search(r"[\u4e00-\u9fff]", title))

        i = 0
        while i < len(body):
            line = body[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            if stripped.startswith("```"):
                i += 1
                code_lines = []
                while i < len(body) and not body[i].strip().startswith("```"):
                    code_lines.append(body[i])
                    i += 1
                i += 1
                self.code(code_lines)
                continue

            if stripped.startswith("$$"):
                i += 1
                math_lines = []
                if stripped != "$$":
                    math_lines.append(stripped[2:])
                while i < len(body) and "$$" not in body[i]:
                    math_lines.append(body[i].strip())
                    i += 1
                if i < len(body):
                    tail = body[i].strip()
                    if tail != "$$":
                        math_lines.append(tail.replace("$$", ""))
                    i += 1
                p = self.doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                self.add_math(p, " ".join(math_lines).strip(), display=True)
                continue

            m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
            if m:
                if len(m.group(1)) != 1 or not title_is_cjk:
                    self.heading(m.group(2).strip(), len(m.group(1)))
                i += 1
                continue

            if stripped.startswith("|") and i + 1 < len(body) and re.match(r"^\|[\s:\-|]+\|$", body[i + 1].strip()):
                rows = []
                rows.append(split_row(stripped))
                i += 2
                while i < len(body) and body[i].strip().startswith("|"):
                    rows.append(split_row(body[i].strip()))
                    i += 1
                self.table(rows)
                continue

            m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
            if m:
                self.image(m.group(1), m.group(2))
                i += 1
                continue

            if stripped.startswith(">"):
                qlines = []
                while i < len(body) and body[i].strip().startswith(">"):
                    qlines.append(body[i].strip()[1:].strip())
                    i += 1
                self.quote([q for q in qlines if q])
                continue

            if re.match(r"^[-*]\s+", stripped):
                items = []
                while i < len(body) and re.match(r"^[-*]\s+", body[i].strip()):
                    items.append(re.sub(r"^[-*]\s+", "", body[i].strip()))
                    i += 1
                for item in items:
                    if title_is_cjk and re.match(r"^(\*\*)?(题目|中文题名)", item):
                        continue
                    self.bullet(item)
                continue

            if re.match(r"^\d+\.\s+", stripped):
                items = []
                while i < len(body) and re.match(r"^\d+\.\s+", body[i].strip()):
                    items.append(re.sub(r"^\d+\.\s+", "", body[i].strip()))
                    i += 1
                for item in items:
                    self.numbered(item)
                continue

            if stripped == "---":
                self.hr()
                i += 1
                continue

            para = [stripped]
            i += 1
            while i < len(body):
                nxt = body[i].strip()
                if (
                    not nxt
                    or nxt.startswith("#")
                    or nxt.startswith("```")
                    or nxt.startswith("$$")
                    or nxt.startswith("|")
                    or nxt.startswith(">")
                    or nxt.startswith("![")
                    or re.match(r"^[-*]\s+", nxt)
                    or re.match(r"^\d+\.\s+", nxt)
                    or nxt == "---"
                ):
                    break
                para.append(nxt)
                i += 1
            self.paragraph(" ".join(para))

        out = Path(self.out_path)
        try:
            self.doc.save(out)
        except PermissionError:
            print(f"skipped (file is open in Word/WPS): {out}")
            self.tmp.cleanup()
            return None
        self.tmp.cleanup()
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown", nargs="?")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--latest", action="store_true", help="convert the newest report under papers/")
    ap.add_argument("--all", action="store_true", help="convert every report under papers/")
    ap.add_argument("--remove-source", action="store_true", help="delete the Markdown source after a successful export")
    args = ap.parse_args()

    if args.all:
        reports = sorted((Path.cwd() / "papers").rglob("report.md"))
    elif args.latest:
        candidates = list((Path.cwd() / "papers").rglob("report.md"))
        reports = [max(candidates, key=lambda p: p.stat().st_mtime)] if candidates else []
    else:
        reports = [Path(args.markdown or "report.md")]

    if not reports:
        raise SystemExit("no report.md found")

    for md in reports:
        out = Path(args.output) if (args.output and len(reports) == 1) else md.with_suffix(".docx")
        exp = Exporter(md)
        exp.out_path = out
        result = exp.convert()
        if result:
            print(f"saved {result}")
            if args.remove_source and md.exists():
                md.unlink()
                print(f"removed {md}")


if __name__ == "__main__":
    main()
