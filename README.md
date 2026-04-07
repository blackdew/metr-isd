# ISD-Bench

**Instructional Systems Design Benchmark for Continual Adaptation AI Agents**

ISD 도메인에서 AI 에이전트의 continual adaptation 능력을 측정하는 벤치마크 구축 및 인간 ISD 전문가와의 종단 비교 연구 프로젝트.

## 연구 목적

1. ISD 도메인 특화 continual adaptation 벤치마크 (ISD-Bench) 구축 및 공개
2. 복수의 LLM adaptation 방법론을 동일 벤치마크에서 비교
3. 15주 종단 연구에서 인간 ISD 전문가 팀과 AI 에이전트의 산출물 품질 비교
4. Skill 축적에 따른 인간-AI 성능 격차 변화 추적

## 연구 질문

| ID | 질문 |
|----|------|
| RQ1 | ISD-Bench에서 adaptation 방법론 간 성능 차이는 어떠하며, 어떤 방법이 가장 효과적인가? |
| RQ2 | 15주 종단 프로젝트에서 최고 성능 에이전트는 인간 ISD 전문가 팀 대비 어느 수준인가? |
| RQ3 | 주차 누적에 따라 skill-driven adaptation 에이전트와 인간의 성능 격차가 감소하는가? |
| RQ4 | ISD 맥락에서 에이전트가 합성하는 behavioral skill의 유형과 일반화 가능성은? |

## 비교 대상 방법론 (5개 조건)

| 조건 | 방법 | 모델 | 훈련 |
|------|------|------|------|
| C1 | Baseline (no adaptation) | GPT-5.4 / Kimi-K2.5 | 없음 |
| C2 | Reflexion (verbal self-reflection) | GPT-5.4 / Kimi-K2.5 | 없음 |
| C3 | ExpeL (experiential learning) | GPT-5.4 / Kimi-K2.5 | 없음 |
| C4 | MetaClaw Skills (skill-driven fast adaptation) | GPT-5.4 / Kimi-K2.5 | 없음 |
| C5 | OpenClaw-RL (GRPO+LoRA) | Qwen3-30B-A3B | Tinker 클라우드 |

## 파일럿 실험 결과 요약

Gemini 2.5 Pro + MetaClaw skills_only 모드로 Week 1~3 ISD 태스크 파일럿 완료.

| 조건 | Week 1 | Week 2 | Week 3 | 평균 |
|------|:------:|:------:|:------:|:----:|
| Baseline (skill 없음) | 17/25 | 22/25 | 24/25 | 21.0 |
| Skills (seed skill 5개 주입) | 20/25 | 22/25 | 24/25 | 22.0 |
| **차이** | **+3** | **0** | **0** | **+1.0** |

- Skill 효과는 **구조화된 초반 태스크(Week 1)**에서 가장 큼 (내용 완전성 +0.3, 실용성 +0.7)
- Week 2~3에서는 **이전 산출물 체이닝**이 skill보다 품질에 더 큰 영향
- 평가: Claude 독립 평가 (Gemini 자기 평가는 전원 만점 → 자기 평가 편향 확인)

상세: [`docs/pilot-experiment-results.md`](docs/pilot-experiment-results.md)

## 프로젝트 구조

```
metr-isd/
├── README.md                      # 이 파일
├── CLAUDE.md                      # Claude Code 작업 가이드
├── ISD_Bench_Proposal_v3.docx     # 연구 계획서 초안 (v3)
├── 2503.14499v3.pdf               # [Ref] METR - Measuring AI Ability to Complete Long Software Tasks
├── 2603.17187v1.pdf               # [Ref] MetaClaw - An Agent That Meta-Learns and Evolves in the Wild
├── docs/                          # 실험 설계/결과 문서
│   ├── pilot-experiment-design.md #   파일럿 실험 설계서
│   ├── pilot-experiment-results.md    # 파일럿 최종 결과 보고서
│   ├── metaclaw-pilot-report.md   #   MetaClaw 실행 가능성 검증
│   └── evaluation-rubric.md       #   ISD 평가 루브릭 (5기준 × 5점)
├── experiments/pilot/             # 파일럿 실험 코드 및 데이터
│   ├── tasks.py                   #   ISD 태스크 프롬프트 정의
│   ├── run_experiment_v2.py       #   실험 러너 (Gemini 직접 호출)
│   ├── evaluate_v2.py             #   LLM-as-judge 평가 스크립트
│   └── results_v2/                #   실험 결과 JSON 데이터
└── MetaClaw/                      # MetaClaw 공식 레포 클론 (MIT, .gitignore)
```

## 참고 논문

### METR (arXiv:2503.14499v3)
- **제목**: Measuring AI Ability to Complete Long Software Tasks
- **핵심**: Task completion time horizon 메트릭 제안. 50% time horizon이 ~7개월마다 2배 성장.
- **본 연구와의 관계**: time horizon 프레임워크를 ISD 도메인으로 확장. Phase 2 human baselining 방법론 차용.

### MetaClaw (arXiv:2603.17187v1)
- **제목**: Just Talk — An Agent That Meta-Learns and Evolves in the Wild
- **핵심**: Skill-driven fast adaptation + Opportunistic policy optimization의 two-timescale continual meta-learning.
- **본 연구와의 관계**: C4 조건에서 skill-driven adaptation 직접 채용. 논문의 한계(CLI 한정, 인간 데이터 부재)를 보완.
- **GitHub**: https://github.com/aiming-lab/MetaClaw (MIT License)

## 벤치마크 설계 개요

- **구조**: 15주 × 주당 3-5개 태스크 (ADDIE/Dick & Carey 절차 기반)
- **시나리오**: 3개 가상 교수설계 맥락 × 3개 학습자 프로파일 = 9개 시나리오
- **평가**: Part A (명시적 루브릭, 자동 채점) + Part B (암묵적 맥락 추론, 전문가 평가)
- **평가자**: ISD 전문가 3인 체제 (Spearman-Brown 기반 ICC≥0.875 확보)
