const pptxgen = require("pptxgenjs");
const path = require("path");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "이우빈";
pres.title = "ClaudeCoach — 윤성로 교수님 1차 미팅";
pres.subject = "AI Expert 현업과제 지도 미팅";

// Palette — academic navy + teal accent
const C = {
  navy: "0F2744",
  navyMid: "1A3A5C",
  teal: "0D9488",
  tealLt: "14B8A6",
  ice: "E8F4F3",
  cream: "F7F8FA",
  white: "FFFFFF",
  ink: "1E293B",
  muted: "64748B",
  soft: "94A3B8",
  line: "E2E8F0",
  card: "FFFFFF",
  warn: "B45309",
  accent: "F59E0B",
};

const font = "NanumGothic";
const fontH = "NanumSquare";

function addFooter(slide, page, total = 14) {
  slide.addText("AI Expert 현업과제  ·  이우빈  ·  지도교수 윤성로", {
    x: 0.5, y: 5.28, w: 7.2, h: 0.28,
    fontSize: 10, fontFace: font, color: C.soft, margin: 0,
  });
  slide.addText(`${page} / ${total}`, {
    x: 8.5, y: 5.28, w: 1.0, h: 0.28,
    fontSize: 10, fontFace: font, color: C.soft, align: "right", margin: 0,
  });
}

function sectionBar(slide, title) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.teal }, line: { color: C.teal },
  });
  slide.addText(title, {
    x: 0.5, y: 0.28, w: 9, h: 0.5,
    fontSize: 26, fontFace: fontH, bold: true, color: C.navy, margin: 0,
  });
}

// ========== 1. Title ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.navy }, line: { color: C.navy },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625, fill: { color: C.teal }, line: { color: C.teal },
  });
  s.addText("AI EXPERT  ·  현업과제 1차 지도 미팅", {
    x: 0.7, y: 1.15, w: 8.5, h: 0.35,
    fontSize: 13, fontFace: font, color: C.tealLt, bold: true,
    charSpacing: 2, margin: 0,
  });
  s.addText("ClaudeCoach", {
    x: 0.7, y: 1.65, w: 8.5, h: 0.7,
    fontSize: 42, fontFace: fontH, bold: true, color: C.white, margin: 0,
  });
  s.addText("사내 Claude Code 사용 로그 기반\n활용·예산 효율 코칭 엔진", {
    x: 0.7, y: 2.45, w: 8.5, h: 0.85,
    fontSize: 20, fontFace: font, color: "CBD5E1", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 3.5, w: 1.2, h: 0.05, fill: { color: C.teal }, line: { color: C.teal },
  });
  s.addText([
    { text: "발표   ", options: { color: C.soft } },
    { text: "이우빈  ·  삼성전자 DX  S/W문화사무국", options: { color: C.white, breakLine: true } },
    { text: "지도   ", options: { color: C.soft } },
    { text: "윤성로 교수님  ·  서울대학교", options: { color: C.white, breakLine: true } },
    { text: "기간   ", options: { color: C.soft } },
    { text: "2026.08.03 ~ 10.16  (사전 준비 7월)", options: { color: C.white } },
  ], {
    x: 0.7, y: 3.75, w: 8.5, h: 1.2,
    fontSize: 14, fontFace: font, margin: 0,
  });
}

// ========== 2. Agenda ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "Agenda");
  addFooter(s, 2);

  const items = [
    { n: "01", t: "문제 정의", d: "도입·한도·활용 편차" },
    { n: "02", t: "제안: ClaudeCoach", d: "시스템 개요·시나리오" },
    { n: "03", t: "우수 세션 정의", d: "품질 × 효율 이축" },
    { n: "04", t: "방법·실험 설계", d: "Embed · SFT · 평가" },
    { n: "05", t: "일정·KPI", d: "Phase 0~3" },
    { n: "06", t: "지도 요청", d: "오늘 논의하고 싶은 점" },
  ];
  items.forEach((it, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.5 + col * 3.1;
    const y = 1.15 + row * 1.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y, w: 2.9, h: 1.55,
      fill: { color: C.white },
      rectRadius: 0.1,
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.08 },
    });
    s.addText(it.n, {
      x: x + 0.2, y: y + 0.25, w: 2.4, h: 0.35,
      fontSize: 14, fontFace: font, bold: true, color: C.teal, margin: 0,
    });
    s.addText(it.t, {
      x: x + 0.2, y: y + 0.6, w: 2.4, h: 0.4,
      fontSize: 16, fontFace: fontH, bold: true, color: C.navy, margin: 0,
    });
    s.addText(it.d, {
      x: x + 0.2, y: y + 1.05, w: 2.4, h: 0.3,
      fontSize: 12, fontFace: font, color: C.muted, margin: 0,
    });
  });
}

// ========== 3. Context ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "배경 — 왜 지금인가");
  addFooter(s, 3);

  const cards = [
    { title: "도구 도입", body: "Claude Code\nEnterprise 도입\n로그·비용 DB 축적" },
    { title: "예산 제약", body: "1인당 월\n~$180 종량제\n조기 소진·비효율" },
    { title: "조직 pain", body: "부서·개인\n활용 편차\n한도 사용률 편차" },
    { title: "기존 한계", body: "대시보드 =\n정형 지표 중심\n코칭·예시 부재" },
  ];
  cards.forEach((c, i) => {
    const x = 0.45 + i * 2.35;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y: 1.15, w: 2.2, h: 2.7,
      fill: { color: i === 1 || i === 2 ? C.navy : C.white },
      rectRadius: 0.1,
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.08 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.15, w: 2.2, h: 0.1,
      fill: { color: C.teal }, line: { color: C.teal },
    });
    s.addText(c.title, {
      x: x + 0.15, y: 1.45, w: 1.9, h: 0.4,
      fontSize: 15, fontFace: fontH, bold: true,
      color: i === 1 || i === 2 ? C.white : C.navy, margin: 0,
    });
    s.addText(c.body, {
      x: x + 0.15, y: 2.05, w: 1.9, h: 1.5,
      fontSize: 13, fontFace: font,
      color: i === 1 || i === 2 ? "CBD5E1" : C.muted, margin: 0,
    });
  });
  s.addText("파트장 합의 방향: 로그에서 「좋은 사용 예시」를 찾고, 질문에 사내 우수 케이스를 소개", {
    x: 0.5, y: 4.15, w: 9, h: 0.55,
    fontSize: 14, fontFace: font, color: C.ink, italic: true, margin: 0,
  });
  s.addText("차별화는 범용 Claude 성능이 아니라 사내 로그·BP·비용 효율 패턴에 있음", {
    x: 0.5, y: 4.65, w: 9, h: 0.35,
    fontSize: 13, fontFace: font, color: C.teal, margin: 0,
  });
}

// ========== 4. Problem ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "문제 정의");
  addFooter(s, 4);

  const probs = [
    { num: "1", t: "활용 편차", d: "도구만 배포하면 “잘 쓰는 법”을 조직 차원에서 설명·전파하기 어렵다." },
    { num: "2", t: "예산 비효율", d: "월 $180 한도 하 과다 컨텍스트·재시도 누적이 발생하나, 개인 예산 코칭이 없다." },
    { num: "3", t: "지표 vs 조언", d: "기존 대시보드는 집계 중심. “내 상황·남은 예산에 맞는 쓰는 법”이 부족하다." },
    { num: "4", t: "교육 요건", d: "Foundation → 후처리 → 평가 → 서빙 연동 증명이 필요하다 (단순 API 래핑 X)." },
  ];
  probs.forEach((p, i) => {
    const y = 1.05 + i * 0.95;
    s.addShape(pres.shapes.OVAL, {
      x: 0.55, y: y + 0.1, w: 0.48, h: 0.48,
      fill: { color: C.teal }, line: { color: C.teal },
    });
    s.addText(p.num, {
      x: 0.55, y: y + 0.16, w: 0.48, h: 0.4,
      fontSize: 16, fontFace: fontH, bold: true, color: C.white, align: "center", margin: 0,
    });
    s.addText(p.t, {
      x: 1.25, y: y, w: 2.2, h: 0.65,
      fontSize: 16, fontFace: fontH, bold: true, color: C.navy, valign: "middle", margin: 0,
    });
    s.addText(p.d, {
      x: 3.5, y: y, w: 5.9, h: 0.65,
      fontSize: 14, fontFace: font, color: C.ink, valign: "middle", margin: 0,
    });
  });
}

// ========== 5. Proposal ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "제안 — ClaudeCoach");
  addFooter(s, 5);

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.85,
    fill: { color: C.navy }, rectRadius: 0.08,
  });
  s.addText("사용 로그로 우수·저토큰 패턴을 학습·검색하고,\n활용 코칭 + 예산 효율 코칭을 함께 제공하는 엔진", {
    x: 0.7, y: 1.15, w: 8.6, h: 0.7,
    fontSize: 15, fontFace: font, color: C.white, margin: 0,
  });

  const steps = [
    { t: "Ingest", d: "익명화·세션\n토큰·라벨" },
    { t: "Pattern\nEmbed", d: "Contrastive FT\n우수 패턴 검색" },
    { t: "Coach\nModel", d: "LoRA SFT\n코칭 생성" },
    { t: "Budget\nCoach", d: "한도 70/90%\n저토큰 사례" },
    { t: "Serve", d: "DS LLM\nMCP 연동" },
  ];
  steps.forEach((st, i) => {
    const x = 0.45 + i * 1.9;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y: 2.2, w: 1.75, h: 2.0,
      fill: { color: C.white }, rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 6, offset: 1, angle: 135, opacity: 0.08 },
    });
    s.addText(String(i + 1), {
      x, y: 2.35, w: 1.75, h: 0.3,
      fontSize: 12, fontFace: font, bold: true, color: C.teal, align: "center", margin: 0,
    });
    s.addText(st.t, {
      x: x + 0.08, y: 2.7, w: 1.6, h: 0.65,
      fontSize: 13, fontFace: fontH, bold: true, color: C.navy, align: "center", margin: 0,
    });
    s.addText(st.d, {
      x: x + 0.08, y: 3.45, w: 1.6, h: 0.6,
      fontSize: 11, fontFace: font, color: C.muted, align: "center", margin: 0,
    });
    if (i < 4) {
      s.addText("→", {
        x: x + 1.55, y: 2.95, w: 0.4, h: 0.35,
        fontSize: 16, color: C.teal, margin: 0,
      });
    }
  });
  s.addText("원칙: 학습 = AI 포털 GPU  ·  서빙 = DS LLM + 게이트웨이  (GPU 상시 운영 안 함)", {
    x: 0.5, y: 4.5, w: 9, h: 0.35,
    fontSize: 13, fontFace: font, color: C.muted, margin: 0,
  });
}

// ========== 6. Scenarios ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "사용자 시나리오 (MVP)");
  addFooter(s, 6);

  const sc = [
    {
      tag: "A  활용 코칭",
      q: "「레거시 모듈 리팩토링인데 컨텍스트를 어떻게 넣어야 할까요?」",
      a: "유사 태스크 우수 세션 3건 요약\n+ 권장 프롬프트·MCP 패턴\n(출처: 익명 로그 ID)",
    },
    {
      tag: "B  예산 코칭",
      q: "「분석 작업인데 이번 달 예산 70% 썼어요. 어떻게 할까요?」",
      a: "저토큰 우수 세션 3건\n+ 컨텍스트 축소·작업 분할\n+ 예상 토큰 구간 안내",
    },
    {
      tag: "C  운영 가시화",
      q: "부서 A vs B 활용률·한도 사용률·우수 패턴 수 비교",
      a: "대시보드 연동\n코칭 대상 부서 선정\n(기존 UI 고도화)",
    },
  ];
  sc.forEach((item, i) => {
    const x = 0.4 + i * 3.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y: 1.1, w: 3.0, h: 3.7,
      fill: { color: C.white }, rectRadius: 0.1,
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.08 },
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x + 0.15, y: 1.3, w: 2.7, h: 0.4,
      fill: { color: C.ice }, rectRadius: 0.06,
    });
    s.addText(item.tag, {
      x: x + 0.15, y: 1.35, w: 2.7, h: 0.32,
      fontSize: 13, fontFace: font, bold: true, color: C.teal, align: "center", margin: 0,
    });
    s.addText("질문 / 상황", {
      x: x + 0.2, y: 1.9, w: 2.6, h: 0.28,
      fontSize: 11, fontFace: font, color: C.soft, margin: 0,
    });
    s.addText(item.q, {
      x: x + 0.2, y: 2.2, w: 2.6, h: 1.15,
      fontSize: 12, fontFace: font, color: C.ink, margin: 0,
    });
    s.addText("ClaudeCoach", {
      x: x + 0.2, y: 3.4, w: 2.6, h: 0.28,
      fontSize: 11, fontFace: font, color: C.soft, margin: 0,
    });
    s.addText(item.a, {
      x: x + 0.2, y: 3.7, w: 2.6, h: 0.95,
      fontSize: 12, fontFace: font, color: C.navy, margin: 0,
    });
  });
}

// ========== 7. Excellent session (KEY for professor) ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "핵심 연구 이슈 — 우수 세션 정의");
  addFooter(s, 7);

  s.addText("이진 “좋다/나쁘다”가 아니라  품질 × 효율  이축으로 정의 (라벨 가이드 v0)", {
    x: 0.5, y: 0.9, w: 9, h: 0.35,
    fontSize: 14, fontFace: font, color: C.muted, italic: true, margin: 0,
  });

  // Two axes cards
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.4, y: 1.4, w: 4.45, h: 2.55,
    fill: { color: C.white }, rectRadius: 0.1,
    shadow: { type: "outer", color: "000000", blur: 6, offset: 1, angle: 135, opacity: 0.08 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.4, w: 0.12, h: 2.55, fill: { color: C.teal }, line: { color: C.teal },
  });
  s.addText("Quality  (활용 BP)", {
    x: 0.75, y: 1.55, w: 3.9, h: 0.35,
    fontSize: 16, fontFace: fontH, bold: true, color: C.navy, margin: 0,
  });
  s.addText([
    { text: "목표 명확 · 선택적 컨텍스트", options: { breakLine: true } },
    { text: "계획 → 수정 → 검증 흐름", options: { breakLine: true } },
    { text: "다른 사람이 재사용 가능한 패턴", options: { breakLine: true } },
    { text: "루브릭 quality ≥ 2  →  exemplar", options: {} },
  ], {
    x: 0.75, y: 2.1, w: 3.9, h: 1.6,
    fontSize: 13, fontFace: font, color: C.ink, margin: 0,
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.15, y: 1.4, w: 4.45, h: 2.55,
    fill: { color: C.white }, rectRadius: 0.1,
    shadow: { type: "outer", color: "000000", blur: 6, offset: 1, angle: 135, opacity: 0.08 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.15, y: 1.4, w: 0.12, h: 2.55, fill: { color: C.accent }, line: { color: C.accent },
  });
  s.addText("Efficiency  (저토큰)", {
    x: 5.5, y: 1.55, w: 3.9, h: 0.35,
    fontSize: 16, fontFace: fontH, bold: true, color: C.navy, margin: 0,
  });
  s.addText([
    { text: "동일 task_type 대비 상대 토큰", options: { breakLine: true } },
    { text: "하위 20~30% + quality 충족", options: { breakLine: true } },
    { text: "짧은 포기 세션 ≠ 효율", options: { breakLine: true } },
    { text: "Q≥2 ∧ E≥2  →  Budget exemplar", options: {} },
  ], {
    x: 5.5, y: 2.1, w: 3.9, h: 1.6,
    fontSize: 13, fontFace: font, color: C.ink, margin: 0,
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.4, y: 4.15, w: 9.2, h: 0.85,
    fill: { color: C.navy }, rectRadius: 0.08,
  });
  s.addText("MVP 절차: 규칙으로 후보 추출 → 운영자 골드 100건 → 규칙 보정 → 200~500건 확장\n(완전 자동 품질 판정은 Phase 2 — 정의 모호 리스크를 수동 골드로 완화)", {
    x: 0.6, y: 4.28, w: 8.8, h: 0.65,
    fontSize: 13, fontFace: font, color: C.white, margin: 0,
  });
}

// ========== 8. Architecture ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "학습 · 서빙 분리");
  addFooter(s, 8);

  // Left: train
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.4, y: 1.15, w: 4.4, h: 3.55,
    fill: { color: C.white }, rectRadius: 0.1,
    shadow: { type: "outer", color: "000000", blur: 6, offset: 1, angle: 135, opacity: 0.08 },
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.4, y: 1.15, w: 4.4, h: 0.55,
    fill: { color: C.navy }, rectRadius: 0.1,
  });
  // cover bottom radius of header
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.5, w: 4.4, h: 0.2, fill: { color: C.navy }, line: { color: C.navy },
  });
  s.addText("학습 (교육 · GPU)", {
    x: 0.55, y: 1.25, w: 4.1, h: 0.4,
    fontSize: 16, fontFace: fontH, bold: true, color: C.white, margin: 0,
  });
  s.addText([
    { text: "PatternEmbed", options: { bold: true, breakLine: true } },
    { text: "bge-m3 / e5 등 · Contrastive FT", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "CoachModel", options: { bold: true, breakLine: true } },
    { text: "Qwen2.5-7B 등 · LoRA / QLoRA SFT", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "인프라: AI 포털 ~A100 mix", options: { breakLine: true } },
    { text: "7월: 베이스 모델 스코어카드 확정", options: {} },
  ], {
    x: 0.7, y: 1.95, w: 3.9, h: 2.5,
    fontSize: 13, fontFace: font, color: C.ink, margin: 0,
  });

  // Right: serve
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.2, y: 1.15, w: 4.4, h: 3.55,
    fill: { color: C.white }, rectRadius: 0.1,
    shadow: { type: "outer", color: "000000", blur: 6, offset: 1, angle: 135, opacity: 0.08 },
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.2, y: 1.15, w: 4.4, h: 0.55,
    fill: { color: C.teal }, rectRadius: 0.1,
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.5, w: 4.4, h: 0.2, fill: { color: C.teal }, line: { color: C.teal },
  });
  s.addText("운영 (서비스)", {
    x: 5.35, y: 1.25, w: 4.1, h: 0.4,
    fontSize: 16, fontFace: fontH, bold: true, color: C.white, margin: 0,
  });
  s.addText([
    { text: "DS LLM API + 검색 컨텍스트", options: { bold: true, breakLine: true } },
    { text: "어댑터 merge 협의 (DS 팀)", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "MCP", options: { bold: true, breakLine: true } },
    { text: "suggest_usage · find_pattern", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "AWS 게이트웨이 · 대시보드 연동", options: { breakLine: true } },
    { text: "SFT 효과 미미 시 → RAG 중심 축소", options: {} },
  ], {
    x: 5.5, y: 1.95, w: 3.9, h: 2.5,
    fontSize: 13, fontFace: font, color: C.ink, margin: 0,
  });
}

// ========== 9. Data ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "데이터 · 라벨 (MVP 규모)");
  addFooter(s, 9);

  const rows = [
    ["데이터", "출처", "규모", "용도"],
    ["Claude 사용 로그 (익명)", "기존 DB", "5K~20K 세션", "Embed·코칭"],
    ["토큰·비용 메타", "로그/Bedrock", "세션 집계", "Budget·효율"],
    ["우수 세션 라벨", "규칙+운영자", "200~500건", "SFT positive"],
    ["코칭 골드셋", "전문가 작성", "30쌍+", "SFT·A/B"],
  ];
  rows.forEach((r, i) => {
    const y = 1.1 + i * 0.65;
    const bg = i === 0 ? C.navy : i % 2 === 0 ? C.ice : C.white;
    const tc = i === 0 ? C.white : C.ink;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 9, h: 0.6,
      fill: { color: bg }, line: { color: i === 0 ? C.navy : C.line },
    });
    const widths = [2.8, 2.2, 2.0, 2.0];
    let x = 0.55;
    r.forEach((cell, j) => {
      s.addText(cell, {
        x, y: y + 0.12, w: widths[j], h: 0.4,
        fontSize: i === 0 ? 13 : 12, fontFace: font,
        bold: i === 0 || j === 0, color: tc, margin: 0,
      });
      x += widths[j];
    });
  });
  s.addText("법무·PII: 익명화·세션 단위 · 개인 한도 코칭은 본인 조회 또는 익명 벤치마크 중심", {
    x: 0.5, y: 4.55, w: 9, h: 0.35,
    fontSize: 12, fontFace: font, color: C.muted, margin: 0,
  });
}

// ========== 10. Evaluation ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "실험 · 평가 설계");
  addFooter(s, 10);

  // Ablation
  s.addText("코칭 조건 ablation", {
    x: 0.5, y: 1.0, w: 4.5, h: 0.35,
    fontSize: 15, fontFace: fontH, bold: true, color: C.navy, margin: 0,
  });
  const conds = [
    { c: "C0", d: "Base LLM only" },
    { c: "C1", d: "+ 우수 패턴 RAG (top-3)" },
    { c: "C2", d: "+ CoachModel SFT (선택)" },
  ];
  conds.forEach((cd, i) => {
    const y = 1.45 + i * 0.7;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y, w: 4.5, h: 0.58,
      fill: { color: i === 1 ? C.teal : C.white }, rectRadius: 0.06,
      shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 135, opacity: 0.06 },
    });
    s.addText(cd.c, {
      x: 0.7, y: y + 0.12, w: 0.7, h: 0.35,
      fontSize: 15, fontFace: fontH, bold: true, color: i === 1 ? C.white : C.teal, margin: 0,
    });
    s.addText(cd.d, {
      x: 1.5, y: y + 0.12, w: 3.3, h: 0.35,
      fontSize: 14, fontFace: font, color: i === 1 ? C.white : C.ink, margin: 0,
    });
  });

  // KPIs
  s.addText("MVP KPI", {
    x: 5.3, y: 1.0, w: 4.3, h: 0.35,
    fontSize: 15, fontFace: fontH, bold: true, color: C.navy, margin: 0,
  });
  const kpis = [
    { v: "60%+", l: "Hit@3 (30 쿼리)" },
    { v: "3.5+", l: "유용도 (5점)" },
    { v: "50+", l: "파일럿 호출" },
    { v: "9월", l: "E2E 데모" },
  ];
  kpis.forEach((k, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 5.3 + col * 2.2;
    const y = 1.45 + row * 1.35;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y, w: 2.05, h: 1.15,
      fill: { color: C.white }, rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 6, offset: 1, angle: 135, opacity: 0.08 },
    });
    s.addText(k.v, {
      x, y: y + 0.2, w: 2.05, h: 0.45,
      fontSize: 22, fontFace: fontH, bold: true, color: C.teal, align: "center", margin: 0,
    });
    s.addText(k.l, {
      x: x + 0.1, y: y + 0.7, w: 1.85, h: 0.3,
      fontSize: 12, fontFace: font, color: C.muted, align: "center", margin: 0,
    });
  });
  s.addText("SFT 효과 없으면 C1(RAG)만으로도 MVP·논문 완성 가능 — 정직한 fallback", {
    x: 0.5, y: 4.55, w: 9, h: 0.35,
    fontSize: 13, fontFace: font, color: C.muted, italic: true, margin: 0,
  });
}

// ========== 11. Timeline ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "일정 — Phase 0 ~ 3");
  addFooter(s, 11);

  // timeline line
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 2.05, w: 8.6, h: 0.06,
    fill: { color: C.teal }, line: { color: C.teal },
  });

  const phases = [
    { p: "0", m: "7월", t: "모델 선정\n라벨 100\nEmbed·SFT PoC", now: true },
    { p: "1", m: "8월", t: "Ingest\nPatternEmbed\nfind_pattern", now: false },
    { p: "2", m: "9월", t: "Coach SFT\nBudgetCoach\nE2E 데모", now: false },
    { p: "3", m: "10월", t: "대시보드\n파일럿 20명\n설문·보고", now: false },
  ];
  phases.forEach((ph, i) => {
    const x = 0.85 + i * 2.3;
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.55, y: 1.88, w: 0.4, h: 0.4,
      fill: { color: ph.now ? C.accent : C.teal }, line: { color: ph.now ? C.accent : C.teal },
    });
    s.addText(ph.p, {
      x: x + 0.55, y: 1.94, w: 0.4, h: 0.3,
      fontSize: 14, fontFace: fontH, bold: true, color: C.white, align: "center", margin: 0,
    });
    s.addText(ph.m, {
      x, y: 1.35, w: 1.5, h: 0.35,
      fontSize: 16, fontFace: fontH, bold: true, color: C.navy, align: "center", margin: 0,
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y: 2.55, w: 2.0, h: 1.7,
      fill: { color: ph.now ? C.navy : C.white }, rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 6, offset: 1, angle: 135, opacity: 0.08 },
    });
    s.addText(ph.t, {
      x: x + 0.1, y: 2.8, w: 1.8, h: 1.3,
      fontSize: 13, fontFace: font, color: ph.now ? C.white : C.ink, align: "center", margin: 0,
    });
  });
  s.addText("본 과제: 8/3 ~ 10/16   ·   지금은 Phase 0 (정의·데이터·모델 선정)", {
    x: 0.5, y: 4.55, w: 9, h: 0.35,
    fontSize: 13, fontFace: font, color: C.muted, margin: 0,
  });
}

// ========== 12. Paper / academic ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "논문 · 학술 포지션 (가산점)");
  addFooter(s, 12);

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 1.0,
    fill: { color: C.navy }, rectRadius: 0.08,
  });
  s.addText("사내 LLM 코딩 도구 사용 로그 기반 활용·비용 효율 패턴이\n코칭 품질에 미치는 영향  —  실증 연구 (SOTA Agent 아님)", {
    x: 0.7, y: 1.2, w: 8.6, h: 0.75,
    fontSize: 15, fontFace: font, color: C.white, margin: 0,
  });

  const rqs = [
    { id: "RQ1", t: "우수·저토큰 패턴 검색이 유용한 exemplar를 주는가?", m: "Hit@3, MRR" },
    { id: "RQ2", t: "패턴 RAG 코칭이 base LLM 대비 선호되는가?", m: "5점 · pairwise" },
    { id: "RQ3", t: "예산 맥락 포함 시 절약·품질 인식이 달라지는가?", m: "B0 vs B1" },
    { id: "RQ4", t: "(탐색) 코칭 후 동일 태스크 토큰이 감소하는가?", m: "전후 집계" },
  ];
  rqs.forEach((r, i) => {
    const y = 2.25 + i * 0.6;
    s.addText(r.id, {
      x: 0.55, y, w: 0.8, h: 0.45,
      fontSize: 14, fontFace: fontH, bold: true, color: C.teal, valign: "middle", margin: 0,
    });
    s.addText(r.t, {
      x: 1.4, y, w: 6.0, h: 0.45,
      fontSize: 13, fontFace: font, color: C.ink, valign: "middle", margin: 0,
    });
    s.addText(r.m, {
      x: 7.5, y, w: 2.0, h: 0.45,
      fontSize: 12, fontFace: font, color: C.muted, valign: "middle", align: "right", margin: 0,
    });
  });
}

// ========== 13. Discussion / ask professor ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.cream }, line: { color: C.cream },
  });
  sectionBar(s, "오늘 지도 요청 · 논의 포인트");
  addFooter(s, 13);

  const asks = [
    {
      n: "1",
      t: "우수 세션 정의",
      d: "품질 루브릭 · 상대 효율 임계값(P20~30)이 타당한가?\n프록시 신호(재시도 · 컨텍스트 dump) 우선순위?",
    },
    {
      n: "2",
      t: "실험 설계",
      d: "C0/C1/C2 ablation · 골드 규모(30쌍 · 100라벨)\n충분한가?  SFT 우선 vs RAG-first 전략?",
    },
    {
      n: "3",
      t: "패턴 모델링",
      d: "세션 단위 임베딩 입력 형태(요약 vs 스니펫)?\n한도 소진 · 이탈 행동 모델링을 Phase에 넣을지?",
    },
    {
      n: "4",
      t: "논문 범위",
      d: "실증 1안(검색 + 코칭)으로 10월 초안 가능 여부\n투고 타깃(KIISE / KSC) 현실성",
    },
  ];
  asks.forEach((a, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.4 + col * 4.8;
    const y = 1.05 + row * 1.9;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y, w: 4.55, h: 1.7,
      fill: { color: C.white }, rectRadius: 0.1,
      shadow: { type: "outer", color: "000000", blur: 6, offset: 1, angle: 135, opacity: 0.08 },
    });
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.2, y: y + 0.25, w: 0.4, h: 0.4,
      fill: { color: C.teal }, line: { color: C.teal },
    });
    s.addText(a.n, {
      x: x + 0.2, y: y + 0.3, w: 0.4, h: 0.32,
      fontSize: 14, fontFace: fontH, bold: true, color: C.white, align: "center", margin: 0,
    });
    s.addText(a.t, {
      x: x + 0.75, y: y + 0.28, w: 3.5, h: 0.35,
      fontSize: 15, fontFace: fontH, bold: true, color: C.navy, margin: 0,
    });
    s.addText(a.d, {
      x: x + 0.25, y: y + 0.8, w: 4.05, h: 0.75,
      fontSize: 12, fontFace: font, color: C.ink, margin: 0,
    });
  });
}

// ========== 14. Closing ==========
{
  const s = pres.addSlide();
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.navy }, line: { color: C.navy },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625, fill: { color: C.teal }, line: { color: C.teal },
  });
  s.addText("Summary", {
    x: 0.7, y: 1.0, w: 8.5, h: 0.4,
    fontSize: 14, fontFace: font, bold: true, color: C.tealLt, charSpacing: 2, margin: 0,
  });
  s.addText("로그 → 우수·저토큰 패턴 → 코칭", {
    x: 0.7, y: 1.5, w: 8.5, h: 0.55,
    fontSize: 26, fontFace: fontH, bold: true, color: C.white, margin: 0,
  });
  s.addText([
    { text: "현업:  Claude 활용 정착 + 월 $180 한도 내 효율", options: { breakLine: true } },
    { text: "교육:  Embed FT + LoRA SFT + 평가 + 서빙 연동", options: { breakLine: true } },
    { text: "학술:  사용 로그 RAG가 코칭에 도움이 되는가 (실증)", options: { breakLine: true } },
  ], {
    x: 0.7, y: 2.3, w: 8.5, h: 1.3,
    fontSize: 16, fontFace: font, color: "CBD5E1", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 3.8, w: 1.0, h: 0.05, fill: { color: C.teal }, line: { color: C.teal },
  });
  s.addText("지도해 주셔서 감사합니다.\n피드백과 우선순위를 부탁드립니다.", {
    x: 0.7, y: 4.05, w: 8.5, h: 0.8,
    fontSize: 16, fontFace: font, color: C.white, margin: 0,
  });
}

const out = path.join(__dirname, "ClaudeCoach_윤성로교수_1차미팅.pptx");
pres.writeFile({ fileName: out }).then(() => {
  console.log("Wrote", out);
});
