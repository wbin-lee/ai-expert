#!/usr/bin/env python3
"""Rebuild 치팅페이퍼.pdf in the original ReportLab style, inserting Sampling Steps.

Preserves layout conventions from the existing PDF:
  - A4, left column only (~half width), right column empty note
  - Body 10.5pt black, 정답 label 11pt #cc0000 bold
  - Headers #0f3460 bold, professor title larger
  - NanumGothic (Malgun not available on this machine; metrics match original)
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, black, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
SRC_PDF = ROOT / "치팅페이퍼.pdf"
OUT_PDF = ROOT / "치팅페이퍼.pdf"
FONT_REG = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"

# layout (measured from original)
PAGE_W, PAGE_H = A4  # 595.27 x 841.89
LEFT = 34.35
COL_W = 250.0  # left column content width (~ to x=284)
RIGHT_EDGE = LEFT + COL_W
TOP = PAGE_H - 44.0
BOTTOM = 40.0
LEADING = 14.0
BODY_SIZE = 10.5
ANS_SIZE = 11.0
HDR_SIZE = 10.5
PROF_SIZE = 12.0
FOOT_SIZE = 7.0

C_BODY = HexColor("#000000")
C_Q = HexColor("#111111")
C_HDR = HexColor("#0f3460")
C_ANS = HexColor("#cc0000")
C_MUTED = HexColor("#444444")
C_RIGHT = HexColor("#bbbbbb")
C_PROF = HexColor("#0f3460")

pdfmetrics.registerFont(TTFont("KR", FONT_REG))
pdfmetrics.registerFont(TTFont("KR-B", FONT_BOLD))


def extract_text_blocks() -> str:
    """Extract full text from existing PDF, strip page chrome."""
    import fitz

    doc = fitz.open(SRC_PDF)
    chunks = []
    for p in doc:
        t = p.get_text()
        # drop page chrome lines
        lines = []
        for ln in t.splitlines():
            s = ln.strip()
            if not s:
                lines.append("")
                continue
            if re.match(r"^—\s*\d+\s*—$", s):
                continue
            if s.startswith("오른쪽 단"):
                continue
            lines.append(ln.rstrip())
        chunks.append("\n".join(lines))
    doc.close()
    # join pages; clean double blanks
    text = "\n".join(chunks)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def reflow_join(text: str) -> str:
    """Join soft line wraps within paragraphs while keeping structural breaks."""
    # Keep structural markers on their own sense of blocks
    lines = text.split("\n")
    out: list[str] = []
    buf = ""

    def flush():
        nonlocal buf
        if buf:
            out.append(buf.strip())
            buf = ""

    for ln in lines:
        s = ln.strip()
        if not s:
            flush()
            out.append("")
            continue
        # structural starts → new block
        if (
            s.startswith("■ ")
            or s.startswith("과목:")
            or s.startswith("[확정]")
            or s.startswith("[예상]")
            or s == "정답"
            or s.startswith("구성:")
            or s.startswith("예상 포함:")
            or s.startswith("→ ")
            or s.startswith("※ ")
            or s.startswith("시험 직전")
            or s.startswith("근거:")
            or s.startswith("Samsung AI")
            or s == "치팅페이퍼"
            or s.startswith("확정문제 전부")
            or s.startswith("정답 라벨")
            or s.startswith("• 곽:")
            or s.startswith("• 권:")
            or s.startswith("• 문:")
            or s.startswith("• 박:")
            or s.startswith("• 서:")
            or s.startswith("• 윤:")
            or s.startswith("• 주:")
            or s.startswith("• 최:")
            or s.startswith("• 홍:")
        ):
            flush()
            out.append(s)
            continue
        # bullet / numbered answer lines
        if s.startswith("• ") or re.match(r"^\d+\.\s", s) or s.startswith("(a)") or s.startswith("(b)") or s.startswith("(c)"):
            flush()
            buf = s
            continue
        # continuation of previous line
        if buf:
            # avoid double space; join with space unless previous ends with open paren etc.
            if buf.endswith(("-", "—")):
                buf = buf[:-1] + s
            else:
                buf = buf + " " + s
        else:
            buf = s
    flush()
    # second pass: merge short continuations that aren't structural
    return "\n".join(out)


def insert_sampling_steps(text: str) -> str:
    """Insert Sampling Steps expected problem after CFG block; update TOC lines."""
    # update cover summary
    text = text.replace("권(CFG)", "권(CFG·Steps)")
    text = text.replace(
        "• 권: 픽셀=연산·VRAM 폭증 · Cond=조건가이드 ·\nLDM=VAE잠재 디퓨전 · CFG7.5\n(낮=자유/높=과집착)",
        "• 권: 픽셀=연산·VRAM 폭증 · Cond=조건가이드 · LDM=VAE잠재 디퓨전 · CFG7.5(낮=자유/높=과집착) · Steps(적=블러/20~30/과다=포화)",
    )
    # also single-line form if already joined
    text = text.replace(
        "• 권: 픽셀=연산·VRAM 폭증 · Cond=조건가이드 · LDM=VAE잠재 디퓨전 · CFG7.5 (낮=자유/높=과집착)",
        "• 권: 픽셀=연산·VRAM 폭증 · Cond=조건가이드 · LDM=VAE잠재 디퓨전 · CFG7.5(낮=자유/높=과집착) · Steps(적=블러/20~30/과다=포화)",
    )

    sampling = """
[예상] 예상문제 2 — Sampling Steps (디노이징 타임스텝)
디퓨전 모델의 추론(생성) 시 sampling steps(디노이징 타임스텝 수)를 조절하면 생성 결과에 어떤 변화가 나타나는지 설명하시오. 스텝을 줄일 때 / 늘릴 때 / 과도하게 늘릴 때 각각의 현상을 서술하시오.
정답
• Sampling steps: 가우시안 노이즈에서 시작해 깨끗한 이미지로 복원하는 디노이징 반복 횟수. 이론상 1000 스텝, 실무에서는 20~50 정도(권장 20~30).
• 줄임(5~10): 디노이징이 불완전하게 끝난다. 블러·미완성 이미지, 디테일 부족.
• 늘림(20~30): 구조(윤곽)가 먼저 잡히고 이후 디테일·질감이 복원된다. 인간 눈으로 충분히 선명한 품질.
• 과다(50+): 품질이 조금 더 좋아질 수 있으나 포화(saturation)에 도달 — 20~30 이후 눈에 띄는 차이가 거의 없고 시간만 선형 증가한다.
• 트레이드오프: 생성 시간은 스텝 수에 비례(선형)하지만, 품질 향상은 한계가 있어 비선형. 권장 범위 대략 20~50(실무 20~30).
• 연동: 사용하는 샘플러(DDIM은 적은 스텝, DPM은 많은 스텝)에 따라 최적 스텝 수가 달라지므로, 샘플러를 바꾸면 스텝도 다시 조절해야 한다.
""".strip()

    # insert before 문태섭
    marker = "■ 문태섭 교수님"
    if marker not in text:
        raise SystemExit("문태섭 marker not found")
    if "예상문제 2 — Sampling Steps" in text:
        print("Sampling Steps already present; skip insert")
        return text
    text = text.replace(marker, sampling + "\n" + marker)
    return text


class CheatDoc:
    def __init__(self, path: Path):
        self.c = canvas.Canvas(str(path), pagesize=A4)
        self.c.setTitle("치팅페이퍼 — Samsung AI Expert 2026 4차 시험")
        self.c.setAuthor("정리본")
        self.y = TOP
        self.page = 1
        self._draw_chrome()

    def _draw_chrome(self):
        self.c.setFont("KR", FOOT_SIZE)
        self.c.setFillColor(C_MUTED)
        self.c.drawCentredString(LEFT + COL_W / 2, 18, f"— {self.page} —")
        # right half note
        self.c.setFillColor(C_RIGHT)
        self.c.setFont("KR", 6.5)
        mid = PAGE_W / 2
        self.c.drawString(mid + 18, PAGE_H / 2, "오른쪽 단 (비움 / 필기 여백)")
        # faint fold line
        self.c.setStrokeColor(HexColor("#dddddd"))
        self.c.setDash(2, 3)
        self.c.line(mid, 28, mid, PAGE_H - 28)
        self.c.setDash()
        self.y = TOP

    def new_page(self):
        self.c.showPage()
        self.page += 1
        self._draw_chrome()

    def ensure(self, h: float):
        if self.y - h < BOTTOM:
            self.new_page()

    def _wrap(self, text: str, font: str, size: float, width: float) -> list[str]:
        """Wrap keeping English tokens intact; Korean wraps per character."""
        # tokenize: runs of [A-Za-z0-9._+\-]+ or single non-space char or space
        tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9_./+\-]*|\s+|.", text)
        lines: list[str] = []
        cur = ""
        for tok in tokens:
            trial = cur + tok
            if self.c.stringWidth(trial, font, size) <= width:
                cur = trial
            else:
                if cur.strip():
                    lines.append(cur.rstrip())
                # if token itself wider than width, hard-split
                if self.c.stringWidth(tok.strip(), font, size) > width:
                    piece = ""
                    for ch in tok:
                        if self.c.stringWidth(piece + ch, font, size) <= width:
                            piece += ch
                        else:
                            if piece:
                                lines.append(piece)
                            piece = ch
                    cur = piece
                else:
                    cur = tok.lstrip() if tok.isspace() else tok
        if cur.strip():
            lines.append(cur.rstrip())
        return lines or [""]

    def draw_text(
        self,
        text: str,
        *,
        font: str = "KR",
        size: float = BODY_SIZE,
        color=C_BODY,
        leading: float | None = None,
        space_before: float = 0,
        space_after: float = 0,
    ):
        if space_before:
            self.ensure(space_before)
            self.y -= space_before
        lh = leading if leading is not None else size + 3.5
        lines = self._wrap(text, font, size, COL_W)
        for ln in lines:
            self.ensure(lh)
            self.c.setFont(font, size)
            self.c.setFillColor(color)
            self.c.drawString(LEFT, self.y - size, ln)
            self.y -= lh
        if space_after:
            self.y -= space_after

    def render_line(self, s: str):
        s = s.rstrip()
        if not s:
            self.y -= 4
            return
        if s.startswith("■ "):
            self.draw_text(
                s,
                font="KR-B",
                size=PROF_SIZE,
                color=C_PROF,
                space_before=10,
                space_after=2,
            )
        elif s.startswith("과목:"):
            self.draw_text(s, font="KR", size=9.5, color=C_MUTED, space_after=4)
        elif s.startswith("[확정]") or s.startswith("[예상]"):
            self.draw_text(
                s,
                font="KR-B",
                size=HDR_SIZE,
                color=C_HDR,
                space_before=8,
                space_after=2,
            )
        elif s == "정답":
            self.draw_text(
                s,
                font="KR-B",
                size=ANS_SIZE,
                color=C_ANS,
                space_before=3,
                space_after=1,
            )
        elif s.startswith("• ") or re.match(r"^\d+\.\s", s):
            self.draw_text(s, font="KR", size=BODY_SIZE, color=C_BODY)
        elif s.startswith("Samsung AI") or s == "치팅페이퍼":
            self.draw_text(s, font="KR-B", size=14 if s == "치팅페이퍼" else 12, color=C_HDR, space_after=2)
        elif s.startswith("확정문제 전부") or s.startswith("정답 라벨") or s.startswith("구성:") or s.startswith("예상 포함:") or s.startswith("→"):
            self.draw_text(s, font="KR", size=9.5, color=C_Q)
        elif s.startswith("※ ") or s.startswith("시험 직전") or s.startswith("근거:"):
            self.draw_text(s, font="KR", size=9.0, color=C_MUTED, space_before=4)
        elif s.startswith("• 곽:") or s.startswith("• 권:") or s.startswith("• 문:") or s.startswith("• 박:") or s.startswith("• 서:") or s.startswith("• 윤:") or s.startswith("• 주:") or s.startswith("• 최:") or s.startswith("• 홍:"):
            self.draw_text(s, font="KR", size=9.0, color=C_BODY)
        else:
            # question body
            self.draw_text(s, font="KR", size=BODY_SIZE, color=C_Q)

    def build(self, text: str):
        for line in text.split("\n"):
            self.render_line(line)
        self.c.save()


def main():
    raw = extract_text_blocks()
    joined = reflow_join(raw)
    final = insert_sampling_steps(joined)
    # backup original once
    bak = ROOT / "치팅페이퍼_원본백업.pdf"
    if SRC_PDF.exists() and not bak.exists():
        bak.write_bytes(SRC_PDF.read_bytes())
        print(f"Backed up original → {bak.name}")
    doc = CheatDoc(OUT_PDF)
    doc.build(final)
    print(f"Wrote {OUT_PDF} ({doc.page} pages)")


if __name__ == "__main__":
    main()
