#!/usr/bin/env python3
"""Build 4차시험.pdf — half-page (left column only) cheating paper.

- Font size 11pt body
- Answers in red
- Professors in 가나다 order
- Confirmed Q&A + top 1–2 predicted per professor
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path

import fitz
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["mathtext.fontset"] = "cm"

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "문제은행" / "4차시험"
FONTS_DIR = Path(__file__).resolve().parent / "fonts"
KOREAN_FONT_FILE = FONTS_DIR / "NanumGothic.ttf"
KOREAN_BOLD_FONT_FILE = FONTS_DIR / "NanumGothicBold.ttf"
FALLBACK_FONT_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FALLBACK_BOLD_FONT_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

OUTPUT_PDF = BANK / "치팅페이퍼.pdf"
# also keep legacy name for convenience
OUTPUT_PDF_ALIAS = BANK / "4차시험.pdf"
SOURCE_MD = BANK / "치팅페이퍼.md"

# ---------------------------------------------------------------------------
# Math
# ---------------------------------------------------------------------------
_MATH_CACHE: dict[tuple[str, float, bool], tuple[bytes, int, int]] = {}


def render_math_png(latex: str, fontsize: float, display: bool) -> tuple[bytes, int, int]:
    key = (latex, fontsize, display)
    if key in _MATH_CACHE:
        return _MATH_CACHE[key]
    latex = re.sub(r"\s+", " ", latex.strip())

    def _save(expr: str, family: str | None = None) -> tuple[bytes, int, int]:
        fig = plt.figure(figsize=(0.01, 0.01))
        try:
            kwargs = {"fontsize": fontsize}
            if family:
                kwargs["family"] = family
            fig.text(0.5, 0.5, expr, ha="center", va="center", **kwargs)
            buf = io.BytesIO()
            fig.savefig(
                buf,
                format="png",
                dpi=fig.get_dpi(),
                transparent=False,
                facecolor="white",
                bbox_inches="tight",
                pad_inches=0.03,
            )
        finally:
            plt.close(fig)
        png = buf.getvalue()
        w_px = int.from_bytes(png[16:20], "big")
        h_px = int.from_bytes(png[20:24], "big")
        return png, w_px, h_px

    try:
        result = _save(f"${latex}$")
    except Exception:
        result = _save(latex, family="monospace")
    _MATH_CACHE[key] = result
    return result


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
_FONT_CACHE: dict[str, fitz.Font] = {}
_FONT_PATHS = {
    "body": KOREAN_FONT_FILE,
    "bold": KOREAN_BOLD_FONT_FILE,
    "fallback": FALLBACK_FONT_FILE,
    "fallback_bold": FALLBACK_BOLD_FONT_FILE,
}


def get_font(name: str = "body") -> fitz.Font:
    if name not in _FONT_CACHE:
        _FONT_CACHE[name] = fitz.Font(fontfile=str(_FONT_PATHS[name]))
    return _FONT_CACHE[name]


def has_glyph(font: fitz.Font, ch: str) -> bool:
    try:
        return bool(font.has_glyph(ord(ch)))
    except Exception:
        return font.text_length(ch, fontsize=10) > 0.5


def runs_for_text(text: str, bold: bool) -> list[tuple[str, str]]:
    primary = "bold" if bold else "body"
    fallback = "fallback_bold" if bold else "fallback"
    primary_font = get_font(primary)
    fallback_font = get_font(fallback)
    runs: list[tuple[str, str]] = []
    cur_text: list[str] = []
    cur_kind: str | None = None

    def flush():
        nonlocal cur_text, cur_kind
        if cur_text:
            runs.append(("".join(cur_text), cur_kind or primary))
            cur_text.clear()
            cur_kind = None

    for ch in text:
        if ch in (" ", "\t") or has_glyph(primary_font, ch):
            kind = primary
        elif has_glyph(fallback_font, ch):
            kind = fallback
        else:
            kind = primary
        if cur_kind is None:
            cur_kind = kind
        if kind != cur_kind:
            flush()
            cur_kind = kind
        cur_text.append(ch)
    flush()
    return runs


def measure(text: str, fontsize: float, bold: bool = False) -> float:
    total = 0.0
    for piece, kind in runs_for_text(text, bold):
        total += get_font(kind).text_length(piece, fontsize=fontsize)
    return total


# ---------------------------------------------------------------------------
# Elements
# ---------------------------------------------------------------------------
@dataclass
class Element:
    kind: str  # h1,h2,h3,h4,para,bullet,math_block,rule,answer_start,answer_end
    content: object
    bold: bool = False


def strip_bold_markers(text: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", r"\1", text)


def parse_markdown(text: str) -> list[Element]:
    lines = text.replace("\r\n", "\n").split("\n")
    elements: list[Element] = []
    i = 0
    in_block_math = False
    math_buf: list[str] = []
    in_answer = False

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # Explicit answer markers
        if stripped == "[[ANSWER]]":
            in_answer = True
            elements.append(Element("answer_start", ""))
            i += 1
            continue
        if stripped == "[[/ANSWER]]":
            in_answer = False
            elements.append(Element("answer_end", ""))
            i += 1
            continue

        # One-line $$...$$
        if (
            not in_block_math
            and stripped.startswith("$$")
            and stripped.endswith("$$")
            and len(stripped) > 4
        ):
            elements.append(Element("math_block", stripped[2:-2].strip()))
            i += 1
            continue
        if not in_block_math and stripped == "$$":
            in_block_math = True
            math_buf = []
            i += 1
            continue
        if in_block_math and stripped == "$$":
            elements.append(Element("math_block", "\n".join(math_buf).strip()))
            math_buf = []
            in_block_math = False
            i += 1
            continue
        if in_block_math:
            math_buf.append(raw)
            i += 1
            continue

        # \[ ... \] display math
        if stripped == r"\[":
            math_buf = []
            i += 1
            while i < len(lines) and lines[i].strip() != r"\]":
                math_buf.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1  # skip \]
            elements.append(Element("math_block", "\n".join(math_buf).strip()))
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", raw)
        if m:
            level = len(m.group(1))
            elements.append(Element(f"h{min(level, 4)}", m.group(2).rstrip()))
            i += 1
            continue

        if re.match(r"^-{3,}\s*$", stripped):
            elements.append(Element("rule", ""))
            i += 1
            continue

        m = re.match(r"^(\s*)[-*]\s+(.*)$", raw)
        if m:
            elements.append(Element("bullet", (len(m.group(1)), m.group(2))))
            i += 1
            continue

        if stripped.startswith(">"):
            elements.append(Element("para", stripped[1:].lstrip()))
            i += 1
            continue

        if not stripped:
            elements.append(Element("rule", "blank"))
            i += 1
            continue

        elements.append(Element("para", raw.rstrip()))
        i += 1

    if in_block_math and math_buf:
        elements.append(Element("math_block", "\n".join(math_buf).strip()))
    return elements


INLINE_TOKEN_RE = re.compile(
    r"(\$[^$\n]+\$)"
    r"|(\\\([^)]+\\\))"  # \( ... \) simple single-line
    r"|(\*\*[^*]+\*\*)"
    r"|(`[^`]+`)"
)


def split_inline(text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    pos = 0
    for m in INLINE_TOKEN_RE.finditer(text):
        if m.start() > pos:
            out.append(("text", text[pos : m.start()]))
        token = m.group(0)
        if token.startswith("$"):
            out.append(("math", token[1:-1]))
        elif token.startswith(r"\("):
            out.append(("math", token[2:-2]))
        elif token.startswith("**"):
            out.append(("bold", token[2:-2]))
        elif token.startswith("`"):
            out.append(("code", token[1:-1]))
        pos = m.end()
    if pos < len(text):
        out.append(("text", text[pos:]))
    return out


# ---------------------------------------------------------------------------
# PDF Writer
# ---------------------------------------------------------------------------
PRIMARY = (0.12, 0.25, 0.55)
ACCENT = (0.75, 0.25, 0.05)
ANSWER_RED = (0.92, 0.05, 0.05)  # vivid red for answer body
MUTED = (0.35, 0.35, 0.35)
HAIRLINE = (0.80, 0.80, 0.80)
BODY_COLOR = (0.06, 0.06, 0.10)


class PdfWriter:
    PAGE_WIDTH = 595.0
    PAGE_HEIGHT = 842.0
    MARGIN_X = 28.0
    MARGIN_TOP = 48.0
    MARGIN_BOTTOM = 36.0
    BODY_SIZE = 11.0
    BODY_LH = 14.2
    BULLET_INDENT = 10.0

    def __init__(self, header: str):
        self.doc = fitz.open()
        self.header = header
        # Left half only (2-column layout, content on left)
        self.right_x = self.PAGE_WIDTH / 2 - 6
        self.font_names = {
            "body": "kbody",
            "bold": "kbold",
            "fallback": "fbody",
            "fallback_bold": "fbold",
        }
        self.font_files = {k: str(_FONT_PATHS[k]) for k in self.font_names}
        self.page = None
        self.y = 0.0
        self.page_no = 0
        self.in_answer = False
        self._new_page()

    @property
    def content_width(self) -> float:
        return self.right_x - self.MARGIN_X

    def _new_page(self):
        self.page = self.doc.new_page(width=self.PAGE_WIDTH, height=self.PAGE_HEIGHT)
        for kind, alias in self.font_names.items():
            self.page.insert_font(fontfile=self.font_files[kind], fontname=alias)
        self.page_no += 1
        self._draw_runs(self.header, self.MARGIN_X, 26, 8, MUTED)
        pl = f"- {self.page_no} -"
        self._draw_runs(pl, self.right_x - measure(pl, 8), 26, 8, MUTED)
        self.page.draw_line(
            (self.MARGIN_X, 34),
            (self.right_x, 34),
            color=HAIRLINE,
            width=0.5,
        )
        mid = self.PAGE_WIDTH / 2
        self.page.draw_line(
            (mid, 20),
            (mid, self.PAGE_HEIGHT - 20),
            color=(0.88, 0.88, 0.88),
            width=0.4,
            dashes="[2 3] 0",
        )
        note = "손필기 메모란 →"
        self._draw_runs(note, mid + 10, 26, 8, (0.70, 0.70, 0.70))
        self.y = self.MARGIN_TOP

    def ensure(self, needed: float):
        if self.y + needed > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self._new_page()

    def vspace(self, h: float):
        self.ensure(h)
        self.y += h

    def _draw_runs(
        self, text: str, x: float, y: float, size: float, color, bold: bool = False
    ) -> float:
        cur_x = x
        for piece, kind in runs_for_text(text, bold):
            self.page.insert_text(
                (cur_x, y),
                piece,
                fontname=self.font_names[kind],
                fontfile=self.font_files[kind],
                fontsize=size,
                color=color,
            )
            cur_x += get_font(kind).text_length(piece, fontsize=size)
        return cur_x

    def _text_color(self):
        return ANSWER_RED if self.in_answer else BODY_COLOR

    def _measure_inline_run(self, kind: str, payload, size: float) -> tuple[float, float]:
        if kind == "math":
            _, w_pt, h_pt = payload
            return w_pt + 1, h_pt
        if kind == "bold":
            return measure(payload, size, bold=True), size
        return measure(payload, size, bold=False), size

    def _layout_inline(
        self, inline_parts: list[tuple[str, str]], max_width: float, size: float
    ) -> list[list[tuple[str, object]]]:
        math_target_h = size * 1.35
        prepared: list[tuple[str, object]] = []
        for kind, content in inline_parts:
            if kind == "math":
                base_fs = size * 1.3
                png, w_px, h_px = render_math_png(content, base_fs, display=False)
                px_to_pt = 0.72
                w_pt = w_px * px_to_pt
                h_pt = h_px * px_to_pt
                scale = math_target_h / h_pt if h_pt > 0 else 1.0
                prepared.append(("math", (png, w_pt * scale, h_pt * scale)))
            else:
                prepared.append((kind, content))

        lines: list[list[tuple[str, object]]] = [[]]
        cur_w = 0.0

        def push(kind, payload):
            nonlocal cur_w
            w, _ = self._measure_inline_run(kind, payload, size)
            if cur_w + w > max_width and lines[-1]:
                lines.append([])
                cur_w = 0.0
            lines[-1].append((kind, payload))
            cur_w += w

        for kind, payload in prepared:
            if kind == "text":
                atoms = re.findall(
                    r"\s+|[A-Za-z0-9_'\-.,;:()/!?@#$%&*+=<>\[\]{}|\\^~`\"]+|[^\s]",
                    payload,
                )
                for atom in atoms:
                    if atom == "" or (atom.isspace() and not lines[-1]):
                        continue
                    w = measure(atom, size, bold=False)
                    if cur_w + w > max_width and lines[-1] and atom.strip():
                        lines.append([])
                        cur_w = 0.0
                    if lines[-1] and lines[-1][-1][0] == "text":
                        prev = lines[-1][-1][1]
                        lines[-1][-1] = ("text", prev + atom)
                    else:
                        lines[-1].append(("text", atom))
                    cur_w += w
            else:
                push(kind, payload)
        for line in lines:
            while line and line[0][0] == "text" and not line[0][1].strip():
                line.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        return lines

    def _draw_inline_line(self, runs, x, size, baseline_y):
        cur_x = x
        color = self._text_color()
        for kind, payload in runs:
            if kind == "math":
                png, w_pt, h_pt = payload
                top = baseline_y - h_pt + 1
                rect = fitz.Rect(cur_x, top, cur_x + w_pt, top + h_pt)
                self.page.insert_image(rect, stream=png)
                cur_x += w_pt + 1
            elif kind == "bold":
                cur_x = self._draw_runs(payload, cur_x, baseline_y, size, color, bold=True)
            else:
                cur_x = self._draw_runs(payload, cur_x, baseline_y, size, color, bold=False)
        return cur_x

    def write_heading(self, level: int, text: str):
        text = strip_bold_markers(text).strip()
        if not text:
            return
        sizes = {1: 13.5, 2: 12.0, 3: 11.2, 4: 11.0}
        size = sizes.get(level, 11.0)
        line_h = size * 1.35
        if level == 1:
            self.ensure(line_h + 12)
            band = fitz.Rect(self.MARGIN_X, self.y, self.right_x, self.y + line_h + 8)
            self.page.draw_rect(band, color=PRIMARY, fill=PRIMARY)
            self._draw_runs(
                text, self.MARGIN_X + 8, self.y + size + 4, size, (1, 1, 1), bold=True
            )
            self.y += line_h + 12
            return
        if level == 2:
            self.vspace(4)
            self.ensure(line_h + 6)
            bar = fitz.Rect(self.MARGIN_X, self.y + 1, self.MARGIN_X + 3, self.y + line_h - 2)
            self.page.draw_rect(bar, color=PRIMARY, fill=PRIMARY)
            self._draw_runs(
                text, self.MARGIN_X + 8, self.y + size, size, PRIMARY, bold=True
            )
            self.y += line_h
            self.page.draw_line(
                (self.MARGIN_X, self.y),
                (self.right_x, self.y),
                color=HAIRLINE,
                width=0.35,
            )
            self.y += 4
            return
        if level == 3:
            self.vspace(3)
            self.ensure(line_h + 2)
            self._draw_runs(text, self.MARGIN_X, self.y + size, size, ACCENT, bold=True)
            self.y += line_h
            return
        self.vspace(2)
        self.ensure(line_h + 2)
        self._draw_runs(text, self.MARGIN_X, self.y + size, size, ACCENT, bold=True)
        self.y += line_h

    def write_paragraph(self, text: str, indent: float = 0.0, leading: str = ""):
        text = text.rstrip()
        if not text.strip():
            self.vspace(2)
            return
        parts = split_inline(text)
        max_w = (
            self.content_width
            - indent
            - measure(leading, self.BODY_SIZE, bold=False)
            - 2
        )
        lines = self._layout_inline(parts, max_w, self.BODY_SIZE)
        if not lines:
            self.vspace(2)
            return
        for idx, line in enumerate(lines):
            heights = [
                self._measure_inline_run(k, p, self.BODY_SIZE)[1] for k, p in line
            ]
            line_h = max(self.BODY_LH, *heights) if heights else self.BODY_LH
            self.ensure(line_h)
            x = self.MARGIN_X + indent
            if idx == 0 and leading:
                lead_color = ANSWER_RED if self.in_answer else ACCENT
                x = self._draw_runs(
                    leading, x, self.y + self.BODY_SIZE, self.BODY_SIZE, lead_color, bold=True
                )
                x += 2
            elif leading:
                x += measure(leading, self.BODY_SIZE, bold=False) + 2
            self._draw_inline_line(line, x, self.BODY_SIZE, self.y + self.BODY_SIZE)
            self.y += self.BODY_LH

    def write_bullet(self, indent_chars: int, text: str):
        depth = indent_chars // 2
        indent = self.BULLET_INDENT + depth * 10
        bullet = "•" if depth == 0 else "·"
        self.write_paragraph(text, indent=indent, leading=bullet + " ")

    def write_math_block(self, latex: str):
        base_fs = self.BODY_SIZE * 1.55
        png, w_px, h_px = render_math_png(latex, base_fs, display=True)
        px_to_pt = 0.72
        w_pt = w_px * px_to_pt
        h_pt = h_px * px_to_pt
        max_w = self.content_width - 8
        if w_pt > max_w:
            scale = max_w / w_pt
            w_pt *= scale
            h_pt *= scale
        self.ensure(h_pt + 4)
        x = self.MARGIN_X + (self.content_width - w_pt) / 2
        rect = fitz.Rect(x, self.y, x + w_pt, self.y + h_pt)
        self.page.insert_image(rect, stream=png)
        self.y += h_pt + 4

    def render_elements(self, elements: list[Element]):
        for el in elements:
            if el.kind == "answer_start":
                self.in_answer = True
                # small red label
                self.vspace(1)
                self.ensure(self.BODY_LH)
                self._draw_runs(
                    "【답안】",
                    self.MARGIN_X,
                    self.y + self.BODY_SIZE,
                    self.BODY_SIZE,
                    ANSWER_RED,
                    bold=True,
                )
                self.y += self.BODY_LH
                continue
            if el.kind == "answer_end":
                self.in_answer = False
                self.vspace(2)
                continue
            if el.kind.startswith("h"):
                self.write_heading(int(el.kind[1]), str(el.content))
            elif el.kind == "para":
                self.write_paragraph(str(el.content))
            elif el.kind == "bullet":
                ind, txt = el.content  # type: ignore
                self.write_bullet(ind, txt)
            elif el.kind == "math_block":
                self.write_math_block(str(el.content))
            elif el.kind == "rule":
                if el.content == "blank":
                    self.vspace(2)
                else:
                    self.vspace(2)
                    self.page.draw_line(
                        (self.MARGIN_X, self.y),
                        (self.right_x, self.y),
                        color=HAIRLINE,
                        width=0.3,
                    )
                    self.vspace(3)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(path))
        self.doc.close()
        print(f"Wrote {path} ({self.page_no} pages)")


def main():
    if not SOURCE_MD.exists():
        raise SystemExit(f"Missing source: {SOURCE_MD}")
    text = SOURCE_MD.read_text(encoding="utf-8")
    elements = parse_markdown(text)
    writer = PdfWriter("Samsung AI Expert 2026 · 4차시험 치팅페이퍼 (왼쪽=문제·답안 / 오른쪽=메모)")
    writer.render_elements(elements)
    writer.save(OUTPUT_PDF)
    # mirror to 4차시험.pdf if different path
    if OUTPUT_PDF_ALIAS != OUTPUT_PDF:
        import shutil
        shutil.copy2(OUTPUT_PDF, OUTPUT_PDF_ALIAS)
        print(f"Also copied to {OUTPUT_PDF_ALIAS}")


if __name__ == "__main__":
    main()
