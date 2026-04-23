# OMNI-ABDUCE
옴니데이터 기반 귀추적 추론 시각화 미니앱

---

## Overview
OMNI-ABDUCE는 복합 관측 데이터로부터 가능한 원인을 추론하고, 그 과정을 인과 그래프로 시각화하는 귀추적(Abductive) 추론 기반 도구입니다.
간단한 확률 모델을 기반으로 다양한 원인 가설을 탐색하고, 가장 그럴듯한 설명을 도출하여 시각적으로 표현합니다.
본 프로그램은 인과 추론의 기본 원리를 이해하고 실험하기 위한 경량형 연구·교육용 환경을 제공합니다.

---

## Features
- 귀추적 추론 기반 가설 탐색
- 확률 기반 스코어링 (Likelihood + Prior)
- 인과 구조 시각화
- 결과 이미지 자동 생성 및 저장
- CLI 기반 실행
- 수정 및 확장이 용이한 구조

---

## Project Structure
```
OMNI-ABDUCE/
├── src/
│   └── src.py
```

---

## Installation
```bash
pip install matplotlib
```

---

## Usage
```bash
python src/src.py --alarm true --smoke true
```

옵션:
- `--alarm`: 관측 신호 (true/false)
- `--smoke`: 관측 신호 (true/false)
- `--out`: 결과 이미지 저장 경로

---

## How It Works
1. 가능한 원인 가설 생성
2. 각 가설에 대해 확률 점수 계산
3. 최적 가설 선택
4. 그래프로 시각화

---

## Output
- 인과 그래프 이미지 생성
- 최상 가설 강조 표시
- PNG 파일 저장

---

## Customization
- PRIORS 수정
- CPTS 수정
- 그래프 구조 변경

---

## Use Cases
- 인과 추론 교육
- 설명 가능한 AI 시연
- 확률 기반 추론 실험

---

## License
MIT License
