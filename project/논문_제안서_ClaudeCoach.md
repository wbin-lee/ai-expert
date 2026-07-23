# 논문 제안서 — ClaudeCoach 관련

**문서번호**: paper-proposal-260710  
**작성일**: 2026-07-10  
**작성자**: 이우빈  
**지도교수**: 윤성로 (서울대)  
**연계 과제**: ClaudeCoach 현업과제 (2026.08 ~ 10.16)

---

## 0. 한 줄 요약

> 사내 **Claude Code Enterprise** 도입 초기, **익명 사용 로그**로 “잘 쓰는 세션”과 **저토큰·고효율 패턴**을 정의하고, 이를 검색·코칭에 넣었을 때 **범용 LLM 대비 도움이 되는지**를 측정하는 **실증(empirical) 논문**을 목표로 한다. 새 모델 아키텍처보다 **데이터·평가·조직 맥락** 기여에 초점을 둔다.

---

## 1. 왜 논문을 쓰는가 (과제와 분리하지 않기)

| 원칙 | 설명 |
|------|------|
| **과제 산출물 = 논문 재료** | Ingest·라벨·Embed·코칭 벤치·파일럿 설문을 그대로 논문 실험으로 사용 |
| **난이도 조절** | SOTA 경쟁이 아니라 **“사내 로그가 코칭에 쓸모 있는가?”** 를 검증하는 연구 |
| **최근 트렌드 정합** | 코딩 에이전트·tool-use·experience memory·엔터프라이즈 LLM 도입 실증은 2024~2026 핫토픽 |

가산점 조건: **주임교수(윤성로) 인정** — 초안 완성 후 1차 미팅(7/31 이전)에서 방향 컨펌 권장.

---

## 2. 논문 후보 (난이도 낮은 순)

### ★ 추천 1안 (메인) — 실증 + RAG/임베딩 비교

**한글 제목 (안)**  
*대규모 기업 내 LLM 코딩 도구 사용 로그 기반 활용·비용 효율 패턴이 코칭 품질에 미치는 영향*

**영문 제목 (안)**  
*Do Enterprise Coding-Assistant Usage Logs Improve Coaching? An Empirical Study of Pattern Retrieval for Budget-Aware Developer Guidance*

**한 줄 기여**  
- 공개 벤치가 아닌 **실제 Enterprise 도입 초기 로그**(익명)에서 우수·저토큰 패턴을 추출하는 **방법 + 소규모 평가 프로토콜** 제시  
- “Claude only” vs “+사내 패턴 검색” vs “+SFT 코칭” **단계별 비교**

**난이도**: ★★☆☆☆ — 새 모델 불필요, 벤치 30~50쿼리 + 설문으로 가능

---

### 2안 (병행·짧은 글) — 도입 초기 관찰 연구

**한글 제목 (안)**  
*Enterprise LLM 코딩 도구 도입 초기 사용자 활용·비용 패턴 관찰 연구*

**영문 제목 (안)**  
*Usage and Cost Patterns in the First Months of Enterprise Claude Code Adoption: A Descriptive Study*

**한 줄 기여**  
- 월 **~$180/인** 한도 하에서의 **부서별 편차·토큰 사용·태스크 유형** 기술 통계  
- 코칭 시스템 없이도 **학계에 없는 조직 규모·제약** 데이터 포인트

**난이도**: ★☆☆☆☆ — 분석 위주, 8~9월 로그만으로 초안 가능

---

### 3안 (여유 시·워크샵) — Budget-aware coaching

**한글 제목 (안)**  
*종량제 예산 제약 하 LLM 코딩 도구 코칭: 저토큰 우수 사례 검색 접근*

**영문 제목 (안)**  
*Budget-Aware Coaching for Metered Enterprise Coding Assistants via Low-Token Exemplar Retrieval*

**난이도**: ★★★☆☆ — 1안 실험에 “예산 맥락” 조건 추가

> **권고**: **10월까지 1안 1편 완주**를 메인으로, 2안은 1안의 §3(데이터 관찰)으로 흡수해도 됨.

---

## 3. 최근 학계 트렌드와의 연결 (Related Work 방향)

논문 서론에서 인용·포지셔닝할 **최근 흐름** (깊은 이론 없이 “우리는 어디에 서 있는가”만):

| 트렌드 (2024~2026) | 대표 맥락 | 본 논문과의 차이 |
|-------------------|-----------|------------------|
| **Coding Agent / Tool-use** | MCP, API 호출, 장기 세션 (ToolHaystack 등) | 사내 **실로그** + **종량제 예산** 맥락 |
| **Experience / Procedural Memory** | trajectory→memory, self-improving agents | 우수 세션을 **코칭용 exemplar**로 재사용 (학습은 Contrastive FT 수준) |
| **Human–AI Collaboration in SE** | “Code with Me or for Me?” 등 | **코칭** 관점 (자동화가 아닌 활용법 전파) |
| **Enterprise LLM adoption** | 대규모 도입·정착·생산성 (산업 보고 다수) | **익명 로그 + 재현 가능한 소규모 벤치** |
| **RAG for domain guidance** | 사내 문서·컨벤션 보강 | 문서 RAG가 아니라 **행동 로그 RAG** |
| **LLM cost / efficiency** | 토큰 절감, routing, cascade | **코칭**으로 저토큰 패턴 전파 효과 측정 |

**피할 것**: “새로운 Agent 아키텍처 제안”, “HumanEval SOTA” — 범위·일정에 맞지 않음.

---

## 4. 연구 질문 (RQs) — 1안 기준

| ID | 연구 질문 | 측정 방법 |
|----|-----------|-----------|
| **RQ1** | 사내 사용 로그에서 추출한 **우수·저토큰 패턴 검색**이 코딩 관련 질문에 **유용한 exemplar**를 제공하는가? | Hit@3, MRR (수동 30~50쿼리) |
| **RQ2** | 패턴 검색 결과를 붙인 코칭이 **범용 LLM only** 대비 선호도·유용도가 높은가? | 5점 Likert, pairwise 선호 (n≥20) |
| **RQ3** | **예산 맥락**(월 한도 대비 사용률)을 코칭에 넣으면 **절약·품질** 인식이 달라지는가? | 조건별 A/B (예산 문구 on/off) |
| **RQ4** (탐색) | 코칭 노출 후 **동일 유형 태스크 세션 토큰**이 감소하는가? | 파일럿 전후 집계 (n 소규모) |

---

## 5. 방법 (과제 ClaudeCoach와 1:1 매핑)

```
[데이터] 익명 Enterprise 로그
    → 세션·태스크·토큰/비용 메타
    → 우수 세션 라벨 (품질 + 동일 태스크 대비 저토큰, 규칙+수동 200~500건)

[PatternEmbed] Contrastive FT (bge-m3 등 1종)
    → 쿼리: 개발자 코칭 질문
    → 검색: 우수 세션 요약·스니펫

[코칭 조건] (논문 ablation)
    C0: DS/Bedrock 베이스 프롬프트 only
    C1: C0 + 검색된 top-3 exemplar (RAG)
    C2: C1 + CoachModel LoRA SFT (선택, 효과 있을 때만)

[Budget 조건]
    B0: 예산 맥락 없음
    B1: "월 한도 $180, 현재 사용률 x%" 포함
```

**논문에 넣을 “방법 기여” (겸손하게)**  
1. Enterprise 코딩 로그용 **우수·저토큰 세션 라벨 가이드 v0**  
2. **Budget-aware coaching** 질의·응답 벤치 30~50쌍 (익명화 템플릿)  
3. 코딩 도구 코칭용 **3-way ablation 프로토콜** (base / +RAG / +SFT)

---

## 6. 실험 설계 (심사·리뷰어 공격 대비)

### 6.1 오프라인 (필수)

| 실험 | 내용 | 목표 수치 |
|------|------|-----------|
| 검색 | 30~50 코칭 쿼리, 전문가가 relevant exemplar 지정 | Hit@3 ≥ 60% |
| 생성 | C0/C1(/C2) 블라인드 pairwise | C1 > C0 선호 ≥ 60% |
| 예산 | B0 vs B1 유용도·“절약 도움” 항목 | B1 우위 또는 동등+절약 항목↑ |

### 6.2 파일럿 (선택·짧게)

- n=15~25, 2주간 코칭 MCP/위젯 사용  
- 설문: 유용도, **다시 쓸 의향**, (선택) 다음 세션 토큰 self-report  
- **통계**: t-test보다 **효과 크기 + 신뢰구간** 간단 기술 (n 작음을 인정)

### 6.3 한계 (Discussion에 선제 기재 — 리뷰어 공격 완화)

- 단일 기업·단일 도구(Claude Code Enterprise)  
- 로그·라벨 **비공개** → 벤치 프로토콜·익명 샘플 쿼리만 공개  
- 인과(생산성↑)보다 **코칭 유용도·검색 품질** 중심  
- SFT 효과 미미 시 **C1(RAG)만으로 논문 완성** (정직한 결론)

---

## 7. 기대 기여 (Contribution) — 초안 문장

1. **Empirical**: 종량제 예산(~$180/월)이 있는 Enterprise 코딩 도구 환경에서 **초기 사용·비용 패턴**을 기술한다.  
2. **Methodological**: 행동 로그 기반 **우수·저토큰 exemplar** 라벨링 및 검색·코칭 **평가 프로토콜**을 제안한다.  
3. **Practical**: 범용 LLM 대비 **사내 패턴 검색(RAG)** 이 코칭에 유의미한지 실증한다. (SFT는 부가 실험)

---

## 8. 투고처 후보 (난이도·일정 순)

| 우선순위 | 저널/학회 | 유형 | 비고 |
|:---:|-----------|------|------|
| **1** | **정보과학회논문지 (KIISE Journal)** | 국내 저널 | 상시 투고, 실증·시스템 논문 수용, **난이도 적합** |
| **2** | **한국정보과학회 KSC** (동계) | 국내 학술대회 | 9~10월 마감 (연도별 확인), 6~8페이지 |
| **3** | **NLP4Prog / AI4Code 워크샵** (ACL·ICSE 계열) | 국제 워크샵 | 코딩+LLM fit, short paper |
| **4** | **소프트웨어공학회 (KSE)** 워크샵 | 국내 | SE+AI 실무 사례 |

> **10월 목표**: KIISE 또는 KSC **초안 제출** — 주임교수 인정·가산점용.

---

## 9. 일정 (과제와 병행)

| 시기 | 논문 작업 | 과제 산출물 |
|------|-----------|-------------|
| **7월** | RQ·벤치 쿼리 30개 초안, Related Work 10편 스케치 | 모델 선정 PoC, 골드 30쌍 |
| **8월** | 라벨 가이드 v0, 관찰 통계(2안 §) | Ingest, PatternEmbed |
| **9월** | C0/C1(/C2) ablation, 표·그래프 | CoachModel, E2E |
| **10월** | 초안 작성·교수 리뷰, 제출 | 파일럿, 최종 보고 |

**페이지 목표**: 초안 **6~8페이지** (학회) / **10~12페이지** (저널 short).

---

## 10. 논문 구조 (템플릿)

1. **Introduction** — Enterprise 코딩 도구 도입·예산 제약·코칭 gap  
2. **Background** — coding agents, tool-use, experience memory, RAG (1~1.5p)  
3. **Context & Data** — 익명 로그, $180/월, 부서 편차 (관찰)  
4. **Method** — 라벨 가이드, PatternEmbed, 코칭 조건 C0/C1/C2, Budget B0/B1  
5. **Evaluation** — 검색·생성·파일럿  
6. **Results** — 표 중심, RQ별  
7. **Discussion** — 한계, 윤리, 왜 SFT가/가n't helped  
8. **Conclusion**

---

## 11. Related Work 스타터 (읽을 논문 8편)

| # | 방향 | 검색 키워드 / 예시 |
|---|------|-------------------|
| 1 | Tool-use 장기 상호작용 | ToolHaystack, ToolLLM |
| 2 | Experience memory | ReasoningBank, PRINCIPLES (strategy memory) |
| 3 | Human-AI coding | "Code with Me or for Me", Copilot productivity studies |
| 4 | Coding agent benchmark | SWE-bench (배경만), COFEE-GYM (피드백) |
| 5 | RAG for SE | domain-specific retrieval for code |
| 6 | Enterprise adoption | internal survey / Microsoft GitHub Copilot studies (인용만) |
| 7 | LLM cost efficiency | routing, cascade (배경) |
| 8 | Coaching / tutoring LLM | 가벼운 교육용 agent (직접 유사도 낮아도 §2.1에 한 줄) |

*구체 bibtex는 8월 Related Work 정리 시 Zotero/엑셀로 관리.*

---

## 12. 윤성로 교수님께 확인할 것 (1차 미팅 안건)

1. **1안 vs 2안** 단일화 — 저널 vs 학회 타깃  
2. **RQ 개수** — 3개로 줄일지 (RQ4 탐색은 부록)  
3. **통계 방법** — n=20 파일럿에서 무엇까지 주장할지  
4. **저자·학생 조교** 역할 (벤치 검수, 표 작성 등)  
5. **주임교수 인정**에 필요한 최소 분량·실험 기준  

---

## 13. 리스크 & 대응 (논문 관점)

| 리스크 | 대응 |
|--------|------|
| SFT 효과 없음 | **RAG-only 논문**으로 제목·결론 수정 (정직한 negative result도 기여) |
| 데이터 부족 | 관찰+소규모 벤치로 **short paper** |
| 공개 불가 | 익명 **쿼리 템플릿 + 평가 스크립트** 공개 |
| 일정 지연 | KSC short → KIISE 순 연기, 과제 보고와 논문 초안 분리 |

---

## 14. 다음 액션 (이번 주)

- [ ] 교수님 메일 발송 + 본 제안서 §2 **1안** 방향 구두 컨펌  
- [ ] 코칭 벤치 쿼리 **30개** 초안 (레거시/리팩토링/MCP/예산 4유형 × 7~8개)  
- [ ] Related Work **5편** 초벌 읽기 (§11 #1~5)  

---

*연계: `proposal(260707).md`, `현업과제_제안서_ClaudeCoach.docx`, `메일_윤성로교수_지도요청.md`*