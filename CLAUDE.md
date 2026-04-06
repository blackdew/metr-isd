# CLAUDE.md — ISD-Bench 프로젝트 작업 가이드

## 프로젝트 개요

ISD(교수설계) 도메인 특화 continual adaptation 벤치마크(ISD-Bench) 연구 프로젝트.
METR의 time horizon 프레임워크 + MetaClaw의 adaptation 메커니즘을 교육공학 도메인으로 확장.

## 핵심 파일

- `ISD_Bench_Proposal_v3.docx` — 연구 계획서 초안 (현재 v3)
- `2503.14499v3.pdf` — METR 참고 논문 (time horizon 메트릭)
- `2603.17187v1.pdf` — MetaClaw 참고 논문 (continual meta-learning)
- `MetaClaw/` — MetaClaw 공식 레포 클론

## 작업 시 주의사항

### 논문/제안서 관련
- docx 파일은 바이너리이므로 `textutil -convert txt -stdout` 또는 `python-docx`로 읽을 것
- PDF는 Read 도구의 `pages` 파라미터로 페이지 범위 지정하여 읽을 것
- 초안의 연구 질문은 RQ1~RQ4, 비교 조건은 C1~C5로 참조

### MetaClaw 레포 관련
- `MetaClaw/` 디렉토리는 외부 클론이므로 수정하지 말 것
- MetaClaw의 핵심 모듈:
  - `metaclaw/skill_manager.py` — 스킬 검색/주입
  - `metaclaw/skill_evolver.py` — 실패 trajectory에서 스킬 합성
  - `metaclaw/trainer.py` — GRPO RL 훈련 루프
  - `metaclaw/scheduler.py` — OMLS 유휴 시간 스케줄러
  - `metaclaw/memory/` — 장기 메모리 시스템 (v0.4.0 추가, 논문 미포함)
  - `benchmark/` — MetaClaw-Bench 평가 파이프라인 (check→infer→score→report)

### 비교 조건 빠른 참조
| 조건 | 방법 | inference 모델 | 훈련 |
|------|------|---------------|------|
| C1 | Baseline | GPT-5.4 / Kimi-K2.5 | 없음 |
| C2 | Reflexion | GPT-5.4 / Kimi-K2.5 | 없음 |
| C3 | ExpeL | GPT-5.4 / Kimi-K2.5 | 없음 |
| C4 | MetaClaw Skills | GPT-5.4 / Kimi-K2.5 | 없음 |
| C5 | OpenClaw-RL | Qwen3-30B-A3B | GRPO+LoRA (Tinker) |

## 코드 작성 시

- 이 프로젝트는 현재 연구 설계 단계이므로 구현 코드는 아직 없음
- 벤치마크 코드 작성 시 MetaClaw의 `benchmark/` 구조를 참고
- Python 3.10+ 기준
