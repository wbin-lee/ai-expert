"""Build 2차시험_치팅페이어.pdf with rendered LaTeX math.

Combines six markdown files (3 professors × {기출확정, 예상문제} where present)
into a single quick-review PDF. Inline $...$ and block $$...$$ math are
rendered as PNG images via matplotlib mathtext and embedded in the layout;
all other text is drawn with NanumGothic so Korean renders cleanly.
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

# Tell mathtext to use STIX fonts which support a broader range of symbols.
matplotlib.rcParams["mathtext.fontset"] = "cm"


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "문제은행" / "2차시험"
FONTS_DIR = Path(__file__).resolve().parent / "fonts"
KOREAN_FONT_FILE = FONTS_DIR / "NanumGothic.ttf"
KOREAN_BOLD_FONT_FILE = FONTS_DIR / "NanumGothicBold.ttf"
FALLBACK_FONT_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FALLBACK_BOLD_FONT_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

OUTPUT_PDF = BANK / "2차시험_치팅페이어.pdf"
OUTPUT_PDF_HALF = BANK / "2차시험(다단).pdf"

# Source order. Files marked optional are skipped if missing.
SOURCE_FILES = [
    ("양인순 교수 — 기출확정", BANK / "양인순교수_기출확정.md"),
    ("황승원 교수 — 기출확정", BANK / "황승원교수_기출확정.md"),
    ("황승원 교수 — 예상 문제", BANK / "황승원교수_예상문제.md"),
    ("김찬우 교수 — 기출확정", BANK / "김찬우교수_기출확정.md"),
    ("김희승 교수 — 기출확정", BANK / "김희승교수_기출확정.md"),
    ("김희승 교수 — 예상 문제", BANK / "김희승교수_예상문제.md"),
]


# ---------------------------------------------------------------------------
# Math rendering (matplotlib mathtext → PNG)
# ---------------------------------------------------------------------------

_MATH_CACHE: dict[tuple[str, float, bool], tuple[bytes, int, int]] = {}


def render_math_png(latex: str, fontsize: float, display: bool) -> tuple[bytes, int, int]:
    """Render a LaTeX expression to PNG bytes via matplotlib mathtext.

    Uses bbox_inches="tight" so descenders, large fraction denominators,
    and \\sum / \\int limits are not clipped at the figure boundary.

    Returns (png_bytes, width_px, height_px).
    """
    key = (latex, fontsize, display)
    if key in _MATH_CACHE:
        return _MATH_CACHE[key]

    # mathtext does NOT accept literal newlines inside $...$, so collapse
    # multi-line block math into a single line.
    latex = re.sub(r"\s+", " ", latex.strip())

    def _save(expr: str, family: str | None = None) -> tuple[bytes, int, int]:
        fig = plt.figure(figsize=(0.01, 0.01))
        try:
            kwargs = {"fontsize": fontsize}
            if family:
                kwargs["family"] = family
            fig.text(0.5, 0.5, expr, ha="center", va="center", **kwargs)
            buf = io.BytesIO()
            # bbox_inches="tight" auto-crops to the tight bounding box of
            # the rendered text *including* descenders and oversized glyphs.
            fig.savefig(
                buf,
                format="png",
                dpi=fig.get_dpi(),
                transparent=False,
                facecolor="white",
                bbox_inches="tight",
                pad_inches=0.04,
            )
        finally:
            plt.close(fig)
        png = buf.getvalue()
        # Inspect the resulting PNG to get pixel dimensions.
        # PNG header: width @ bytes 16..20, height @ bytes 20..24 (big-endian).
        w_px = int.from_bytes(png[16:20], "big")
        h_px = int.from_bytes(png[20:24], "big")
        return png, w_px, h_px

    try:
        result = _save(f"${latex}$")
    except Exception:
        # Fallback: dump the raw LaTeX source in monospace so the document
        # still builds even when mathtext rejects the expression.
        result = _save(latex, family="monospace")

    _MATH_CACHE[key] = result
    return result


# ---------------------------------------------------------------------------
# Font helpers (Korean + Latin fallback)
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
# Markdown parsing — emit a flat list of layout instructions
# ---------------------------------------------------------------------------

@dataclass
class Element:
    """One renderable block."""
    kind: str            # 'h1','h2','h3','h4','para','bullet','code','math_block','table','rule'
    content: object      # str for text; for table: list[list[str]]; for math_block: latex str
    bold: bool = False


def parse_markdown(text: str) -> list[Element]:
    """Parse markdown into a flat list of layout elements.

    Supported subset:
      - headings (#, ##, ###, ####)
      - paragraphs (text + inline $...$ math kept in-place)
      - bullet lists ('- ' and '* ')
      - fenced code blocks (```)
      - block math ($$ ... $$)
      - markdown tables (| ... |)
      - thematic break (---)
    """
    lines = text.replace("\r\n", "\n").split("\n")
    elements: list[Element] = []
    i = 0
    in_code = False
    code_buf: list[str] = []
    in_block_math = False
    math_buf: list[str] = []
    table_buf: list[list[str]] = []
    table_active = False

    def flush_table():
        nonlocal table_buf, table_active
        if table_buf:
            elements.append(Element("table", table_buf))
        table_buf = []
        table_active = False

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # Code fences
        if stripped.startswith("```"):
            flush_table()
            if in_code:
                elements.append(Element("code", "\n".join(code_buf)))
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(raw)
            i += 1
            continue

        # Block math fences ($$ ... $$ on lines by themselves OR opening line)
        # Cases:
        #   "$$" (open) ... "$$" (close)
        #   "$$X$$" (one-line block)
        if not in_block_math and stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            flush_table()
            inner = stripped[2:-2].strip()
            elements.append(Element("math_block", inner))
            i += 1
            continue
        if not in_block_math and stripped == "$$":
            flush_table()
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
            # Also support `$$ ... $$` where text trails on opening line
            math_buf.append(raw)
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", raw)
        if m:
            flush_table()
            level = len(m.group(1))
            content = m.group(2).rstrip()
            kind = f"h{min(level, 4)}"
            elements.append(Element(kind, content))
            i += 1
            continue

        # Thematic break
        if re.match(r"^-{3,}\s*$", stripped):
            flush_table()
            elements.append(Element("rule", ""))
            i += 1
            continue

        # Table: a row of `| ... |` followed by a separator row `|---|...`
        if "|" in raw and stripped.startswith("|"):
            # Look ahead one line for separator
            if not table_active:
                # Check next line for separator
                if i + 1 < len(lines):
                    nxt = lines[i + 1].strip()
                    if re.match(r"^\|?\s*:?-{2,}:?", nxt) and "|" in nxt:
                        table_active = True
                        header = [cell.strip() for cell in stripped.strip("|").split("|")]
                        table_buf.append(header)
                        i += 2  # skip header + separator
                        continue
            else:
                row = [cell.strip() for cell in stripped.strip("|").split("|")]
                table_buf.append(row)
                i += 1
                continue
        else:
            flush_table()

        # Bullet
        m = re.match(r"^(\s*)[-*]\s+(.*)$", raw)
        if m:
            indent = len(m.group(1))
            text = m.group(2)
            elements.append(Element("bullet", (indent, text)))
            i += 1
            continue

        # Blockquote — treat as paragraph with leading "> "
        if stripped.startswith(">"):
            elements.append(Element("para", stripped[1:].lstrip()))
            i += 1
            continue

        # Blank line → small spacer
        if not stripped:
            elements.append(Element("rule", "blank"))
            i += 1
            continue

        # Default paragraph
        elements.append(Element("para", raw.rstrip()))
        i += 1

    if in_code and code_buf:
        elements.append(Element("code", "\n".join(code_buf)))
    if in_block_math and math_buf:
        elements.append(Element("math_block", "\n".join(math_buf).strip()))
    flush_table()
    return elements


# ---------------------------------------------------------------------------
# Inline parsing — split a paragraph into runs of (text, kind)
# ---------------------------------------------------------------------------

INLINE_TOKEN_RE = re.compile(
    r"(\$[^$\n]+\$)"                # $...$ inline math
    r"|(\*\*[^*]+\*\*)"              # **bold**
    r"|(`[^`]+`)"                    # `code`
)


def split_inline(text: str) -> list[tuple[str, str]]:
    """Return list of (kind, content) for inline tokens.

    Kinds: 'text', 'math', 'bold', 'code'.
    """
    out: list[tuple[str, str]] = []
    pos = 0
    for m in INLINE_TOKEN_RE.finditer(text):
        if m.start() > pos:
            out.append(("text", text[pos:m.start()]))
        token = m.group(0)
        if token.startswith("$"):
            out.append(("math", token[1:-1]))
        elif token.startswith("**"):
            out.append(("bold", token[2:-2]))
        elif token.startswith("`"):
            out.append(("code", token[1:-1]))
        pos = m.end()
    if pos < len(text):
        out.append(("text", text[pos:]))
    return out


# ---------------------------------------------------------------------------
# Style helpers — clean markdown emphasis from already-bold contexts
# ---------------------------------------------------------------------------

def strip_bold_markers(text: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", r"\1", text)


# ---------------------------------------------------------------------------
# PDF layout
# ---------------------------------------------------------------------------

PRIMARY_COLOR = (0.16, 0.32, 0.62)
ACCENT_COLOR = (0.88, 0.45, 0.10)
MUTED_TEXT = (0.32, 0.32, 0.32)
HAIRLINE = (0.78, 0.78, 0.78)
CODE_BG = (0.96, 0.96, 0.93)
TABLE_HEAD_BG = (0.92, 0.94, 0.99)


class PdfWriter:
    PAGE_WIDTH = 595
    PAGE_HEIGHT = 842
    MARGIN_X = 50
    MARGIN_TOP = 64
    MARGIN_BOTTOM = 56

    BODY_SIZE = 10.5
    BODY_LH = 16.5
    SECTION_TOP_PAD = 6
    BULLET_INDENT = 14

    def __init__(self, header: str, *, half_width: bool = False):
        self.doc = fitz.open()
        self.header = header
        self.half_width = half_width
        # In half-width mode, content fills only the left half of the page.
        # The right half is reserved for hand-written notes.
        if half_width:
            self.right_x = self.PAGE_WIDTH / 2 - 8   # small inner gutter
        else:
            self.right_x = self.PAGE_WIDTH - self.MARGIN_X
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
        self._new_page()

    # ---- page chrome ----

    def _new_page(self):
        self.page = self.doc.new_page(width=self.PAGE_WIDTH, height=self.PAGE_HEIGHT)
        for kind, alias in self.font_names.items():
            self.page.insert_font(fontfile=self.font_files[kind], fontname=alias)
        self.page_no += 1
        # running head
        self._draw_runs(self.header, self.MARGIN_X, 30, 9, MUTED_TEXT)
        page_label = f"- {self.page_no} -"
        pl_w = measure(page_label, 9)
        self._draw_runs(
            page_label,
            self.right_x - pl_w,
            30,
            9,
            MUTED_TEXT,
        )
        self.page.draw_line(
            (self.MARGIN_X, 40),
            (self.right_x, 40),
            color=HAIRLINE,
            width=0.5,
        )
        # In half-width mode, draw a faint vertical fold line at the page
        # midpoint so the visual "fold" is obvious when printed.
        if self.half_width:
            mid = self.PAGE_WIDTH / 2
            self.page.draw_line(
                (mid, 24),
                (mid, self.PAGE_HEIGHT - 24),
                color=(0.85, 0.85, 0.85),
                width=0.4,
                dashes="[2 3] 0",
            )
        self.y = self.MARGIN_TOP

    def ensure(self, needed: float):
        if self.y + needed > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self._new_page()

    def vspace(self, h: float):
        self.ensure(h)
        self.y += h

    @property
    def content_width(self) -> float:
        return self.right_x - self.MARGIN_X

    # ---- low-level drawing ----

    def _draw_runs(self, text: str, x: float, y: float, size: float, color, bold: bool = False) -> float:
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

    # ---- inline run-aware wrapping with math images ----

    def _draw_inline_line(
        self,
        runs: list[tuple[str, object]],
        x: float,
        size: float,
        baseline_y: float,
    ):
        """Draw a single composed line with mixed text/math runs.

        runs items:
          ('text', str) | ('bold', str) | ('code', str) | ('math', (png, w_pt, h_pt))
        """
        cur_x = x
        for kind, payload in runs:
            if kind == "math":
                png, w_pt, h_pt = payload
                # Place math image so its vertical center aligns with text x-height
                top = baseline_y - h_pt + 1
                rect = fitz.Rect(cur_x, top, cur_x + w_pt, top + h_pt)
                self.page.insert_image(rect, stream=png)
                cur_x += w_pt + 1
            elif kind == "text":
                cur_x = self._draw_runs(payload, cur_x, baseline_y, size, (0.08, 0.08, 0.12))
            elif kind == "bold":
                cur_x = self._draw_runs(payload, cur_x, baseline_y, size, (0.08, 0.08, 0.12), bold=True)
            elif kind == "code":
                # Subtle inline code: monospaced look via fallback font is acceptable
                cur_x = self._draw_runs(payload, cur_x, baseline_y, size, (0.20, 0.20, 0.45))
        return cur_x

    def _measure_inline_run(self, kind: str, payload, size: float) -> tuple[float, float]:
        """Returns (width_pt, height_pt) of one inline run."""
        if kind == "math":
            _, w_pt, h_pt = payload
            return w_pt + 1, h_pt
        if kind == "text":
            return measure(payload, size, bold=False), size
        if kind == "bold":
            return measure(payload, size, bold=True), size
        if kind == "code":
            return measure(payload, size, bold=False), size
        return 0.0, size

    def _layout_inline(
        self,
        inline_parts: list[tuple[str, str]],
        max_width: float,
        size: float,
    ) -> list[list[tuple[str, object]]]:
        """Wrap inline parts to fit max_width.

        Math tokens are rendered to PNG and converted to point-sized images
        based on a desired math height (~1.4x body size).
        Returns a list of lines; each line is a list of runs ready to draw.
        """
        # Pre-render math
        math_target_h = size * 1.4   # visual size of inline math
        prepared: list[tuple[str, object]] = []
        for kind, content in inline_parts:
            if kind == "math":
                # mathtext fontsize tuned so the resulting PNG height ~= math_target_h
                # We pick mathtext fontsize and then scale based on actual height.
                base_fs = size * 1.4
                png, w_px, h_px = render_math_png(content, base_fs, display=False)
                # Convert from pixel-units (matplotlib uses 100 DPI by default
                # for figure backend; pixel == 1/100 inch == 0.72 pt)
                px_to_pt = 0.72
                w_pt = w_px * px_to_pt
                h_pt = h_px * px_to_pt
                # Scale so height matches math_target_h
                scale = math_target_h / h_pt if h_pt > 0 else 1.0
                w_pt *= scale
                h_pt *= scale
                prepared.append(("math", (png, w_pt, h_pt)))
            elif kind == "text":
                # break the text by spaces and Korean syllables for wrapping
                # We'll do a simpler approach: keep text as one run, but split
                # at whitespace during the wrap loop.
                prepared.append((kind, content))
            else:
                prepared.append((kind, content))

        # Wrap by walking runs and splitting text runs as needed
        lines: list[list[tuple[str, object]]] = [[]]
        cur_w = 0.0

        def push_run(kind, payload):
            nonlocal cur_w
            w, _ = self._measure_inline_run(kind, payload, size)
            if cur_w + w > max_width and lines[-1]:
                lines.append([])
                cur_w = 0.0
            lines[-1].append((kind, payload))
            cur_w += w

        for kind, payload in prepared:
            if kind == "text":
                # Split text into wrappable atoms: words + Korean per-character
                atoms = re.findall(r"\s+|[A-Za-z0-9_'\-.,;:()/!?@#$%&*+=<>\[\]{}|\\^~`\"]+|[^\s]", payload)
                for atom in atoms:
                    if atom == "" or (atom.isspace() and not lines[-1]):
                        continue
                    w = measure(atom, size, bold=False)
                    if cur_w + w > max_width and lines[-1] and atom.strip():
                        lines.append([])
                        cur_w = 0.0
                    # merge consecutive text atoms
                    if lines[-1] and lines[-1][-1][0] == "text":
                        prev_kind, prev_text = lines[-1][-1]
                        lines[-1][-1] = ("text", prev_text + atom)
                    else:
                        lines[-1].append(("text", atom))
                    cur_w += w
            else:
                push_run(kind, payload)
        # Drop leading whitespace-only entries on each line
        for line in lines:
            while line and line[0][0] == "text" and not line[0][1].strip():
                line.pop(0)
        # Drop empty trailing lines
        while lines and not lines[-1]:
            lines.pop()
        return lines

    # ---- block emitters ----

    def write_heading(self, level: int, text: str):
        text = strip_bold_markers(text).strip()
        if not text:
            return
        sizes = {1: 18.0, 2: 14.5, 3: 12.5, 4: 11.5}
        colors = {1: (1, 1, 1), 2: PRIMARY_COLOR, 3: PRIMARY_COLOR, 4: (0.10, 0.10, 0.20)}
        bold = level <= 3
        size = sizes.get(level, 11.0)
        line_h = size * 1.5
        if level == 1:
            self.ensure(line_h + 18)
            band = fitz.Rect(self.MARGIN_X, self.y, self.right_x, self.y + line_h + 14)
            self.page.draw_rect(band, color=PRIMARY_COLOR, fill=PRIMARY_COLOR)
            self._draw_runs(text, self.MARGIN_X + 14, self.y + size + 8, size, (1, 1, 1), bold=True)
            self.y += line_h + 18
            return
        if level == 2:
            # vertical bar accent
            self.vspace(self.SECTION_TOP_PAD)
            self.ensure(line_h + 10)
            bar = fitz.Rect(self.MARGIN_X, self.y + 2, self.MARGIN_X + 4, self.y + line_h - 4)
            self.page.draw_rect(bar, color=PRIMARY_COLOR, fill=PRIMARY_COLOR)
            self._draw_runs(text, self.MARGIN_X + 12, self.y + size + 1, size, PRIMARY_COLOR, bold=True)
            self.y += line_h + 4
            self.page.draw_line(
                (self.MARGIN_X, self.y),
                (self.right_x, self.y),
                color=HAIRLINE,
                width=0.4,
            )
            self.y += 6
            return
        if level == 3:
            self.vspace(4)
            self.ensure(line_h + 4)
            self._draw_runs(text, self.MARGIN_X, self.y + size, size, PRIMARY_COLOR, bold=True)
            self.y += line_h
            return
        # h4
        self.vspace(2)
        self.ensure(line_h + 2)
        self._draw_runs(text, self.MARGIN_X, self.y + size, size, ACCENT_COLOR, bold=True)
        self.y += line_h

    def write_paragraph(self, text: str, indent: float = 0.0, leading: str = ""):
        text = text.rstrip()
        if not text.strip():
            self.vspace(3)
            return
        parts = split_inline(text)
        max_w = self.content_width - indent - measure(leading, self.BODY_SIZE, bold=False) - 2
        lines = self._layout_inline(parts, max_w, self.BODY_SIZE)
        if not lines:
            self.vspace(3)
            return
        for idx, line in enumerate(lines):
            # height = max of run heights
            heights = [self._measure_inline_run(k, p, self.BODY_SIZE)[1] for k, p in line]
            line_h = max(self.BODY_LH, *heights) if heights else self.BODY_LH
            self.ensure(line_h)
            x = self.MARGIN_X + indent
            if idx == 0 and leading:
                x = self._draw_runs(leading, x, self.y + self.BODY_SIZE, self.BODY_SIZE, ACCENT_COLOR, bold=True)
                x += 2
            elif leading:
                # Continuation hangs under the leading marker
                x += measure(leading, self.BODY_SIZE, bold=False) + 2
            self._draw_inline_line(line, x, self.BODY_SIZE, self.y + self.BODY_SIZE)
            self.y += self.BODY_LH

    def write_bullet(self, indent_chars: int, text: str):
        depth = indent_chars // 2
        indent = self.BULLET_INDENT + depth * 12
        bullet = "•" if depth == 0 else "·"
        self.write_paragraph(text, indent=indent, leading=bullet + "  ")

    def write_code(self, code: str):
        size = 9.5
        lh = 13.5
        pad = 8
        lines = code.split("\n")
        max_w = self.content_width - 2 * pad - 4
        wrapped: list[str] = []
        for ln in lines:
            if measure(ln, size) <= max_w:
                wrapped.append(ln)
            else:
                # Hard wrap by character
                cur = ""
                for ch in ln:
                    if measure(cur + ch, size) > max_w:
                        wrapped.append(cur)
                        cur = ch
                    else:
                        cur += ch
                if cur:
                    wrapped.append(cur)
        h = lh * len(wrapped) + 2 * pad
        self.ensure(h + 6)
        rect = fitz.Rect(
            self.MARGIN_X,
            self.y,
            self.right_x,
            self.y + h,
        )
        self.page.draw_rect(rect, color=CODE_BG, fill=CODE_BG)
        stripe = fitz.Rect(rect.x0, rect.y0, rect.x0 + 3, rect.y1)
        self.page.draw_rect(stripe, color=PRIMARY_COLOR, fill=PRIMARY_COLOR)
        yy = self.y + pad + size
        for ln in wrapped:
            self._draw_runs(ln, self.MARGIN_X + pad + 4, yy, size, (0.18, 0.18, 0.35))
            yy += lh
        self.y += h + 6

    def write_math_block(self, latex: str):
        # Render block math larger than inline
        base_fs = self.BODY_SIZE * 1.8
        png, w_px, h_px = render_math_png(latex, base_fs, display=True)
        px_to_pt = 0.72
        w_pt = w_px * px_to_pt
        h_pt = h_px * px_to_pt
        # cap width to content area and scale proportionally
        max_w = self.content_width - 16
        if w_pt > max_w:
            scale = max_w / w_pt
            w_pt *= scale
            h_pt *= scale
        self.ensure(h_pt + 6)
        x = self.MARGIN_X + (self.content_width - w_pt) / 2
        rect = fitz.Rect(x, self.y, x + w_pt, self.y + h_pt)
        self.page.insert_image(rect, stream=png)
        self.y += h_pt + 6

    def write_table(self, rows: list[list[str]]):
        if not rows:
            return
        n_cols = max(len(r) for r in rows)
        # Normalize widths
        for r in rows:
            while len(r) < n_cols:
                r.append("")
        cell_padding = 5
        body_size = 9.5
        # Compute column widths proportional to content length, with min/max
        max_table_w = self.content_width
        weights = [1.0] * n_cols
        for r in rows:
            for j, cell in enumerate(r):
                weights[j] = max(weights[j], min(measure(strip_bold_markers(cell), body_size, bold=False) + 12, 220))
        total = sum(weights)
        col_widths = [w / total * max_table_w for w in weights]
        # Pre-layout cells
        line_h = body_size * 1.45
        prepared_rows: list[tuple[list[list[list[tuple[str, object]]]], float]] = []
        for ri, row in enumerate(rows):
            cell_layouts: list[list[list[tuple[str, object]]]] = []
            row_h = 0.0
            for j, raw_cell in enumerate(row):
                inner_w = col_widths[j] - 2 * cell_padding
                parts = split_inline(raw_cell)
                lines = self._layout_inline(parts, inner_w, body_size)
                cell_layouts.append(lines)
                row_h = max(row_h, max(1, len(lines)) * line_h)
            row_h += 2 * cell_padding
            prepared_rows.append((cell_layouts, row_h))

        # Render
        for ri, (cell_layouts, row_h) in enumerate(prepared_rows):
            self.ensure(row_h + 2)
            x = self.MARGIN_X
            y0 = self.y
            row_rect = fitz.Rect(x, y0, x + sum(col_widths), y0 + row_h)
            if ri == 0:
                self.page.draw_rect(row_rect, color=TABLE_HEAD_BG, fill=TABLE_HEAD_BG)
            self.page.draw_rect(row_rect, color=HAIRLINE, width=0.4)
            cx = x
            for j, lines in enumerate(cell_layouts):
                cell_w = col_widths[j]
                # vertical separator
                if j > 0:
                    self.page.draw_line(
                        (cx, y0),
                        (cx, y0 + row_h),
                        color=HAIRLINE,
                        width=0.4,
                    )
                yy = y0 + cell_padding + body_size
                for line in lines:
                    self._draw_inline_line(line, cx + cell_padding, body_size, yy)
                    yy += line_h
                cx += cell_w
            self.y += row_h

    # ---- file output ----

    def save(self, path: Path):
        self.doc.save(path, deflate=True)
        self.doc.close()


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def render_md_file(pdf: PdfWriter, label: str, md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    elements = parse_markdown(text)
    # Insert a section header for the file
    pdf.vspace(4)
    pdf.write_heading(2, label)
    pdf.vspace(2)
    for el in elements:
        if el.kind == "h1":
            # demote — we already have a section header
            pdf.write_heading(3, el.content)
        elif el.kind == "h2":
            pdf.write_heading(3, el.content)
        elif el.kind == "h3":
            pdf.write_heading(4, el.content)
        elif el.kind == "h4":
            pdf.write_heading(4, el.content)
        elif el.kind == "para":
            pdf.write_paragraph(el.content)
        elif el.kind == "bullet":
            indent, t = el.content
            pdf.write_bullet(indent, t)
        elif el.kind == "code":
            pdf.write_code(el.content)
        elif el.kind == "math_block":
            pdf.write_math_block(el.content)
        elif el.kind == "table":
            pdf.write_table(el.content)
        elif el.kind == "rule":
            if el.content == "blank":
                pdf.vspace(3)
            else:
                pdf.vspace(4)
                pdf.page.draw_line(
                    (pdf.MARGIN_X, pdf.y),
                    (pdf.right_x, pdf.y),
                    color=HAIRLINE,
                    width=0.4,
                )
                pdf.vspace(6)


def build_pdf(out_path: Path, *, half_width: bool = False, subtitle: str | None = None):
    pdf = PdfWriter("2차시험 치팅페이어", half_width=half_width)
    pdf.write_heading(1, "2차시험 치팅페이어")
    pdf.write_paragraph(
        subtitle
        or "시험 직전 빠른 복습용. 문제 prompt와 답안을 이어 붙였습니다."
    )
    pdf.vspace(4)

    for label, md_path in SOURCE_FILES:
        if not md_path.exists():
            continue
        render_md_file(pdf, label, md_path)

    pdf.save(out_path)
    print(f"Wrote {out_path}")


def main():
    # Standard full-width cheat sheet
    build_pdf(OUTPUT_PDF, half_width=False)
    # Folded (half-width) variant — left side prints, right side is blank
    # for hand-written notes when the paper is folded along the dashed line.
    build_pdf(
        OUTPUT_PDF_HALF,
        half_width=True,
        subtitle="왼쪽 단에만 내용이 인쇄됩니다. 오른쪽은 필기/메모용 공간.",
    )


if __name__ == "__main__":
    main()
