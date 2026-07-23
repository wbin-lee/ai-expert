#!/usr/bin/env python3
"""Generate A4 one-page project submission PDF."""

from fpdf import FPDF
from pathlib import Path

FONT_REGULAR = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"
OUTPUT = Path(__file__).parent / "현업과제_제안서_ClaudeCoach.pdf"


class SubmissionPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("NanumGothic", size=8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "AI Expert 위탁교육 · 현업과제 제안서", align="C")


def section_title(pdf: FPDF, text: str):
    pdf.set_font("NanumGothicBold", size=11)
    pdf.set_text_color(30, 60, 110)
    pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(30, 60, 110)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)


def body_text(pdf: FPDF, text: str, bold_prefix: str | None = None):
    pdf.set_font("NanumGothic", size=10)
    pdf.set_text_color(30, 30, 30)
    if bold_prefix:
        pdf.set_font("NanumGothicBold", size=10)
        pdf.write(5, bold_prefix)
        pdf.set_font("NanumGothic", size=10)
        pdf.write(5, text)
        pdf.ln(6)
    else:
        pdf.multi_cell(0, 5.2, text)
        pdf.ln(1)


def main():
    pdf = SubmissionPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(18, 16, 18)
    pdf.add_page()

    pdf.add_font("NanumGothic", "", FONT_REGULAR)
    pdf.add_font("NanumGothicBold", "", FONT_BOLD)

    pdf.set_font("NanumGothicBold", size=15)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(0, 9, "AI Expert 현업과제 제안서", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("NanumGothic", size=9)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(
        0,
        5,
        "작성자: 이우빈  |  지도교수: 윤성로(서울대)  |  과제: 2026.08~10",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    section_title(pdf, "1. 프로젝트 주제")
    pdf.set_font("NanumGothicBold", size=11)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 6, "사내 AI 코딩 도구 활용·예산 효율 코칭 시스템 (ClaudeCoach)")
    pdf.ln(2)

    section_title(pdf, "2. 프로젝트 소개")

    intro_proposal = (
        "최근 사내 Claude Code Enterprise가 도입되었으며, 1인당 월 약 $180(종량제) "
        "사용 한도가 있습니다. "
        "사용 로그를 분석해 우수·저토큰 고효율 활용 사례를 검색·추천하고 "
        "맞춤 코칭을 제공하는 ClaudeCoach 시스템을 구축합니다. "
        "기존 활용 대시보드·AWS 게이트웨이를 확장하며 "
        "① 로그 정제·토큰/비용 메타·우수 세션 라벨링, "
        "② PatternEmbed, ③ CoachModel(LoRA SFT), "
        "④ BudgetCoach(한도 사용률·저토큰 사례·컨텍스트 축소 권고), "
        "⑤ DS LLM·게이트웨이 연동으로 구성됩니다. "
        "「예산 70% 썼는데 레거시 분석 어떻게 해?」에 "
        "저토큰 우수 세션·작업 분할·MCP 패턴을 제안합니다."
    )
    body_text(pdf, intro_proposal, bold_prefix="제안 내용  ")

    intro_tech = (
        "지도교수: 서울대 윤성로 교수님. "
        "7월 PoC·골드셋 후 8월 본격 수행. "
        "학습은 AI 포털 GPU, 운영은 DS LLM API. "
        "활용·비용 효율 패턴 분석·실험 설계 지도. "
        "평가: Hit@k, 설문, DS 베이스 A/B, (탐색) 토큰 절감."
    )
    body_text(pdf, intro_tech, bold_prefix="기술·인프라  ")

    intro_effect = (
        "활용도·생산성과 월 $180 한도 내 Bedrock 비용 효율 향상에 기여합니다. "
        "10월 MVP: E2E 데모, 파일럿 50회+, Hit@3 60%+, 한도 사용률 대시보드."
    )
    body_text(pdf, intro_effect, bold_prefix="기대 효과  ")

    print(f"소개 본문 글자수: {len(intro_proposal + intro_tech + intro_effect)}")
    pdf.output(str(OUTPUT))
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()