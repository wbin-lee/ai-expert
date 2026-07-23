# 2안 — DSDN AI (MVP)


---

## 한 줄 요약

사내 Q&A 커뮤니티 **DSDN** 채택 답변 N건으로 **유사 질문 검색(DsdnEmbed)** · **답변 초안(DsdnAnswer)** 모델을 vLLM 서빙하고, Claude Code **MCP 2개**(`search_dsdn`, `draft_answer`) 제공한다. **「검색 → 답변 초안 → 사용자 검토」** 루프 구현이 목표.

---

## 제안 배경

-  **DSDN 운영**에 현재 AI 기능이 없고, 검색·중복 질문이 pain point이다.
- Claude Code 확대 시 **사내 개발 지식(BP·과거 해법)** 이 도구 안으로 들어오지 않는다.
- DSDN 데이터는 구성원이 접근·활용하기 쉬워 **현업 과제 + 조직 기여** 정합도가 높다.

---

## MVP에서 하는 것 (2가지)

| 구성 | 내용 |
|------|------|
| **DsdnEmbed Lite** | (질문, 채택답변) 임베딩 fine-tune, MCP `search_dsdn` |
| **DsdnAnswer Lite** | 질문+유사스레드 → 답변 초안, LoRA SFT + vLLM, MCP `draft_answer` |

**흐름**: Claude Code → DSDN 유사 스레드 검색 → 답변 초안 → **사용자 HITL(검토 후 DSDN 게시는 수동)**

**인프라**: 사내 GPU·vLLM / Claude Code=Bedrock 

---

## 성공 기준 · 일정

| 시점 | 목표 |
|------|------|
| 9월 | search → draft E2E 1회 |
| 10월 | MCP 호출 20회+, 검색 Hit@5 60%+ (50쿼리) |

**데이터**: 채택 답변 있는 스레드 1K건(→3K 확장), 익명화

---

## 기대 효과

- **중복 질문·검색 시간** 절감, 사내 BP 재활용
- Claude Code 사용 시 **DSDN 지식을 MCP로 인용** (Bedrock 토큰 절감 보조)
- AI4SE **집단 지성**의 데이터·서비스 기반 마련 (2안 → 이후 DSDN UI·위키 확장)

---
