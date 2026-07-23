# 현업과제 제안서 2안 — DSDN AI (MVP)

**안 구분**: 2안 (S/W Culture사무국 · **DSDN** · Q&A RAG) — **MVP 우선, 단계적 확장**  
**작성일**: 2026-06-25 (v3 — MVP 범위 축소)  
**작성자**: 이우빈  
**보고 대상**: 누리 파트장 / AI-Expert 현업과제 심사  
**대비**: [1안 MVP](proposal_memcoder_harness.md) · [3안 ChallengeForge MVP](proposal_3안_challengeforge.md)

> **DSDN**: 사내 Stack Overflow 성격의 S/W 개발 Q&A·지식 커뮤니티

---

## 0. 한 줄 요약

> DSDN 채택 답변 스레드 **1K건**으로 **DsdnEmbed Lite(검색)** · **DsdnAnswer Lite(답변 초안 SFT)** 를 학습·vLLM 서빙하고, Claude Code(Bedrock) **MCP 2개**(`search_dsdn`, `draft_answer`)만 제공한다. DSDN UI 개편·위키 자동화·DPO는 **Phase 2+**.

**MVP 성공 정의**: Claude Code에서 질문 입력 → 유사 스레드 검색 → 답변 초안 생성 → 사용자가 검토·수정. **9월 E2E 1회 + 10월 호출 20회+.**

---

## 1. 1안과의 관계

| | 1안 MVP | 2안 MVP |
|---|---------|---------|
| **데이터** | 파일럿 repo + 리뷰 | **DSDN Q&A** |
| **MCP** | `search_repo`, `review_diff` | `search_dsdn`, `draft_answer` |
| **모델** | MemCoder (리뷰 SFT) | DsdnEmbed + DsdnAnswer |
| **조직** | 메모리 파일럿 | **사무국 DSDN** |

---

## 2. 배경 (왜 MVP인가)

| 현황 | 문제 |
|------|------|
| DSDN에 개발 Q&A 축적 | 검색 약함, **중복 질문** |
| Claude Code 10K (Bedrock) | 사내 해법을 **도구 안에서 못 찾음** |
| 사무국 핵심 업무 = DSDN 운영 | AI 기능 **한 가지**라도 동작해야 함 |
| AI-Expert: RAG·SFT·서빙 | DSDN 데이터 접근 용이, **작게 시작** 가능 |

한 번에 UI·위키·DPO까지 하면 1안과 같이 **미완성** 위험. **MCP 2개 + 검색·초안 2모델**만 먼저 완주.

---

## 3. MVP 범위 — 2 MCP · 2 모델

```
Claude Code (Bedrock)
        │
        ├── MCP: search_dsdn   ──►  DsdnEmbed Lite + Vector DB
        │
        └── MCP: draft_answer  ──►  DsdnAnswer Lite (vLLM)
                │
                ▼
           👤 사용자 검토 (HITL, DSDN 게시는 수동)
```

### 3.1 Ingest Lite (스크립트만, 제품 아님)

| MVP | Phase 2+ |
|-----|----------|
| DSDN 덤프/API → **채택 답변 있는 스레드** 추출 | 실시간 ingest 파이프라인 |
| 익명화 JSONL **1K건** (8월 **3K** 확장) | 전체 코퍼스·위키 후보 생성 |
| 질문 + 채택답변 텍스트만 | 댓글·코드스니펫·태그 정교화 |

### 3.2 DsdnEmbed Lite

| MVP | Phase 2+ |
|-----|----------|
| (질문, 채택답변) 쌍 **Contrastive FT** | hard negative·코드 스니펫 |
| 벡터 DB + `search_dsdn` | DSDN **웹 UI** 유사질문 위젯 |
| 7월: 범용 bge PoC → 8월: FT v0 | MRR 벤치 자동화 |

### 3.3 DsdnAnswer Lite

| MVP | Phase 2+ |
|-----|----------|
| 입력: 질문 + `search_dsdn` 상위 3건 | UI 내 원클릭 초안 |
| 출력: **답변 초안** (게시 전 HITL) | 위키·튜토리얼 자동화 |
| LoRA SFT, vLLM 1엔드포인트 | **DsdnAlign DPO** |
| | Bedrock escalate 자동화 |

### 3.4 HITL (MVP)

- AI는 **초안·검색만**. DSDN 게시·편집은 **사람이 기존 UI로** 처리.
- (chosen, rejected) 로그 수집은 **Phase 2** (DPO용).

---

## 4. 시스템 개요 (MVP)

```
 DSDN export (1K~3K 스레드)
       │
       ▼
 [Ingest 스크립트] ──► JSONL
       │
       ├─────────────────┐
       ▼                 ▼
 DsdnEmbed Lite     DsdnAnswer Lite
 (GPU FT)           (GPU LoRA SFT)
       │                 │
       ▼                 ▼
 Vector DB            vLLM API
       │                 │
       └────────┬────────┘
                ▼
         MCP Server (2 tools)
                │
                ▼
         Claude Code (Bedrock)
```

**별도 포털·DSDN 프론트 개발 없음** (MVP).

---

## 5. 학습 데이터 (MVP)

| 데이터 | 규모 | 용도 |
|--------|------|------|
| 채택 답변 스레드 (익명) | 1K → 3K | Embed FT + Answer SFT |
| 수동 평가 쿼리 | 50개 | search Hit@5 |

---

## 6. 일정 (8/3 ~ 10/16)

| Phase | 기간 | 산출물 | 완료 기준 |
|-------|------|--------|-----------|
| **0** | 7월 | DSDN 500스레드, bge PoC, Embed FT 1회 | 검색 데모 OK |
| **1** | 8월 | Ingest 1K, DsdnEmbed v0, `search_dsdn` | Hit@5 50% on 50쿼리 |
| **2** | 9월 | DsdnAnswer SFT v0, `draft_answer`, **E2E** | Claude Code 1회 성공 |
| **3** | 10월 | 3K 확장, 파일럿 2주, 보고 | 호출 20회+, 설문 |

---

## 7. KPI (MVP만)

| 항목 | 목표 |
|------|------|
| E2E (search → draft) | **9월 말 1회** |
| `search_dsdn` Hit@5 (50쿼리) | **60%+** |
| 답변 초안 적합도 (5점) | **3.0+** |
| MCP 호출 (10월) | **20회+** |
| 중복 질문 등록 감소 | **정성** (파일럿 그룹 인터뷰) |

위키 20건·MRR@10·DPO는 **Phase 2 KPI**.

---

## 8. Phase 2+ 로드맵

| 순서 | 확장 |
|------|------|
| 1 | DSDN **질문 작성 화면** 유사질문·초안 UI |
| 2 | Ingest 실시간·코드 스니펫 인덱싱 |
| 3 | 위키·튜토리얼 자동 초안 + 사무국 HITL |
| 4 | FeedbackLoop + **DsdnAlign DPO** |
| 5 | 1안 Harness MCP가 `search_dsdn` 호출 |

---

## 9. 평가·조직 기여 (MVP)

| 평가 축 | MVP 대응 |
|---------|----------|
| 도전성 | 사내 Q&A 특화 Embed+SFT, MCP·Bedrock 연동 |
| 난이도·중요도 | DSDN 단일 플랫폼, 사무국 직무 정합 |
| 경영 기여 | 중복 질문·검색 시간 절감 (파일럿) |
| 교육 완성도 | **Embed FT + Answer SFT + vLLM + MCP** 1사이클 |
| 논문 | 10월 방향 확정, 본실험은 Phase 2 |

---

## 10. 범위 외

- DSDN UI 대규모 개편 (MVP는 MCP만)
- 위키·튜토리얼 자동 발행
- DPO / DsdnAlign
- RepoScout, 스킬 마켓, 활용도 대시보드, 리뷰 Agent, 1안 Harness

---

## 11. 리스크

| 리스크 | 대응 |
|--------|------|
| DSDN 데이터 추출 지연 | 500건으로 7월 PoC, API 협의 병행 |
| 노이즈 답변 | **채택 답변만** 학습 |
| 답변 환각 | RAG 필수 + 출처 스레드 ID 반환 + 초안 포지셔닝 |
| 범위 creep | **MCP 2개 고정**, UI는 Phase 2 이슈 |

---

## 12. 의사결정 요청

1. **2안 MVP** 범위 확정 (MCP 2개).
2. DSDN 스레드 추출 **1K건** 범위·법무.
3. Claude Code 파일럿 사용자 그룹 (10~20명).
4. **주임교수** — 여진영 1순위.

---

## 13. 교육 연계

| 교수 | MVP | Phase 2+ |
|------|-----|----------|
| **여진영** | DsdnEmbed, DsdnAnswer SFT | DPO, Distillation |
| **황승원** | MCP·IR | Agentic |
| **양인순** | — | DsdnAlign |