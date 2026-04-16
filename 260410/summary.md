# 2026년 4월 10일 강의 요약

## 1. 오전 강의: 인공지능의 기초 및 머신러닝의 핵심 개념

### 인공지능의 정의 및 역사
* **AI의 정의**: 인간처럼 생각하거나 행동하는 합리적(Rational)인 기계를 만드는 것.
* **세대별 발전**:
    * **1세대 (Rule-based)**: 규칙 기반 시스템. 데이터 없이 규칙만으로 동작하지만 예외 상황에 취약함.
    * **2세대 (Machine Learning)**: 데이터 기반 학습. 사람이 직접 특징(Feature)을 추출하여 학습시키는 방식.
    * **3세대 (Deep Learning)**: 표현 학습(Representation Learning). 기계가 데이터로부터 스스로 특징을 추출함 (다단계 구조).

### 머신러닝의 핵심 개념
* **일반화 (Generalization)**: 학습 시 보지 못한 데이터(Unseen Data)에 대해 얼마나 잘 동작하는지를 의미하며, 머신러닝의 궁극적인 목표임.
* **과적합(Overfitting) vs 과소적합(Underfitting)**:
    * **과적합**: 모델이 너무 복잡하여 학습 데이터의 노이즈까지 학습해버린 상태. 일반화 성능이 낮음.
    * **과소적합**: 모델이 너무 단순하여 데이터의 패턴을 충분히 학습하지 못한 상태.
* **데이터 분할**:
    * **Training Set**: 파라미터 학습용.
    * **Validation (Dev) Set**: 하이퍼파라미터 튜닝 및 모델 선택용.
    * **Test Set**: 최종 모델의 일반화 성능 측정용 (금고에 보관하듯 엄격히 관리).

---

## 2. 오후 강의: 최적화 및 규제화 (Optimization & Regularization)

### 최적화 (Optimization)
* **경사 하강법(Gradient Descent)**의 변형들:
    * **Momentum**: 관성을 이용하여 진동을 줄이고 빠르게 수렴.
    * **RMS-Prop**: 학습률(Learning Rate)을 적응적으로 조절.
    * **Adam**: Momentum과 RMS-Prop의 장점을 결합한 현재 가장 널리 쓰이는 알고리즘.
* **Learning Rate Scheduling**: 초기에는 크게, 나중에는 작게 조절하거나 Warm-up 기법을 사용함.

### 규제화 (Regularization)
* **목적**: 모델의 복잡도를 제한하여 과적합을 방지하고 일반화 성능을 향상시킴.
* **주요 기법**:
    * **L1 (Lasso)**: 가중치의 절대값 합을 페널티로 부여. 가중치를 0으로 만들어 특징 선택 효과(Sparsity)가 있음.
    * **L2 (Ridge/Weight Decay)**: 가중치의 제곱 합을 페널티로 부여. 가중치를 작게 만들어 부드러운 모델을 생성.
    * **Early Stopping**: 검증 에러(Validation Error)가 증가하기 시작할 때 학습을 중단.
    * **Dropout**: 학습 중에 무작위로 뉴런을 비활성화하여 특정 뉴런에 의존하지 않는 강인한 네트워크 학습.

### 현대적 관점: Double Descent
* 전통적인 이론과 달리, 모델의 복잡도가 특정 임계치를 넘어서면 다시 일반화 에러가 감소하는 현상으로, 거대 모델(Deep Learning)이 잘 동작하는 이론적 근거 중 하나임.

---

## 3. 실습 (Lab)
* **PyTorch 기초**: Tensor 조작, GPU(CUDA) 연동 및 시드(Seed) 고정 방법.
* **구현 과제**:
    * **Softmax**: 수치적 안정성(Numerical Stability)을 고려한 구현.
    * **Cross Entropy Loss**: 수식을 코드로 변환 및 PyTorch 내장 함수와의 비교.
    * **Linear Classifier**: CIFAR-10 데이터를 이용한 선형 분류기 구성 및 학습 루틴 이해.
