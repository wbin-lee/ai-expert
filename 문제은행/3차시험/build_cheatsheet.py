#!/usr/bin/env python3
"""3차시험 치팅페이퍼 생성: 확정문제 + 예상문제 → MD + PDF (2단, 왼쪽만)"""

import base64
import re
import sys
from pathlib import Path

import markdown
from markdown.extensions.tables import TableExtension
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent

# 가나다순: 김선주 → 서홍석 → 윤성의 → 이재욱 → 임종우 → 주한별 → 하순회 → 한보형 → 홍승훈
PROFESSORS = [
    ("1. 김선주 교수님", "4. 김선주 교수님 확정문제.md", "김선주 교수님 예상문제.md"),
    ("2. 서홍석 교수님", "1. 서홍석 교수님 확정문제.md", "서홍석 교수님 예상문제.md"),
    ("3. 윤성의 교수님", "3. 윤성의 교수님 확정문제.md", None),
    ("4. 이재욱 교수님", "8. 이재욱 교수님 확정문제.md", "이재욱 교수님 예상문제.md"),
    ("5. 임종우 교수님", "2. 임종우 교수님 확정문제.md", "임종우 교수님 예상문제.md"),
    ("6. 주한별 교수님", "5. 주한별 교수님 확정문제.md", "주한별 교수님 예상문제.md"),
    ("7. 하순회 교수님", "9. 하순회 교수님 확정문제.md", "하순회 교수님 예상문제.md"),
    ("8. 한보형 교수님", "7. 한보형 교수님 확정문제.md", "한보형 교수님 예상문제.md"),
    ("9. 홍승훈 교수님", "6. 홍승훈 교수님 확정문제.md", "홍승훈 교수님 예상문제.md"),
]


def condense_problem(text: str, max_len: int = 320) -> str:
    """문제 본문을 핵심만 남기도록 축약."""
    text = re.sub(r"!\[.*?\]\([^)]+\)", "[그림]", text)
    text = re.sub(r"\n{2,}", "\n", text.strip())
    text = re.sub(r"^#{1,3}\s+", "", text, flags=re.M)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if not lines:
        return ""
    kept = []
    total = 0
    for ln in lines:
        if ln.startswith(">") or (ln.startswith("|") and "---" in ln):
            continue
        if ln.startswith("|"):
            continue
        if total + len(ln) > max_len and kept:
            break
        kept.append(ln)
        total += len(ln)
    result = " ".join(kept)
    if len(result) > max_len:
        result = result[: max_len - 1] + "…"
    return result


def extract_confirmed(content: str) -> list[tuple[str, str, str]]:
    """(번호, 문제, 답안) 리스트 추출."""
    content = re.sub(r"^# .*?\n", "", content, count=1)
    content = re.sub(r"^과목명:.*?\n", "", content, flags=re.M)
    content = re.sub(r"^담당교수:.*?\n", "", content, flags=re.M)
    content = re.sub(r"^---\s*\n", "", content)

    parts = re.split(r"\n## 문제\s*", content)
    results = []
    for part in parts[1:]:
        header, _, body = part.partition("\n")
        num = re.sub(r"[:：].*", "", header.strip())
        has_sub = bool(re.search(r"\n###\s*\(\d+\)", body))
        if has_sub:
            prob = body
            ans_parts = re.split(r"\n###\s*답안(?:\s*\(정답 예시\))?", body)
            ans = "\n\n".join(p.strip() for p in ans_parts[1:] if p.strip())
        else:
            ans_split = re.split(r"\n###\s*답안(?:\s*\(정답 예시\))?", body, maxsplit=1)
            if len(ans_split) == 2:
                prob, ans = ans_split
            else:
                prob, ans = body, ""
        results.append((num, prob.strip(), ans.strip()))
    return results


def extract_predicted(content: str) -> list[tuple[str, str, str]]:
    """예상문제 (번호, 문제, 답안) 추출."""
    pattern = (
        r"(?:^|\n)(?:#{2,3}\s*(?:🔥\s*)?예상문제\s*\d+[^\n]*|"
        r"#{2,3}\s*예상문제\s*\d+[^\n]*)\n"
    )
    chunks = re.split(pattern, content)
    headers = re.findall(pattern, content)
    if not headers:
        return []

    results = []
    for i, header in enumerate(headers):
        body = chunks[i + 1] if i + 1 < len(chunks) else ""
        num_match = re.search(r"예상문제\s*(\d+)", header)
        num = num_match.group(1) if num_match else str(i + 1)

        ans_patterns = [
            r"\n####?\s*답안",
            r"\n####?\s*모범\s*답안",
            r"\n###\s*답안",
        ]
        prob, ans = body, ""
        for ap in ans_patterns:
            sp = re.split(ap, body, maxsplit=1)
            if len(sp) == 2:
                prob, ans = sp[0], sp[1]
                break
        else:
            prob = body
            next_q = re.search(r"\n(?:#{2,3}\s*(?:🔥\s*)?예상문제|\n# [0-9]부)", prob)
            if next_q:
                prob = prob[: next_q.start()]

        prob = re.sub(r"\n---\s*\n.*", "", prob, flags=re.S)
        ans = re.split(r"\n---\s*\n", ans)[0]
        ans = re.split(r"\n(?:#{2,3}\s*(?:🔥\s*)?예상문제|\n# )", ans)[0]

        prob = prob.strip()
        ans = ans.strip()
        if prob:
            results.append((num, prob, ans))
    return results


def resolve_image_path(path: str, src_file: Path) -> Path | None:
    if path.startswith("data:"):
        return None
    p = Path(path) if Path(path).is_absolute() else (src_file.parent / path.replace("%20", " ")).resolve()
    return p if p.exists() else None


def fix_image_paths(text: str, src_file: Path, embed: bool = False) -> str:
    """이미지 경로 정규화. embed=True면 base64 data URI."""
    def repl(m):
        alt, path = m.group(1), m.group(2)
        p = resolve_image_path(path, src_file)
        if not p:
            return m.group(0)
        if embed:
            ext = p.suffix.lstrip(".").lower()
            mime = {"png": "png", "jpg": "jpeg", "jpeg": "jpeg", "gif": "gif", "webp": "webp"}.get(ext, "png")
            data = base64.b64encode(p.read_bytes()).decode("ascii")
            return f"![{alt}](data:image/{mime};base64,{data})"
        return f"![{alt}]({p})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, text)


def build_markdown() -> str:
    lines = ["# 3차시험 치팅페이퍼", "", "> 문제: 핵심만 · 답안: 상세 · PDF: 2단(왼쪽만)", ""]

    lines += ["---", "", "## 제1부. 확정문제", ""]
    for prof, confirmed_file, _ in PROFESSORS:
        path = BASE / confirmed_file
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        items = extract_confirmed(raw)
        lines.append(f"### {prof}")
        for num, prob, ans in items:
            prob_md = fix_image_paths(prob, path, embed=False)
            ans_md = fix_image_paths(ans, path, embed=False)
            prob_imgs = re.findall(r"!\[[^\]]*\]\([^)]+\)", prob_md)
            missing_imgs = [img for img in prob_imgs if img not in ans_md]
            if missing_imgs:
                ans_md = f"{'\n\n'.join(missing_imgs)}\n\n{ans_md}".strip()
            prob_short = re.split(r"\n###\s*답안", prob_md)[0]
            lines += [
                f"#### 확정 Q{num}",
                "",
                f"**문제** {condense_problem(prob_short)}",
                "",
                "**답안**",
                "",
                ans_md,
                "",
            ]

    lines += ["---", "", "## 제2부. 예상문제", ""]
    for prof, _, predicted_file in PROFESSORS:
        if not predicted_file:
            lines.append(f"### {prof}")
            lines.append("*예상문제 파일 없음*")
            lines.append("")
            continue
        path = BASE / predicted_file
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        items = extract_predicted(raw)
        if not items:
            continue
        lines.append(f"### {prof}")
        for num, prob, ans in items:
            prob_md = fix_image_paths(prob, path, embed=False)
            ans_md = fix_image_paths(ans, path, embed=False)
            prob_short = re.split(r"\n####?\s*답안", prob_md)[0]
            lines += [
                f"#### 예상 Q{num}",
                "",
                f"**문제** {condense_problem(prob_short)}",
                "",
                "**답안**",
                "",
                ans_md if ans_md else "(답안은 개념 정리 섹션 참고)",
                "",
            ]

    return "\n".join(lines)


def md_to_html(md_text: str) -> str:
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{
    delimiters: [
      {{left: '$$', right: '$$', display: true}},
      {{left: '$', right: '$', display: false}},
      {{left: '\\\\[', right: '\\\\]', display: true}},
      {{left: '\\\\(', right: '\\\\)', display: false}}
    ],
    throwOnError: false
  }});"></script>
<style>
  @page {{ size: A4; margin: 6mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Noto Sans KR", "Malgun Gothic", sans-serif;
    font-size: 8.2pt;
    line-height: 1.38;
    color: #111;
  }}
  .sheet {{
    display: flex;
    width: 100%;
    min-height: 100vh;
  }}
  .left-col {{
    width: 48%;
    padding: 0 1.5% 0 0;
    border-right: 0.6px dashed #bbb;
  }}
  .right-col {{
    width: 48%;
    padding: 0 0 0 1.5%;
  }}
  h1 {{ font-size: 11.5pt; margin: 0 0 6px; border-bottom: 2px solid #222; padding-bottom: 3px; }}
  h2 {{ font-size: 10pt; margin: 10px 0 4px; color: #0d3b66; border-bottom: 1px solid #0d3b66; }}
  h3 {{ font-size: 9pt; margin: 8px 0 3px; color: #333; }}
  h4 {{ font-size: 8.5pt; margin: 5px 0 2px; color: #555; }}
  p {{ margin: 2px 0; }}
  ul, ol {{ margin: 2px 0; padding-left: 14px; }}
  li {{ margin: 1px 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 3px 0; font-size: 7.8pt; }}
  th, td {{ border: 0.5px solid #999; padding: 2px 3px; vertical-align: top; }}
  th {{ background: #f0f0f0; }}
  img {{ max-width: 100%; height: auto; display: block; margin: 3px 0; }}
  code {{ font-size: 7.8pt; background: #f4f4f4; padding: 0 2px; }}
  pre {{ font-size: 7.5pt; background: #f8f8f8; padding: 4px; overflow-x: auto; }}
  strong {{ color: #1a1a6e; }}
  blockquote {{ margin: 2px 0; padding-left: 6px; border-left: 2px solid #ccc; color: #444; }}
  .katex {{ font-size: 1em; }}
</style>
</head>
<body>
<div class="sheet">
  <div class="left-col">
    {html_body}
  </div>
  <div class="right-col"></div>
</div>
</body>
</html>"""


def verify_pdf(pdf_path: Path) -> dict:
    """PDF 가독성·수식·이미지 검증."""
    import fitz

    doc = fitz.open(pdf_path)
    report = {
        "pages": doc.page_count,
        "images": 0,
        "broken_images": [],
        "text_chars": 0,
        "has_korean": False,
        "has_math_symbols": False,
    }
    for i in range(doc.page_count):
        page = doc[i]
        report["text_chars"] += len(page.get_text())
        text = page.get_text()
        if re.search(r"[가-힣]", text):
            report["has_korean"] = True
        if re.search(r"[∫∑√±×÷≤≥]", text) or "FLOP" in text:
            report["has_math_symbols"] = True
        for img in page.get_images():
            report["images"] += 1
            xref = img[0]
            try:
                doc.extract_image(xref)
            except Exception as e:
                report["broken_images"].append(f"page{i+1}: {e}")
    doc.close()
    return report


def main():
    md_path = BASE / "치팅페이퍼.md"
    pdf_path = BASE / "치팅페이퍼.pdf"
    html_path = BASE / "치팅페이퍼.html"

    md_text = build_markdown()
    md_path.write_text(md_text, encoding="utf-8")
    print(f"✓ MD 생성: {md_path} ({len(md_text):,} chars)")

    html_md = fix_image_paths(md_text, BASE, embed=True)
    html = md_to_html(html_md)
    html_path.write_text(html, encoding="utf-8")
    print(f"✓ HTML 생성: {html_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2500)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            margin={"top": "6mm", "bottom": "6mm", "left": "6mm", "right": "6mm"},
            print_background=True,
        )
        browser.close()

    print(f"✓ PDF 생성: {pdf_path}")

    report = verify_pdf(pdf_path)
    print("\n=== PDF 검증 ===")
    print(f"  페이지: {report['pages']}")
    print(f"  텍스트: {report['text_chars']:,} chars")
    print(f"  이미지: {report['images']}개")
    print(f"  한글 포함: {report['has_korean']}")
    print(f"  수식 기호 포함: {report['has_math_symbols']}")
    if report["broken_images"]:
        print(f"  ⚠ 깨진 이미지: {report['broken_images']}")
        sys.exit(1)
    else:
        print("  ✓ 이미지 정상")
    if report["text_chars"] < 5000:
        print("  ⚠ 텍스트가 너무 적음 — 내용 누락 가능")
        sys.exit(1)
    print("  ✓ 가독성 검증 통과")


if __name__ == "__main__":
    main()
