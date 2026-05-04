from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "문제은행"
FONTS_DIR = Path(__file__).resolve().parent / "fonts"
KOREAN_FONT_FILE = FONTS_DIR / "NanumGothic.ttf"
KOREAN_BOLD_FONT_FILE = FONTS_DIR / "NanumGothicBold.ttf"
FALLBACK_FONT_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FALLBACK_BOLD_FONT_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

CONFIRMED_FILES = [
    BANK / "260406-260409.md",
    BANK / "260410-260421.md",
    BANK / "260427-260504.md",
]

EXPECTED_FILES = [
    BANK / "260406-260409(예상).md",
    BANK / "260406-260409(예측_codex).md",
    BANK / "260410-260421(예상).md",
    BANK / "260410-260421(예측_codex).md",
    BANK / "260427-260504(예측).md",
    BANK / "260427-260504(예측_codex).md",
]

SECTION_TITLES = {
    "260406-260409": "1부. 인공지능 기초 (260406~260409 / 장병탁 교수님)",
    "260410-260421": "2부. 딥러닝 기초 (260410~260421 / 윤성로 교수님)",
    "260427-260504": "3부. 자연어처리 (260427~260504 / 황승원 교수님)",
}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

PROBLEM_HEADER_RE = re.compile(
    r"^\s*##\s+(?:예상\s*문제|예측\s*문제|예측문제|예상문제|문제)?\s*"
    r"(?P<num>[0-9]+)\.[ \t]*(?P<title>.*)$"
)
QSTYLE_HEADER_RE = re.compile(
    r"^\s*###\s+Q\s*(?P<num>\d+)\.?\s*(?P<title>.*)$"
)
ANSWER_MARKER_RE = re.compile(
    r"^\s*(?:#{1,6}\s*(?:정답|답안|예상\s*정답)\s*$"
    r"|>\s*\*\*(?:모범\s*답안|예상\s*답안|답안)\*\*\s*$)"
)
GRADING_HEADER_RE = re.compile(r"^\s*채점\s*포인트")

META_HEADER_RE = re.compile(
    r"^\s*#{2,4}\s*(?:출제\s*가능성이?\s*높은\s*이유|"
    r"출제\s*확률\s*근거|"
    r"최종\s*우선순위|"
    r"한\s*페이지\s*핵심\s*정리|"
    r"분석\s*개요|"
    r"채점\s*기준|"
    r"기존\s*문제\s*스타일\s*분석|"
    r"세션별\s*커버\s*현황|"
    r"문제별\s*세션\s*매핑)"
)
RUBRIC_LIST_RE = re.compile(r"^\s*[`\s]*●")


def normalize_lines(text: str) -> list[str]:
    text = text.replace("\r\n", "\n")
    return text.split("\n")


@dataclass
class Problem:
    section: str
    file_label: str
    number: str
    title: str
    body_lines: list[str] = field(default_factory=list)
    answer_lines: list[str] = field(default_factory=list)


def trim_expected(text: str) -> str:
    """For prediction/expected files, drop analysis preamble."""
    starts = [
        "# 예상 문제지",
        "# 예측 문제지",
        "# 4. 고확률 예측 문제",
        "# 고확률 예측 문제",
        "## 예측 문제 1.",
        "## 예상문제 1.",
        "## 예측문제 1.",
    ]
    earliest = None
    for marker in starts:
        idx = text.find(marker)
        if idx != -1 and (earliest is None or idx < earliest):
            earliest = idx
    if earliest is not None:
        return text[earliest:]
    return text


def parse_problems(path: Path, section_key: str, file_label: str) -> list[Problem]:
    raw = path.read_text(encoding="utf-8")
    if "(예상)" in path.name or "(예측" in path.name:
        raw = trim_expected(raw)

    problems: list[Problem] = []
    cur: Problem | None = None
    in_answer = False

    for line in normalize_lines(raw):
        m = PROBLEM_HEADER_RE.match(line) or QSTYLE_HEADER_RE.match(line)
        if m:
            if cur is not None:
                problems.append(cur)
            num = m.group("num")
            title = m.group("title").strip()
            title = re.sub(r"\s*\(.*?(?:예상|예측).*?\)\s*", " ", title).strip()
            title = re.sub(r"\s+", " ", title)
            cur = Problem(
                section=section_key,
                file_label=file_label,
                number=num,
                title=title,
            )
            in_answer = False
            continue
        if cur is None:
            continue
        if ANSWER_MARKER_RE.match(line):
            in_answer = True
            continue
        if line.strip().startswith("---"):
            # divider — close out
            in_answer = False
            problems.append(cur)
            cur = None
            continue
        if GRADING_HEADER_RE.match(line):
            in_answer = True
            cur.answer_lines.append("")
            cur.answer_lines.append("[채점 포인트]")
            continue
        if META_HEADER_RE.match(line):
            # Trailing analysis/meta section — close out the problem so that
            # rationale/forecast prose does not bleed into the answer.
            problems.append(cur)
            cur = None
            in_answer = False
            continue
        if in_answer:
            cur.answer_lines.append(line)
        else:
            cur.body_lines.append(line)

    if cur is not None:
        problems.append(cur)

    # Files that put question and answer in two separate `### Q#` lists must
    # be merged so each Q# appears only once.
    if path.name in {
        "260410-260421.md",
        "260410-260421(예상).md",
        "260410-260421(예측_codex).md",
    }:
        problems = merge_separate_answer_sheet(problems)

    # Filter out empty placeholders (e.g., entries created from spurious headers)
    cleaned: list[Problem] = []
    for p in problems:
        body_text = "\n".join(p.body_lines).strip()
        ans_text = "\n".join(p.answer_lines).strip()
        if not body_text and not ans_text:
            continue
        cleaned.append(p)
    return cleaned


def merge_separate_answer_sheet(problems: list[Problem]) -> list[Problem]:
    """260410-260421.md repeats Q1..Q12 once for questions, once for answers.

    Strategy: keep the body from the first occurrence (= the question text);
    the second occurrence has the SAME question repeated above the answer,
    so we drop its body and only keep its answer_lines.
    """
    by_num: dict[str, Problem] = {}
    order: list[str] = []
    for p in problems:
        if p.number not in by_num:
            by_num[p.number] = Problem(
                section=p.section,
                file_label=p.file_label,
                number=p.number,
                title=p.title,
                body_lines=list(p.body_lines),
                answer_lines=list(p.answer_lines),
            )
            order.append(p.number)
            continue
        target = by_num[p.number]
        if not target.title and p.title:
            target.title = p.title
        # body lines from the duplicate are the repeated question — drop them.
        if p.answer_lines:
            target.answer_lines.extend(p.answer_lines)
    return [by_num[n] for n in order]


# ---------------------------------------------------------------------------
# Cleanup helpers
# ---------------------------------------------------------------------------

# Substitutions for glyphs neither NanumGothic nor DejaVu Sans supports
# (multi-font fallback handles Greek/math symbols at render time).
SYMBOL_REPLACE = {
    # Mathematical italic letters (U+1D400 block) — not in either font
    "𝑓": "f",
    "𝑔": "g",
    "ℎ": "h",
    "𝑛": "n",
    "𝑥": "x",
    "𝑦": "y",
    # Korean closing quote U+02EE → ASCII double quote
    "ˮ": '"',
    "ʼ": "'",
    # Hyphens
    "−": "-",
    "–": "-",
}


def strip_md(line: str) -> str:
    line = line.rstrip()
    line = re.sub(r"^#{1,6}\s*", "", line)
    line = re.sub(r"^\s*>\s?", "", line)
    line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
    line = re.sub(r"`([^`]*)`", r"\1", line)
    line = line.replace("<br>", " ")
    for src, dst in SYMBOL_REPLACE.items():
        line = line.replace(src, dst)
    # collapse standalone code-fence markers ("```" on their own line)
    if line.strip() in {"```", "``", "`"}:
        return ""
    return line.rstrip()


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
    """Check if a font actually renders a glyph for the character."""
    try:
        return bool(font.has_glyph(ord(ch)))
    except Exception:
        # fallback to width heuristic
        return font.text_length(ch, fontsize=10) > 0.5


def runs_for_text(text: str, bold: bool) -> list[tuple[str, str]]:
    """Split text into (run_text, font_kind) pairs.

    font_kind is one of "body" / "bold" / "fallback" / "fallback_bold".
    Each run holds consecutive characters that share the same font.
    """
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
            cur_text = []
            cur_kind = None

    for ch in text:
        if ch == " " or ch == "\t" or has_glyph(primary_font, ch):
            kind = primary
        elif has_glyph(fallback_font, ch):
            kind = fallback
        else:
            # neither font has it — emit through primary anyway (will show as a
            # blank box, but we did our best)
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
    """Measure visual width of text using the same multi-font logic as drawing."""
    total = 0.0
    for piece, kind in runs_for_text(text, bold):
        total += get_font(kind).text_length(piece, fontsize=fontsize)
    return total


def text_width(text: str, fontsize: float, bold: bool = False) -> float:
    return measure(text, fontsize, bold)


def wrap_visual(text: str, max_width: float, fontsize: float) -> list[str]:
    """Width-aware wrapper using NanumGothic metrics."""
    leading_match = re.match(r"^(\s*)", text)
    leading = leading_match.group(1) if leading_match else ""
    body = text[len(leading):]

    if text_width(text, fontsize) <= max_width:
        return [text]

    out: list[str] = []
    cur = leading
    cur_w = text_width(leading, fontsize)
    tokens = re.findall(r"\S+\s*|\s+", body)
    for tok in tokens:
        tw = text_width(tok, fontsize)
        if cur_w + tw <= max_width or not cur.strip():
            cur += tok
            cur_w += tw
            continue
        out.append(cur.rstrip())
        cur = leading + tok.lstrip()
        cur_w = text_width(cur, fontsize)
        while text_width(cur, fontsize) > max_width:
            cut_chars: list[str] = []
            w = text_width(leading, fontsize)
            for ch in cur[len(leading):]:
                cw = text_width(ch, fontsize)
                if w + cw > max_width:
                    break
                cut_chars.append(ch)
                w += cw
            if not cut_chars:
                cut_chars.append(cur[len(leading)] if len(cur) > len(leading) else "")
            piece = leading + "".join(cut_chars)
            cur_remaining = cur[len(piece):]
            out.append(piece.rstrip())
            cur = leading + cur_remaining.lstrip()
            cur_w = text_width(cur, fontsize)
    if cur.strip():
        out.append(cur.rstrip())
    return out


def clean_block(lines: list[str]) -> list[str]:
    """Drop trailing empty lines, stray quote markers, and 1-char garbage."""
    out: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        # standalone quote markers like ">" or "> " add no info
        if stripped == ">" or stripped == ">>":
            continue
        # stray single-letter trailing artifacts (e.g., a literal "s" on its
        # own line at the end of a file) — skip when 1-character non-Korean.
        if len(stripped) == 1 and stripped.isascii() and stripped.isalpha():
            continue
        out.append(raw)
    while out and not out[-1].strip():
        out.pop()
    while out and not out[0].strip():
        out.pop(0)
    return out


# ---------------------------------------------------------------------------
# Markdown emission
# ---------------------------------------------------------------------------

def render_question_md(problems_by_section: dict[str, list[Problem]], title: str) -> str:
    out: list[str] = []
    out.append(f"# {title}")
    out.append("")
    out.append("이름: ____________________    수험번호: ____________________    날짜: __________")
    out.append("")
    out.append("응시 안내")
    out.append("")
    out.append("- 모든 답안은 각 문제 아래의 [답안 작성 공간]에 작성하시오.")
    out.append("- 풀이 과정과 핵심 키워드를 함께 서술하면 가점이 부여될 수 있다.")
    out.append("")
    out.append("---")

    counter = 1
    for section_key, problem_list in problems_by_section.items():
        out.append("")
        out.append(f"## {SECTION_TITLES.get(section_key, section_key)}")
        out.append("")
        for p in problem_list:
            title_line = p.title or ""
            out.append(f"### 문제 {counter}. {title_line}".rstrip())
            out.append("")
            for line in clean_block(p.body_lines):
                out.append(line)
            out.append("")
            out.append("[답안 작성 공간]")
            for _ in range(14):
                out.append("_" * 78)
            out.append("")
            counter += 1
        out.append("---")
    return "\n".join(out).rstrip() + "\n"


def render_answer_md(problems_by_section: dict[str, list[Problem]], title: str) -> str:
    out: list[str] = []
    out.append(f"# {title}")
    out.append("")
    out.append("---")

    counter = 1
    for section_key, problem_list in problems_by_section.items():
        out.append("")
        out.append(f"## {SECTION_TITLES.get(section_key, section_key)}")
        out.append("")
        for p in problem_list:
            title_line = p.title or ""
            out.append(f"### 문제 {counter}. {title_line}".rstrip())
            out.append("")
            out.append("[정답]")
            out.append("")
            for line in clean_block(p.answer_lines) or ["(정답 누락)"]:
                out.append(line)
            out.append("")
            counter += 1
        out.append("---")
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------------------
# PDF rendering
# ---------------------------------------------------------------------------


PRIMARY_COLOR = (0.16, 0.32, 0.62)   # navy-ish
ACCENT_COLOR = (0.88, 0.45, 0.10)    # warm orange
MUTED_TEXT = (0.32, 0.32, 0.32)
HAIRLINE = (0.78, 0.78, 0.78)
RULE_LINE = (0.85, 0.85, 0.85)
CODE_BG = (0.96, 0.96, 0.93)
ANSWER_BG = (0.985, 0.985, 0.99)


class PdfWriter:
    PAGE_WIDTH = 595        # A4
    PAGE_HEIGHT = 842
    MARGIN_X = 56
    MARGIN_TOP = 70
    MARGIN_BOTTOM = 60

    BODY_SIZE = 11.0
    BODY_LH = 19.0          # vertical step per body line
    PARA_GAP = 6.0          # blank-line spacing
    BULLET_INDENT = 16.0
    SUB_INDENT = 28.0

    def __init__(self, header: str):
        self.doc = fitz.open()
        self.header = header
        # PyMuPDF font registration names per page
        self.font_names = {
            "body": "kbody",
            "bold": "kbold",
            "fallback": "fbody",
            "fallback_bold": "fbold",
        }
        self.font_files = {k: str(_FONT_PATHS[k]) for k in self.font_names}
        self.font = get_font("body")
        self.bold_font = get_font("bold")
        self.page = None
        self.y = 0.0
        self.page_no = 0
        self.new_page()

    # ---------------- page chrome ----------------

    def new_page(self):
        self.page = self.doc.new_page(width=self.PAGE_WIDTH, height=self.PAGE_HEIGHT)
        for kind, alias in self.font_names.items():
            self.page.insert_font(fontfile=self.font_files[kind], fontname=alias)
        self.page_no += 1
        # running head
        self._draw_runs(self.header, self.MARGIN_X, 32, 9, MUTED_TEXT)
        page_label = f"- {self.page_no} -"
        pl_w = measure(page_label, fontsize=9)
        self._draw_runs(page_label, self.PAGE_WIDTH - self.MARGIN_X - pl_w, 32, 9, MUTED_TEXT)
        self.page.draw_line(
            (self.MARGIN_X, 42),
            (self.PAGE_WIDTH - self.MARGIN_X, 42),
            color=HAIRLINE,
            width=0.6,
        )
        self.y = self.MARGIN_TOP

    def ensure(self, needed: float):
        if self.y + needed > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self.new_page()

    def vspace(self, h: float):
        self.ensure(h)
        self.y += h

    # ---------------- low-level text ----------------

    def _draw_runs(self, text: str, x: float, y: float, size: float, color, bold: bool = False):
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

    def _draw_line(self, text: str, x: float, y: float, size: float, color, bold_emulate=False):
        self._draw_runs(text, x, y, size, color, bold=bold_emulate)

    def write_simple(self, text: str, *, size=None, color=(0, 0, 0), bold=False, indent=0.0):
        size = size or self.BODY_SIZE
        line_h = size * 1.6
        self.ensure(line_h)
        self._draw_line(text, self.MARGIN_X + indent, self.y + size, size, color, bold)
        self.y += line_h

    def write_centered(self, text: str, *, size=None, color=(0, 0, 0), bold=False):
        size = size or self.BODY_SIZE
        w = self.font.text_length(text, fontsize=size)
        line_h = size * 1.6
        self.ensure(line_h)
        x = (self.PAGE_WIDTH - w) / 2
        self._draw_line(text, x, self.y + size, size, color, bold)
        self.y += line_h

    # ---------------- structural blocks ----------------

    def cover_title(self, title: str, subtitle: str | None = None):
        # decorative band
        self.ensure(70)
        band = fitz.Rect(
            self.MARGIN_X,
            self.y,
            self.PAGE_WIDTH - self.MARGIN_X,
            self.y + 56,
        )
        self.page.draw_rect(band, color=PRIMARY_COLOR, fill=PRIMARY_COLOR)
        self._draw_line(
            title,
            self.MARGIN_X + 16,
            self.y + 36,
            22,
            (1, 1, 1),
            bold_emulate=True,
        )
        if subtitle:
            self._draw_line(
                subtitle,
                self.MARGIN_X + 16,
                self.y + 50,
                10,
                (0.92, 0.92, 0.96),
            )
        self.y += 64
        self.vspace(4)

    def info_row(self, fields: list[str]):
        size = self.BODY_SIZE
        line_h = size * 1.7
        self.ensure(line_h + 4)
        x = self.MARGIN_X
        usable = self.PAGE_WIDTH - 2 * self.MARGIN_X
        col_w = usable / len(fields)
        for i, label in enumerate(fields):
            cx = self.MARGIN_X + col_w * i
            self._draw_line(
                f"{label}: ",
                cx,
                self.y + size,
                size,
                MUTED_TEXT,
            )
            label_w = self.font.text_length(f"{label}: ", fontsize=size)
            line_y = self.y + size + 2
            self.page.draw_line(
                (cx + label_w, line_y),
                (cx + col_w - 12, line_y),
                color=HAIRLINE,
                width=0.6,
            )
        self.y += line_h + 4

    def section_header(self, text: str):
        self.ensure(40)
        # left rule + heading
        rect = fitz.Rect(
            self.MARGIN_X,
            self.y + 4,
            self.MARGIN_X + 4,
            self.y + 26,
        )
        self.page.draw_rect(rect, color=PRIMARY_COLOR, fill=PRIMARY_COLOR)
        self._draw_line(
            text,
            self.MARGIN_X + 12,
            self.y + 22,
            14.5,
            PRIMARY_COLOR,
            bold_emulate=True,
        )
        self.y += 32
        self.page.draw_line(
            (self.MARGIN_X, self.y),
            (self.PAGE_WIDTH - self.MARGIN_X, self.y),
            color=HAIRLINE,
            width=0.6,
        )
        self.y += 10

    def problem_header(self, num: int, title: str):
        self.ensure(30)
        label = f"문제 {num}."
        lbl_w = self.bold_font.text_length(label, fontsize=12.5)
        self._draw_line(label, self.MARGIN_X, self.y + 13, 12.5, ACCENT_COLOR, bold_emulate=True)
        max_title_w = self.PAGE_WIDTH - 2 * self.MARGIN_X - lbl_w - 10
        wrapped = wrap_visual(title, max_title_w, fontsize=12.5) or [""]
        for i, piece in enumerate(wrapped):
            if i > 0:
                self.y += 18
                self.ensure(20)
            x_off = self.MARGIN_X + lbl_w + 6 if i == 0 else self.MARGIN_X
            self._draw_line(piece, x_off, self.y + 13, 12.5, (0.10, 0.10, 0.18), bold_emulate=True)
        self.y += 22

    def callout(self, label: str, color=PRIMARY_COLOR):
        size = 10.5
        line_h = size * 1.6
        self.ensure(line_h + 4)
        # filled left bar
        bar = fitz.Rect(self.MARGIN_X, self.y + 2, self.MARGIN_X + 3, self.y + line_h - 2)
        self.page.draw_rect(bar, color=color, fill=color)
        self._draw_line(label, self.MARGIN_X + 10, self.y + size + 1, size, color, bold_emulate=True)
        self.y += line_h + 2

    # ---------------- paragraph rendering ----------------

    def _bullet_indent(self, line: str) -> tuple[float, str]:
        s = line.lstrip()
        if s.startswith("● "):
            return self.BULLET_INDENT, "● " + s[2:]
        if s.startswith("- "):
            return self.BULLET_INDENT, "• " + s[2:]
        leading_ws = len(line) - len(s)
        if leading_ws >= 3:
            return self.SUB_INDENT, s
        return 0.0, line

    def write_paragraph(self, raw: str):
        line = strip_md(raw)
        if not line.strip():
            self.vspace(self.PARA_GAP)
            return
        indent, text = self._bullet_indent(line)
        max_width = self.PAGE_WIDTH - 2 * self.MARGIN_X - indent - 6
        wrapped = wrap_visual(text, max_width, fontsize=self.BODY_SIZE)
        if not wrapped:
            wrapped = [""]
        for i, piece in enumerate(wrapped):
            extra_indent = indent
            if i > 0 and indent > 0:
                # hanging indent: continuation lines align after the bullet
                extra_indent = indent + 12
            self.ensure(self.BODY_LH)
            self._draw_line(
                piece,
                self.MARGIN_X + extra_indent,
                self.y + self.BODY_SIZE,
                self.BODY_SIZE,
                (0.08, 0.08, 0.12),
            )
            self.y += self.BODY_LH

    def write_code_block(self, lines: list[str]):
        if not lines:
            return
        size = 10.0
        lh = 15.0
        pad = 9
        # symbol-clean each code line (math italic chars must be normalised)
        cleaned: list[str] = []
        for raw in lines:
            ln = raw
            for src, dst in SYMBOL_REPLACE.items():
                ln = ln.replace(src, dst)
            cleaned.append(ln)
        # wrap each line so it fits within the code-block width
        max_w = self.PAGE_WIDTH - 2 * self.MARGIN_X - 2 * pad - 6
        wrapped: list[str] = []
        for ln in cleaned:
            pieces = wrap_visual(ln, max_w, fontsize=size)
            wrapped.extend(pieces or [""])
        h = lh * len(wrapped) + pad * 2
        self.ensure(h + 4)
        rect = fitz.Rect(
            self.MARGIN_X,
            self.y,
            self.PAGE_WIDTH - self.MARGIN_X,
            self.y + h,
        )
        self.page.draw_rect(rect, color=CODE_BG, fill=CODE_BG)
        stripe = fitz.Rect(rect.x0, rect.y0, rect.x0 + 3, rect.y1)
        self.page.draw_rect(stripe, color=PRIMARY_COLOR, fill=PRIMARY_COLOR)
        yy = self.y + pad + size
        for ln in wrapped:
            self._draw_line(
                ln,
                self.MARGIN_X + pad + 6,
                yy,
                size,
                (0.18, 0.18, 0.30),
            )
            yy += lh
        self.y += h + 6

    def answer_box(self, lines: int = 12, min_lines: int = 8):
        """Render an answer box. If the full target doesn't fit on the current
        page, but at least min_lines do, shrink to fit; otherwise spill onto
        the next page with the full target size.
        """
        line_h = 22
        target_h = lines * line_h + 22 + 14  # box height + bottom margin
        remaining = self.PAGE_HEIGHT - self.MARGIN_BOTTOM - self.y
        actual_lines = lines
        if remaining < target_h:
            fit_lines = int((remaining - 22 - 14) / line_h)
            if fit_lines >= min_lines:
                actual_lines = fit_lines
            else:
                self.new_page()
                remaining = self.PAGE_HEIGHT - self.MARGIN_BOTTOM - self.y
                fit_lines = int((remaining - 22 - 14) / line_h)
                actual_lines = max(min_lines, min(lines, fit_lines))
        h = actual_lines * line_h + 22
        rect = fitz.Rect(
            self.MARGIN_X,
            self.y,
            self.PAGE_WIDTH - self.MARGIN_X,
            self.y + h,
        )
        self.page.draw_rect(rect, color=HAIRLINE, fill=ANSWER_BG, width=0.8)
        tab = fitz.Rect(rect.x0, rect.y0, rect.x0 + 60, rect.y0 + 18)
        self.page.draw_rect(tab, color=PRIMARY_COLOR, fill=PRIMARY_COLOR)
        self._draw_line("답안", rect.x0 + 12, rect.y0 + 13, 9.5, (1, 1, 1), bold_emulate=True)
        yy = rect.y0 + 22 + line_h * 0.4
        for _ in range(actual_lines):
            self.page.draw_line(
                (rect.x0 + 14, yy),
                (rect.x1 - 14, yy),
                color=(0.86, 0.88, 0.92),
                width=0.5,
            )
            yy += line_h
        self.y += h + 14

    def save(self, path: Path):
        self.doc.save(path, deflate=True)
        self.doc.close()


def emit_problem_body(pdf: PdfWriter, body_lines: list[str]):
    """Render the question body, treating ```...``` as code blocks."""
    in_code = False
    code_buf: list[str] = []
    for raw in body_lines:
        stripped_raw = raw.strip()
        if stripped_raw.startswith("```"):
            if in_code:
                pdf.write_code_block(code_buf)
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(raw.rstrip())
            continue
        pdf.write_paragraph(raw)
    if in_code and code_buf:
        pdf.write_code_block(code_buf)


def render_question_pdf(
    problems_by_section: dict[str, list[Problem]],
    out_pdf: Path,
    title: str,
):
    pdf = PdfWriter(title)
    pdf.cover_title(title, "AI Expert · 시험 문제지")
    pdf.vspace(2)
    pdf.info_row(["이름", "수험번호", "날짜"])
    pdf.vspace(8)
    pdf.callout("응시 안내")
    for line in [
        "모든 답안은 각 문제 아래 답안 박스 안에 작성하시오.",
        "풀이 과정과 핵심 키워드를 함께 서술하면 가점될 수 있다.",
        "답안 박스의 줄 수는 가이드일 뿐이며 박스를 넘겨 작성해도 무방하다.",
    ]:
        pdf.write_paragraph(f"- {line}")
    pdf.vspace(8)

    counter = 1
    first_section = True
    for section_key, problem_list in problems_by_section.items():
        if not first_section:
            pdf.vspace(8)
        first_section = False
        pdf.section_header(SECTION_TITLES.get(section_key, section_key))
        for p in problem_list:
            pdf.problem_header(counter, p.title or "")
            emit_problem_body(pdf, clean_block(p.body_lines))
            pdf.vspace(2)
            pdf.answer_box(lines=12)
            counter += 1
    pdf.save(out_pdf)


def render_answer_pdf(
    problems_by_section: dict[str, list[Problem]],
    out_pdf: Path,
    title: str,
):
    pdf = PdfWriter(title)
    pdf.cover_title(title, "AI Expert · 모범 답안")
    pdf.vspace(8)

    counter = 1
    first_section = True
    for section_key, problem_list in problems_by_section.items():
        if not first_section:
            pdf.vspace(8)
        first_section = False
        pdf.section_header(SECTION_TITLES.get(section_key, section_key))
        for p in problem_list:
            pdf.problem_header(counter, p.title or "")
            pdf.callout("정답", color=ACCENT_COLOR)
            answer_lines = clean_block(p.answer_lines)
            if not answer_lines:
                pdf.write_paragraph("(정답 누락)")
            else:
                emit_problem_body(pdf, answer_lines)
            pdf.vspace(8)
            counter += 1
    pdf.save(out_pdf)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def gather(files: list[Path]) -> dict[str, list[Problem]]:
    sections: dict[str, list[Problem]] = {}
    for path in files:
        section_key = path.stem.split("(")[0]
        problems = parse_problems(path, section_key, path.stem)
        sections.setdefault(section_key, []).extend(problems)
    return sections


def main():
    confirmed = gather(CONFIRMED_FILES)
    expected = gather(EXPECTED_FILES)

    outputs = [
        ("기출확정문제", confirmed, "question"),
        ("기출확정문제_답안", confirmed, "answer"),
        ("기출예상문제", expected, "question"),
        ("기출예상문제_답안", expected, "answer"),
    ]

    for name, problems_by_section, mode in outputs:
        md_path = BANK / f"{name}.md"
        pdf_path = BANK / f"{name}.pdf"
        if mode == "question":
            md_path.write_text(
                render_question_md(problems_by_section, name), encoding="utf-8"
            )
            render_question_pdf(problems_by_section, pdf_path, name)
        else:
            md_path.write_text(
                render_answer_md(problems_by_section, name), encoding="utf-8"
            )
            render_answer_pdf(problems_by_section, pdf_path, name)
        print(pdf_path)


if __name__ == "__main__":
    main()
