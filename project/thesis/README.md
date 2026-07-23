# ClaudeCoach — 추천 논문 리딩 리스트

**문서번호**: thesis-reading-list-260722  
**작성일**: 2026-07-22  
**연계**: `project/proposal(260707).md`, `project/논문_제안서_ClaudeCoach.md`  
**목적**: 우수 세션 정의·PatternEmbed·코칭 SFT·BudgetCoach·평가 설계에 바로 붙일 **관련 논문 지도**

---

## 0. 이 폴더를 읽는 법

| 상황 | 추천 경로 |
|------|-----------|
| **시간 2~3시간** | §1 필수 8편만 (초록 + Related Work 표 1개) |
| **1주일 (Phase 0)** | §1 필수 + §2 경험/메모리 + §3 RAG·임베딩 |
| **논문 초안 작성** | §1~§6 전체 + §8 인용 매핑 표 |
| **피하고 싶은 함정** | §9 Anti-reading (범위 creep 방지) |

**원칙 (논문 제안서와 동일)**  
- SOTA Agent 아키텍처·HumanEval 경쟁 논문은 **깊게 파지 않음**  
- 읽을 때는 항상: *「우리 사내 로그 → 우수 exemplar → 검색/코칭」* 에 어떻게 연결되나?

---

## 1. 필수 8편 (Must-read, ★★★)

과제 MVP·논문 Related Work 골격에 가장 직접적인 논문.

| # | 논문 | 연도 | 링크 | ClaudeCoach 연결 |
|---|------|------|------|-----------------|
| 1 | **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks** (Lewis et al.) | 2020 | [arXiv:2005.11401](https://arxiv.org/abs/2005.11401) | C0 vs C1(RAG) ablation의 원형. **문서 RAG ≠ 행동 로그 RAG** 포지셔닝 근거 |
| 2 | **ExpeL: LLM Agents Are Experiential Learners** (Zhao et al., AAAI 2024) | 2023/24 | [arXiv:2308.10144](https://arxiv.org/abs/2308.10144) | trajectory → insight 추출. 우수 세션을 **자연어 교훈**으로 요약하는 방법 참고 |
| 3 | **Voyager: An Open-Ended Embodied Agent with LLMs** (Wang et al.) | 2023 | [arXiv:2305.16291](https://arxiv.org/abs/2305.16291) | skill library + **임베딩 검색**으로 재사용. PatternEmbed의 개념적 친척 (도메인은 다름) |
| 4 | **The Impact of AI on Developer Productivity: Evidence from GitHub Copilot** (Peng et al.) | 2023 | [arXiv:2302.06590](https://arxiv.org/abs/2302.06590) | 코딩 어시스턴트 **생산성 실증** 벤치마크. 우리 논문의 “도입·활용” 서론 인용 |
| 5 | **Measuring GitHub Copilot’s Impact on Productivity** (Ziegler et al., CACM) | 2024 | [CACM](https://cacm.acm.org/research/measuring-github-copilots-impact-on-productivity/) | **자기보고 + 사용 로그** 병행. 파일럿 설문·토큰 지표 설계에 참고 |
| 6 | **BGE M3-Embedding** (Chen et al.) | 2024 | [arXiv:2402.03216](https://arxiv.org/abs/2402.03216) | PatternEmbed 후보 `bge-m3`. 다국어·긴 입력 — 사내 한·영 혼용 로그에 적합 |
| 7 | **LoRA: Low-Rank Adaptation of Large Language Models** (Hu et al.) | 2021 | [arXiv:2106.09685](https://arxiv.org/abs/2106.09685) | CoachModel LoRA SFT의 표준 근거. GPU 제약(~A100) 정당화 |
| 8 | **A Unified Approach to Routing and Cascading for LLMs** (Dekoninck et al.) | 2024 | [arXiv:2403.12033](https://arxiv.org/abs/2403.12033) | **비용–품질 trade-off**. BudgetCoach·한도 코칭 이론 배경 (라우팅 자체는 MVP 제외) |

### 1.1 필수 8편 — 읽을 때 체크리스트

각 논문을 읽을 때 아래 질문에 **한 줄씩** 메모해 두면 라벨 가이드·논문 Method에 바로 쓸 수 있다.

1. **무엇을 “좋은 경험/결과”로 정의했는가?** (성공 라벨, 보상, human preference…)  
2. **그 정의를 로그/관측만으로 근사할 수 있는가?** (우리 데이터 필드와 매핑)  
3. **검색 단위는 무엇인가?** (문서 청크 / skill / insight / trajectory 요약)  
4. **평가 지표는 무엇인가?** (Hit@k, 선호도, 비용, 태스크 성공률)  
5. **우리 기여와의 차이 한 문장** (예: “우리는 에이전트 self-play가 아니라 **인간 개발자 Enterprise 로그 + 월 $180 예산**”)

---

## 2. 경험 메모리 · Trajectory 재사용 (★★★ ~ ★★)

> 기획 키워드: *Experience / Procedural Memory*, 우수 세션 → exemplar

| 논문 | 링크 | 왜 읽나 | 깊이 |
|------|------|---------|:----:|
| **ExpeL** (위 필수) | [2308.10144](https://arxiv.org/abs/2308.10144) | 성공/실패 trajectory에서 **insight 추출** → 이후 few-shot. 우수 세션 **요약 템플릿** 설계에 직결 | ★★★ |
| **Voyager** (위 필수) | [2305.16291](https://arxiv.org/abs/2305.16291) | skill을 임베딩 인덱싱·검색. “패턴 라이브러리” UX 참고 | ★★★ |
| **Reflexion: Language Agents with Verbal Reinforcement Learning** (Shinn et al.) | [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) | 실패 후 **언어적 반성** 메모리. hard_negative 세션 → “하지 말 것” 코칭 문구에 응용 | ★★ |
| **Generative Agents** (Park et al.) | [arXiv:2304.03442](https://arxiv.org/abs/2304.03442) | 관찰 → 기억 → 성찰 → 검색. **세션 요약 계층**(raw log ≠ coaching memory) 설계 영감 | ★★ |
| **MemGPT** (Packer et al.) | [arXiv:2310.08560](https://arxiv.org/abs/2310.08560) | 컨텍스트 윈도우 관리·계층 메모리. BudgetCoach의 “컨텍스트 축소” 권고와 인접 | ★☆ (선택) |

**ClaudeCoach 적용 포인트**  
- ExpeL/Voyager는 **에이전트가 스스로** 경험을 쌓음.  
- 우리는 **이미 쌓인 인간 사용 로그**에서 우수/저토큰을 **라벨링**해 재사용.  
- 논문 포지션: *human usage-log memory for coaching*, not *self-improving coding agent*.

---

## 3. RAG · Dense Retrieval · 임베딩 (★★★)

> 컴포넌트: PatternEmbed, `find_pattern`, Hit@3 KPI

| 논문 | 링크 | 왜 읽나 | 깊이 |
|------|------|---------|:----:|
| **RAG** (Lewis et al., 필수) | [2005.11401](https://arxiv.org/abs/2005.11401) | parametric + non-parametric. C1 조건의 이론 | ★★★ |
| **BGE-M3** (필수) | [2402.03216](https://arxiv.org/abs/2402.03216) | 다국어·multi-granularity. 세션 요약(짧은 쿼리) vs 로그 스니펫(긴 문서) | ★★★ |
| **Text Embeddings by Weakly-Supervised Contrastive Pre-training** (E5, Wang et al.) | [arXiv:2212.03533](https://arxiv.org/abs/2212.03533) | `multilingual-e5-large` 계열. Contrastive pair 설계 직관 | ★★ |
| **Dense Passage Retrieval** (Karpukhin et al.) | [arXiv:2004.04906](https://arxiv.org/abs/2004.04906) | dual-encoder + hard negative. PatternEmbed **positive/negative 샘플링** 원형 | ★★ |
| **CodeRAG-Bench: Can Retrieval Augment Code Generation?** (Wang et al.) | [arXiv:2406.14497](https://arxiv.org/abs/2406.14497) | 코드 도메인 RAG 한계·벤치 설계. **문서/코드 RAG vs 사용패턴 RAG** 차별 문장 작성용 | ★★ |
| **Improving Efficient Neural Ranking Models with Cross-Encoders** (rerank 계열, 선택) | 검색 후 cross-encoder re-rank | Hit@3 부족 시 Phase 2 옵션 | ★ |

**PatternEmbed 실험 설계에 옮길 것**  
- Query: 개발자 코칭 질문 (자연어)  
- Doc: 우수 세션 **요약 + pattern_tags** (원문 전체 X)  
- Positive: `exemplar_quality` / `exemplar_efficient`  
- Hard negative: `retry_loop`, `waste_context` 등  
- 지표: Hit@3, MRR (골드 30~50 쿼리)

---

## 4. 코딩 어시스턴트 · 생산성 · Human–AI SE (★★★ ~ ★★)

> 문제 정의·경영 기여·파일럿 설문 설계

| 논문 | 링크 | 왜 읽나 | 깊이 |
|------|------|---------|:----:|
| **Peng et al. Copilot RCT** (필수) | [2302.06590](https://arxiv.org/abs/2302.06590) | 통제 실험, 완료 시간. “활용이 생산성에 영향” 서론 | ★★★ |
| **Ziegler et al. CACM** (필수) | [CACM](https://cacm.acm.org/research/measuring-github-copilots-impact-on-productivity/) | 지각된 생산성 vs 로그 지표 괴리 — **설문만 믿지 말 것** | ★★★ |
| **Expectation vs. Experience** (Vaithilingam et al., CHI EA 2022) | [DOI](https://doi.org/10.1145/3491101.3519665) / ACM | 코드 생성 도구 **기대–경험 갭**. 코칭 UX 실패 모드 | ★★ |
| **Code with Me or for Me? How Developers Use Generative AI** (관련 HCI/SE 설문 계열) | 논문 제안서 Related Work 키워드로 검색 | 자동화 vs **협업·코칭** 포지션 | ★★ |
| **SWE-bench** (Jimenez et al.) | [arXiv:2310.06770](https://arxiv.org/abs/2310.06770) | 리포 수준 코딩 벤치. **우리는 코드 생성 SOTA가 아님** — 벤치 인용 시 범위 제한 명시 | ★☆ |

**파일럿 설계 팁 (Ziegler·Peng에서 가져올 것)**  
- 유용도 Likert + pairwise 선호 (C0 vs C1)  
- (탐색) 동일 태스크 유형 평균 토큰 전후 비교  
- n 작으면 유의성보다 **효과 크기 + CI** 솔직히 보고

---

## 5. 비용·라우팅·토큰 효율 (★★)

> BudgetCoach, 월 ~$180, 저토큰 우수 사례

| 논문 | 링크 | 왜 읽나 | 깊이 |
|------|------|---------|:----:|
| **Cascade Routing** (Dekoninck et al., 필수) | [2403.12033](https://arxiv.org/abs/2403.12033) | routing vs cascade 통합 프레임. 비용–품질 Pareto | ★★★ |
| **FrugalGPT / LLM cascade** 계열 (Chen et al. 등) | [arXiv:2305.05176](https://arxiv.org/abs/2305.05176) (FrugalGPT) | 저가 모델 우선 → escalate. “예산 70%일 때 전략” 서사 | ★★ |
| **Large Language Model Cascades with Mixture of Thoughts** (Yue et al.) | [arXiv:2310.03094](https://arxiv.org/abs/2310.03094) | 약한 모델 일관성으로 난이도 추정. 개념만 | ★ |
| **RouteLLM** 등 오픈 라우터 (선택) | 프로젝트 페이지/논문 검색 | 운영 라우팅은 Phase 2+; Related Work 1문단 | ★ |

**중요**: MVP의 BudgetCoach는 **모델 라우터가 아니라**  
“유사 태스크 **저토큰 우수 세션 검색** + 컨텍스트 축소·작업 분할 권고”이다.  
라우팅 논문은 **비용 인식 코칭의 동기**로만 인용.

---

## 6. SFT · 정렬 · 평가 방법 (★★)

> CoachModel LoRA, 골드 30쌍, A/B vs DS 베이스

| 논문 | 링크 | 왜 읽나 | 깊이 |
|------|------|---------|:----:|
| **LoRA** (필수) | [2106.09685](https://arxiv.org/abs/2106.09685) | 파라미터 효율 FT | ★★★ |
| **QLoRA** (Dettmers et al.) | [arXiv:2305.14314](https://arxiv.org/abs/2305.14314) | 7B on limited GPU. AI 포털 PoC 실무 | ★★ |
| **InstructGPT** (Ouyang et al.) | [arXiv:2203.02155](https://arxiv.org/abs/2203.02155) | SFT + preference. 코칭 데이터 품질 > 양 | ★★ |
| **Self-Instruct** (Wang et al.) | [arXiv:2212.10560](https://arxiv.org/abs/2212.10560) | 시드 소수 → 확장. 골드 30쌍 부트스트랩 아이디어 | ★ |
| **DPO** (Rafailov et al.) | [arXiv:2305.18290](https://arxiv.org/abs/2305.18290) | Phase 2 HITL 선호 정렬 (기획서 §14) | ★ (Phase 2) |

**SFT 데이터 품질 원칙 (InstructGPT 교훈)**  
- 200~500 우수 세션 라벨 중 **코칭 쌍으로 쓸 수 있는 것만** 변환  
- (질문, 맥락, 예산상태) → (요약된 패턴 3개 + 팁 + 출처 ID)  
- 원문 대화 전체를 그대로 SFT하지 말 것 (PII·노이즈)

---

## 7. Tool-use · Coding Agent 맥락 (★ ~ ★★, 배경)

> 차별화: 우리는 새 에이전트를 만들지 않음. Claude Code **사용 로그**를 다룸.

| 논문 | 링크 | 왜 읽나 | 깊이 |
|------|------|---------|:----:|
| **ReAct** (Yao et al.) | [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) | thought–act–observe. 세션 품질 신호(계획→도구→검증) 루브릭 근거 | ★★ |
| **Toolformer** (Schick et al.) | [arXiv:2302.04761](https://arxiv.org/abs/2302.04761) | 도구 호출 학습. MCP 사용 패턴 라벨 영감 | ★ |
| **SWE-agent / OpenHands** 등 최근 서베이 1편 | 최신 서베이 검색 | Related Work “Coding Agent” 1문단용 | ★ |

세션 품질 루브릭에 쓸 수 있는 **ReAct 정렬 휴리스틱**  
- 목표 명시(thought) → 파일/검색(act) → 결과 확인(observe) → 수정 → 검증  
- 이 흐름이 깨진 세션 = hard_negative 후보

---

## 8. 논문 제안서 RQ ↔ 읽을 논문 매핑

| RQ | 읽을 논문 | 우리 실험에 가져올 것 |
|----|-----------|----------------------|
| **RQ1** 패턴 검색이 유용한 exemplar인가? | RAG, DPR, BGE-M3, CodeRAG-Bench, ExpeL, Voyager | Hit@3/MRR, query–doc 형식, hard negative |
| **RQ2** RAG 코칭 > base LLM? | RAG, InstructGPT, Peng/Ziegler | C0/C1 pairwise, Likert, 블라인드 |
| **RQ3** 예산 맥락이 인식 변화? | Cascade/FrugalGPT, Budget 시나리오 설계 | B0/B1 조건, “절약 도움” 문항 |
| **RQ4** 토큰 감소? (탐색) | Ziegler(로그 지표), Peng(생산성) | 전후 집계, 인과 주장 자제 |

---

## 9. Anti-reading — 지금은 깊게 안 읽어도 되는 것

범위 creep·시간 낭비를 막기 위한 목록.

| 피하거나 얕게 | 이유 |
|---------------|------|
| HumanEval/MBPP SOTA 경쟁 논문 다수 | 과제 목표가 코드 생성 성능이 아님 |
| 새 Multi-agent orchestration 아키텍처 | MVP는 검색+코칭, Agent 플랫폼 아님 |
| Full RLHF/PPO 구현 논문 심화 | Phase 2 DPO 전까지만 개념 |
| Text-to-SQL / 대시보드 NL2SQL 전체 | Phase 2, 기획에서 제외 |
| 순수 비전·멀티모달 코딩 | 범위 밖 |

---

## 10. 추천 독서 일정 (Phase 0·1)

### Week A (2~3일) — 문제·포지션 고정
1. Peng et al. (Copilot RCT) — 초록+실험 설계  
2. Ziegler et al. (CACM) — 지표·설문  
3. ExpeL — insight 추출 파이프라인  
4. Voyager — skill library + retrieval (Figure 위주)

### Week B (2~3일) — 방법 스택
5. RAG (Lewis) — 구조  
6. BGE-M3 — 모델 카드 + 논문 §method  
7. DPR 또는 E5 — contrastive pair  
8. LoRA (+ 필요 시 QLoRA 1절)

### Week C (1~2일) — 예산·평가
9. Cascade Routing 또는 FrugalGPT  
10. CodeRAG-Bench — “우리 RAG는 코드가 아니라 **사용 패턴**” 문장 작성  
11. 라벨 가이드 v0 초안 작성 (우수 세션 정의 반영)

### 산출물 (읽기와 동시에)
- [ ] Related Work 초안 1.5p (트렌드 표 6행)  
- [ ] 우수 세션 루브릭 v0 (quality + efficiency)  
- [ ] 검색 벤치 쿼리 30개 초안  
- [ ] 코칭 골드 템플릿 5쌍 샘플

---

## 11. BibTeX 시드 (초안용)

```bibtex
@inproceedings{lewis2020rag,
  title={Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks},
  author={Lewis, Patrick and others},
  booktitle={NeurIPS},
  year={2020}
}

@inproceedings{zhao2024expel,
  title={ExpeL: LLM Agents are Experiential Learners},
  author={Zhao, Andrew and others},
  booktitle={AAAI},
  year={2024}
}

@article{wang2023voyager,
  title={Voyager: An Open-Ended Embodied Agent with Large Language Models},
  author={Wang, Guanzhi and others},
  journal={arXiv:2305.16291},
  year={2023}
}

@article{peng2023copilot,
  title={The Impact of AI on Developer Productivity: Evidence from GitHub Copilot},
  author={Peng, Sida and Kalliamvakou, Eirini and Cihon, Peter and Demirer, Mert},
  journal={arXiv:2302.06590},
  year={2023}
}

@article{chen2024bgem3,
  title={BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation},
  author={Chen, Jianlv and others},
  journal={arXiv:2402.03216},
  year={2024}
}

@inproceedings{hu2022lora,
  title={LoRA: Low-Rank Adaptation of Large Language Models},
  author={Hu, Edward J. and others},
  booktitle={ICLR},
  year={2022}
}

@article{dekoninck2024cascade,
  title={A Unified Approach to Routing and Cascading for LLMs},
  author={Dekoninck, Jasper and Baader, Maximilian and Vechev, Martin},
  journal={arXiv:2403.12033},
  year={2024}
}

@article{shinn2023reflexion,
  title={Reflexion: Language Agents with Verbal Reinforcement Learning},
  author={Shinn, Noah and others},
  journal={arXiv:2303.11366},
  year={2023}
}

@inproceedings{karpukhin2020dpr,
  title={Dense Passage Retrieval for Open-Domain Question Answering},
  author={Karpukhin, Vladimir and others},
  booktitle={EMNLP},
  year={2020}
}

@article{wang2022e5,
  title={Text Embeddings by Weakly-Supervised Contrastive Pre-training},
  author={Wang, Liang and others},
  journal={arXiv:2212.03533},
  year={2022}
}
```

---

## 12. 폴더 구조 (권장)

```
project/thesis/
  README.md                 ← 본 문서 (리딩 맵)
  notes/                    ← 논문별 1페이지 메모 (선택)
    01_rag_lewis.md
    02_expel.md
    ...
  related_work_draft.md     ← 논문 §2 초안 (작성 시)
```

논문 한 편을 다 읽으면 `notes/`에 다음 템플릿으로 남기면 좋다.

```markdown
# [논문명]
- 한 줄 요약:
- 좋은 경험/결과 정의:
- 검색·메모리 단위:
- 평가 지표:
- ClaudeCoach 연결 (라벨 / Embed / SFT / Budget / 평가):
- 우리와의 차이 1문장:
- 인용할 문장/표:
```

---

## 13. 관련 내부 문서

| 문서 | 역할 |
|------|------|
| `../proposal(260707).md` | 과제 본체 (ClaudeCoach) |
| `../논문_제안서_ClaudeCoach.md` | RQ·ablation·투고 전략 |
| `../CLAUDE.md` | 교육·지도교수·후보 과제 맥락 |
| (작성 예정) 우수 세션 라벨 가이드 v0 | 본 리스트 §2·§7과 동기화 |

---

*작성 기준: ClaudeCoach MVP(로그 라벨 → PatternEmbed → 코칭 RAG/SFT → BudgetCoach).  
새 Agent SOTA 추적은 의도적으로 최소화함.*
