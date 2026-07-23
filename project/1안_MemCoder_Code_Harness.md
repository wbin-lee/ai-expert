# 1안 — MemCoder + Code Harness (MVP)

---

## 한 줄 요약

메모리사 파일럿 repo n개에 **코드 검색(Harness)** + **리뷰 초안 생성(MemCoder)** 을 사내 vLLM으로 서빙하고, Claude Code(Bedrock)에서 MCP 2개로 호출한다.  **「검색 → 리뷰 초안 → 개발자 검토」** 최소 루프 1회 구현을 목표.

---

## 제안 배경

- **AIDLC** 활용 대형 코드베이스 컨텍스트·Bedrock 비용이 병목이다.
- AI-Expert 교육 내용은 **모델 SFT → vLLM 서빙 → 실서비스 연동** 으로 포함한다.

---

## MVP에서 하는 것 (2가지)

| 구성 | 내용 |
|------|------|
| **Harness Lite** | 파일럿 repo 인덱싱, MCP `search_repo` |
| **MemCoder Lite** | PR diff → 리뷰 코멘트 초안, LoRA SFT + vLLM, MCP `review_diff` |

**흐름**: Claude Code → 코드 검색 → 리뷰 초안 → **개발자 HITL(검토·수정)**

**인프라**: 사내 GPU·vLLM  / Claude Code=Bedrock 

---

## 성공 기준 · 일정

| 시점 | 목표 |
|------|------|
| 9월 | Claude Code E2E 데모 1회 |
| 10월 | 파일럿 실사용 20회+, 현업 과제 보고 |

**데이터**: 익명화 리뷰 코멘트 약 3K건(최소), 파일럿 repo N개

---

## 기대 효과

- 메모리사 **AIDLC 활용 시 코드 맥락·리뷰 보조** 실증
- 반복 리뷰를 사내 모델로 처리해 **Bedrock 부담 일부 절감**
- 팀 AI-DLC 전략의 **실행 레이어** 프로토타입

---
