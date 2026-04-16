# 260413 강의 요약

## 1. 머신러닝 기초 및 일반화 (오전)
*   **데이터 분할**: 데이터를 트레이닝(Training), 밸리데이션(Validation), 테스트(Test) 세트로 나누는 목적과 중요성 학습.
*   **일반화(Generalization)와 근사(Approximation)**:
    *   **Overfitting (과적합)**: 모델이 복잡하여 노이즈까지 학습하는 현상 (High Variance).
    *   **Underfitting (과소적합)**: 모델이 너무 단순하여 데이터의 패턴을 파악하지 못하는 현상 (High Bias).
    *   **Bias-Variance Trade-off**: 편향과 분산 사이의 균형을 맞추는 것이 핵심.
*   **규제화 (Regularization)**: 
    *   L1, L2 Norm Penalty 등을 통해 모델의 복잡도를 제어하고 과적합을 방지.
    *   Augmented Error ($E_{aug} = E_{train} + \lambda \Omega(w)$) 개념 이해.

## 2. MLP (Multi-Layer Perceptron) 구조 (오전)
*   **뉴런 모델링**: 가중합(Weighted Sum, Linear)과 활성화 함수(Activation Function, Nonlinear)의 결합.
*   **심층 신경망 구조**: 입력층(Input), 은닉층(Hidden), 출력층(Output)으로 구성된 계층적 구조.
*   **Fully Connected (FC) Layer**: 모든 이전 층의 뉴런이 다음 층의 모든 뉴런과 연결된 형태.
*   **활성화 함수**: Sigmoid, ReLU, Tanh 등의 역할과 특성.
*   **다른 모델과의 비교**: CNN(합성곱), RNN(재귀/피드백) 모델과의 구조적 차이점 서술.

## 3. 오차 역전파 및 실습 (오후)
*   **백프로파게이션 (Backpropagation)**:
    *   체인 룰(Chain Rule)을 이용한 그레디언트(Gradient) 계산 원리.
    *   컴퓨테이션 그래프(Computation Graph)를 통한 순전파(Forward)와 역전파(Backward) 과정 이해.
*   **NumPy를 이용한 직접 구현**:
    *   PyTorch 등 프레임워크를 쓰지 않고 NumPy만으로 Affine Layer(FC Layer)의 순전파와 역전파 직접 구현.
    *   캐시(Cache) 시스템: 역전파 시 필요한 중간값을 저장하여 계산 효율성 증대.
*   **PyTorch 활용**: NumPy 구현체와 PyTorch의 `autograd` 기능을 비교하며 실습.

## 4. 딥러닝 최적화 기법 (오후)
*   **그레디언트 소실 (Gradient Vanishing)**: 층이 깊어질수록 그레디언트가 작아져 학습이 안 되는 문제 확인 및 데이터 조작을 통한 재현.
*   **가중치 초기화 (Weight Initialization)**:
    *   **Xavier (Glorot) 초기화**: Sigmoid/Tanh 활성화 함수에 적합.
    *   **Kaiming (He) 초기화**: ReLU 활성화 함수에 적합.
*   **배치 정규화 (Batch Normalization)**: 학습 과정을 안정화하고 속도를 높이기 위한 기법 학습 및 구현.
