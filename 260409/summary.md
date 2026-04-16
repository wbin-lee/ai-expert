# 260409 강의 요약 (4일차)

## 1. 트랜스포머 (Transformer) 아키텍처
- **배경:** 기존 RNN의 정보 손실(Information Bottleneck) 및 병목 문제를 해결하기 위해 등장. "Attention Is All You Need" 논문을 통해 Attention 메커니즘만으로 시퀀스 데이터를 처리하는 구조 제안.
- **핵심 메커니즘 (Attention):**
    - **Query(Q), Key(K), Value(V):** 검색(Search)과 추출(Retrieval) 단계로 구성. Q와 K의 유사도를 점수화하고 이를 가중치로 하여 V를 합산.
    - **Self-Attention:** 입력 문장 내의 단어들끼리 서로의 연관성을 계산하여 문맥을 파악.
    - **Multi-Head Attention:** 여러 개의 어텐션을 병렬로 수행하여 다양한 관계(의미적, 문법적 등)를 포착.
    - **Positional Encoding:** 순차적 처리를 하지 않는 트랜스포머의 특성상, 단어의 위치 정보를 추가하기 위해 사인/코사인 함수 기반의 벡터를 더해줌.
- **구조:**
    - **Encoder:** 입력 문장을 이해하고 함축된 표현을 생성 (Self-Attention 사용).
    - **Decoder:** 인코더의 정보를 참고하여 출력 문장을 생성 (Masked Self-Attention 및 Cross-Attention 사용).

## 2. 주요 모델: BERT vs GPT
- **BERT (Bidirectional Encoder Representations from Transformers):**
    - 트랜스포머의 **인코더**만 사용.
    - **양방향(Bidirectional)** 문맥 파악에 유리.
    - Masked Language Modeling(MLM) 방식으로 학습 (빈칸 채우기).
    - 문맥 이해, 분류, 개체명 인식 등에 특화.
- **GPT (Generative Pre-trained Transformer):**
    - 트랜스포머의 **디코더**만 사용.
    - **일방향(Unidirectional)** 문맥 파악.
    - Next Token Prediction 방식으로 학습 (다음 단어 예측).
    - 텍스트 생성에 특화.

## 3. 거대 언어 모델 (LLM, Large Language Models)
- **스케일링 법칙 (Scaling Laws):** 모델 파라미터 수(N), 데이터 양(D), 계산량(C)이 증가함에 따라 모델의 성능이 예측 가능한 함수 형태로 향상됨을 확인. 특히 모델 크기를 키우는 것이 성능 향상에 매우 효율적임.
- **In-Context Learning:** 방대한 파라미터를 가진 모델은 별도의 미세 조정(Fine-tuning) 없이 몇 개의 예시(Few-shot)나 설명(Prompting)만으로도 새로운 태스크를 수행할 수 있음.
    - **Zero-shot:** 예시 없이 바로 질문.
    - **One-shot / Few-shot:** 하나 또는 소수의 예시를 제공하여 가이드.
- **디코딩 전략 (Decoding Strategies):**
    - **Greedy Search:** 가장 확률이 높은 단어만 선택 (단조로움).
    - **Sampling:** 확률 분포에 따라 랜덤하게 선택 (창의적이지만 위험함).
    - **Top-K / Top-P:** 상위 K개 또는 누적 확률 P 이내의 단어 중에서 선택하여 품질과 다양성을 조절.
    - **Temperature:** 확률 분포를 조절하여 결과의 무작위성(Randomness)을 제어.

## 4. 실습 주요 내용
- PyTorch를 이용한 Attention 수식의 코드 구현 (Matrix Multiplication).
- GPT-2 모델을 활용한 텍스트 생성 및 디코딩 전략별 결과 비교.
- 단어 임베딩의 유사도 분석 (Cosine Similarity) 및 시각화 (PCA).
- 프롬프트 엔지니어링을 통한 모델의 성능 변화 관찰.
