# 2026년 4월 6일 강의 요약

## 오전: 인공지능 개요 및 역사, 철학적 배경
* **인공지능의 정의**: 사람처럼 생각하고 행동하는 기계, 또는 합리적으로 생각하고 행동하는 시스템(에이전트).
* **패러다임의 변화**: 기호주의(Symbolic AI, 규칙 기반) -> 연결주의(Connectionism, 신경망/학습 기반) -> 에이전트 및 물리적 AI(Physical AI).
* **역사적 주요 사건**: 1956년 다트머스 회의(AI 탄생), AI의 겨울(학습의 한계), 1997년 딥블루(체스 승리), 2012년 이미지넷 대회(딥러닝 혁명), 2016년 알파고.
* **철학적 논쟁**:
    * **기능주의(Functionalism)** vs **물리주의(Physicalism)**.
    * **중국어 방 논증(Chinese Room Argument)**: 기호 조작만으로는 진정한 의미 이해가 불가능하다는 존 설의 비판.
    * **강인공지능(Strong AI)** vs **약인공지능(Weak AI)** 및 **AGI(범용 인공지능)**.
    * **특이점(Singularity)**: 기계 지능이 인간 지능을 능가하는 시점.

## 오후: 지능형 에이전트, 탐색, 그리고 확률적 추론
* **지능형 에이전트**: 환경을 지각(Sensing)하고 액추에이터를 통해 행동(Action)하는 자율 시스템. PEAS(Performance, Environment, Actuators, Sensors) 프레임워크로 설계.
* **강화 학습(Reinforcement Learning)**: 시행착오를 통해 보상(Reward)을 최대화하는 정책(Policy)을 학습. MDP(Markov Decision Process)로 정형화.
* **알파고의 핵심 기술**: 딥러닝(정책망/가치망) + 몬테카를로 트리 탐색(MCTS).
* **탐색 알고리즘**:
    * **무정보 탐색**(너비 우선, 깊이 우선) vs **정보 탐색**(휴리스틱 이용).
    * **A* 알고리즘**: $f(n) = g(n) + h(n)$ 식을 사용하여 최적 경로를 효율적으로 탐색.
* **기호주의 AI와 지식 표현**:
    * **논리적 추론**: 명제 논리, 술어 논리, 전방 추론(Forward Chaining), 후방 추론(Backward Chaining).
    * **지식 구조**: 의미망(Semantic Networks), 프레임(Frames), 스크립트(Scripts).
* **확률적 추론(Bayesian Networks)**: 불확실성을 다루기 위한 확률 모델. 베이즈 정리(Bayes' Rule)를 이용하여 사전 확률(Prior)과 우도(Likelihood)를 결합해 사후 확률(Posterior)을 추론.
