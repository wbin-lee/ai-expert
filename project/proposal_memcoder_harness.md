# 현업과제 제안서 1안 — MemCoder + Code Harness (MVP)

**안 구분**: 1안 (메모리사 Brownfield · AIDLC 연동 · 도메인 모델) — **MVP 우선, 단계적 확장**  
**작성일**: 2026-06-25 (v3 — MVP 범위 축소)  
**작성자**: 이우빈  
**보고 대상**: 누리 파트장 / 실장님 / AI-Expert 현업과제 심사  
**대비**: [2안 DSDN MVP](proposal_2안_dsdn_ai.md) · [3안 ChallengeForge MVP](proposal_3안_challengeforge.md)  
**AIDLC 참조**: [AIDLC Guide](https://nuriguri1228.github.io/AIDLC-Guide/)

---

## 0. 한 줄 요약

> 메모리사 파일럿 repo **1개**에 대해 **Harness Lite(코드 검색 MCP)** + **MemCoder Lite(리뷰 코멘트 SFT·vLLM)** 만 구현한다. Claude Code(Bedrock)가 MCP로 관련 코드를 가져오고, 반복 리뷰 태스크는 **사내 모델**이 처리하는 **동작하는 최소 루프**를 10월까지 완성하고, AIDLC 전 단계·DPO·라우터 등은 **이후 Phase**로 미룬다.

---

## 1. 배경 (왜 MVP인가)

| 현황 | 문제 |
|------|------|
| [AIDLC](https://nuriguri1228.github.io/AIDLC-Guide/) · 메모리사 Brownfield 관심 | 14-Step 전체 + 대형 인프라를 한 번에 하면 **8~10월에 미완성** |
| 대형 코드베이스 + Bedrock 한계 | **검색 + 도메인 1태스크**부터 증명 필요 |
| AI-Expert: SFT·RAG·서빙 | **한 번의 학습→서빙→연동** 완주가 평가에 유리 |
| GPU·vLLM·Bedrock ✅ | MVP에 충분 |

**MVP 성공 정의**: 파일럿 repo에서 Claude Code가 `search_repo` MCP로 컨텍스트를 받고, PR diff 리뷰 초안을 **MemCoder API**로 생성 → 개발자가 검토·수정. **이 한 줄이 10월까지 끝나면 성공.**

---

## 2. MVP 범위 — 딱 2개만

```
Claude Code (Bedrock, AIDLC는 수동 진행)
        │
        ├── MCP: search_repo  ──►  Harness Lite (인덱스·검색)
        │
        └── MCP: review_diff  ──►  MemCoder Lite (vLLM, 리뷰 SFT)
                │
                ▼
           👤 개발자 검토 (HITL)
```

### 2.1 Harness Lite

| MVP 포함 | MVP 제외 (Phase 2+) |
|----------|---------------------|
| 파일럿 repo **1개** 인덱싱 | 다 repo·모노레포 전사 확산 |
| 함수/파일 단위 청킹 + 벡터 검색 | 의존 그래프·모듈 맵·영향 분석 |
| MCP `search_repo(query)` | SRS/DLD·aidlc-docs 연동 |
| 범용 embedding (bge 등) | **MemEmbed** 도메인 fine-tune |
| | `aidlc-state.md` 자동 갱신 |

### 2.2 MemCoder Lite

| MVP 포함 | MVP 제외 (Phase 2+) |
|----------|---------------------|
| OSS Code LM + **LoRA SFT** (리뷰 코멘트 1태스크) | 패치 생성·코드 생성·다태스크 |
| **vLLM** 사내 API 1엔드포인트 | MemRouter 자동 분기 |
| 입력: diff + (선택) Harness 검색 결과 | **DPO / PrefAlign** |
| | Preempt-QA·Gatekeeper 제품화 |

### 2.3 AIDLC와의 관계 (MVP)

| MVP | 이후 |
|-----|------|
| Claude Code로 **AIDLC Brownfield kickoff** 수동 1회 체험 | 14-Step 중 RE·Code Gen 단계에 MCP **공식 연동** |
| Harness가 RE 시 **코드 구조 검색** 보조 | RE 산출물 자동 초안 |
| 👤 기존 AIDLC 승인 게이트 그대로 사용 | FeedbackLoop → DPO |

> MVP는 **AIDLC 인프라 전체가 아니라**, AIDLC를 쓰는 개발자에게 **코드 검색·리뷰 초안** 두 도구를 MCP로 제공하는 것에 집중.

---

## 3. 시스템 개요 (MVP)

```
 파일럿 repo (1개)
       │
       ▼
 [Harness Lite] ──► Vector DB (청크 인덱스)
       │                    │
       │    MCP search_repo │
       ▼                    ▼
 Claude Code ◄──────────────┘
 (Bedrock)
       │
       │    MCP review_diff (diff + optional context)
       ▼
 [MemCoder Lite] ◄── GPU LoRA SFT ── 리뷰 (diff→comment) 3K건
       │
       ▼
   vLLM API
```

**구현 형태**: MCP 서버 1프로세스 + vLLM 배포 + 인덱싱 스크립트 1회. **별도 포털·대시보드 없음.**

---

## 4. 학습 데이터 (MVP 최소)

| 데이터 | 규모 | 용도 |
|--------|------|------|
| PR/MR diff + 리뷰 코멘트 (익명) | **3,000건** | MemCoder SFT |
| 파일럿 repo 소스 | 1 repo | Harness 인덱싱 |
| (없음) | — | SRS/DLD, DPO 쌍은 Phase 2 |

---

## 5. 일정 (8/3 ~ 10/16)

| Phase | 기간 | 산출물 | 완료 기준 |
|-------|------|--------|-----------|
| **0** | 7월 | GPU+vLLM PoC, 리뷰 500건, repo 선정 | LoRA 1회 + inference OK |
| **1** | 8월 | Harness Lite 인덱스, MemCoder SFT v0 | `search_repo` 동작 |
| **2** | 9월 | MCP 2개 연동, SFT 3K 확장 | Claude Code에서 E2E 1회 |
| **3** | 10월 | 파일럿 **2주 사용** + HITL 설문, 보고서 | MVP 성공 정의 충족 |

---

## 6. KPI (MVP만)

| 항목 | 목표 |
|------|------|
| MVP E2E 데모 (search → review 초안) | **9월 말 1회 성공** |
| 리뷰 초안 전문가 적합도 (5점) | **3.0+** (범용 대비 +0.5) |
| `search_repo` Hit@5 (수동 라벨 50쿼리) | **60%+** |
| 파일럿 사용자 실사용 (리뷰 초안 호출) | **20회+** (10월) |
| Bedrock 단독 대비 해당 태스크 토큰 | **체감 절감** (정성, MVP) |

Phase 2 KPI(전사·AIDLC 전체·DPO)는 **10월 보고서에 로드맵으로만** 기술.

---

## 7. Phase 2+ 로드맵 (범위 외, 구체화 예정)

| 순서 | 확장 | 기대 효과 |
|------|------|-----------|
| 1 | **MemEmbed** 도메인 임베딩 | 검색 MRR↑, 논문 1 |
| 2 | MemCoder 태스크 확장 (패치 제안) | Code Gen 보조 |
| 3 | SRS/DLD·aidlc-docs 인덱싱 | AIDLC RE 품질 |
| 4 | **MemRouter** (vLLM vs Bedrock) | 비용 KPI 정량화 |
| 5 | FeedbackLoop + **DPO** | HITL 선호 정렬, 논문 2 |
| 6 | Gatekeeper·Preempt-QA·전사 Harness | 팀 하반기 전략 확산 |

---

## 8. 평가 항목 매핑 (MVP로도 충족)

| 평가 축 | MVP 대응 |
|---------|----------|
| 도전성·혁신성 | Brownfield MCP + 도메인 SFT + Bedrock 하이브리드 **최소 증명** |
| 과제 난이도 | 모델·인덱스·MCP 3층 **실동작** |
| 경영 기여도 | 파일럿 repo 리뷰 보조, Bedrock 부담 일부 전환 |
| 교육 완성도 | **Foundation → LoRA SFT → vLLM Serving → 서비스 연동** 1사이클 |
| 논문 | 10월: 파일럿 결과 기반 1편 방향 확정, 2편은 Phase 2 |

---

## 9. 인프라·리스크

| 항목 | 내용 |
|------|------|
| GPU·vLLM·Bedrock | ✅ (기존 확인) |
| 범위 creep | PR 기준 **MCP 2개 + SFT 1태스크**만 — 기능 추가는 Phase 2 이슈로 |
| SFT 품질 부족 | MVP 포지션: **초안** — HITL 필수, Bedrock은 사용자가 직접 escalate |
| AIDLC 14-Step 미완 | MVP 비목표 — **연동 가능성**만 9월 데모로 시사 |
| 데이터 지연 | 500건으로 7월 PoC, 8월 병행 수집 |

---

## 10. 의사결정 요청

1. **1안 MVP** — 파일럿 repo 1개 + MCP 2개 범위 확정.
2. **MVP 성공 정의** — 위 §1 기준 동의.
3. **리뷰 학습 데이터** — 3K건 추출·익명화 범위.
4. **주임교수** — 여진영(SFT·RAG) / 황승원(Code Model·MCP).

---

## 11. 교육 연계

| 교수 | MVP | Phase 2+ |
|------|-----|----------|
| **여진영** | MemCoder SFT, Harness RAG baseline | MemEmbed, DPO |
| **황승원** | MCP·Code Model | Agentic AIDLC 연동 |
| **양인순** | — | Router reward, DPO |