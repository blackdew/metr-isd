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

## 프로젝트 구조

```
metr-isd/
├── README.md                      # 이 파일
├── CLAUDE.md                      # Claude Code 작업 가이드
├── ISD_Bench_Proposal_v3.docx     # 연구 계획서 초안 (v3)
├── 2503.14499v3.pdf               # [Ref] METR - Measuring AI Ability to Complete Long Software Tasks
├── 2603.17187v1.pdf               # [Ref] MetaClaw - An Agent That Meta-Learns and Evolves in the Wild
└── MetaClaw/                      # MetaClaw 공식 레포 클론 (MIT License)
    ├── metaclaw/                  #   핵심 프레임워크 (proxy, skill, RL, memory)
    ├── benchmark/                 #   MetaClaw-Bench 평가 파이프라인
    ├── extensions/                #   OpenClaw 플러그인
    ├── openclaw-metaclaw-memory/  #   메모리 사이드카 서비스
    ├── scripts/                   #   실험 자동화 스크립트
    └── tests/                     #   테스트 코드
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
