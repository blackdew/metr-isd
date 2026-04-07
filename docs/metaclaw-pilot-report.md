# MetaClaw 파일럿 실행 보고서

**작성일**: 2026-04-07  
**목적**: ISD-Bench 연구를 위한 MetaClaw 프레임워크 실행 가능성 검증

---

## 1. 실행 개요

| 항목 | 내용 |
|------|------|
| MetaClaw 버전 | v0.4.1.2 |
| 실행 모드 | `skills_only` (RL 훈련 없이 skill 주입만) |
| LLM 프로바이더 | Gemini (OAuth 토큰 방식) |
| LLM 모델 | gemini-2.5-pro |
| 프록시 주소 | `http://localhost:30000` |
| Python 환경 | 3.13.12 (arm64, venv) |

---

## 2. 설치 과정에서 확인된 이슈

### 2.1 Python 버전 호환성

| Python 버전 | 아키텍처 | torch 설치 | MetaClaw 실행 |
|-------------|---------|-----------|--------------|
| 3.14.2 | arm64 | 미지원 (배포 없음) | 실패 |
| 3.13.11 | x86_64 (Rosetta) | 미지원 (arm64만 배포) | 실패 |
| **3.13.12** | **arm64** | **CPU-only 설치 성공** | **성공** |

**핵심 발견**: MetaClaw는 `data_formatter.py`에서 torch를 top-level import하므로, `skills_only` 모드에서도 torch가 필수. Python 3.14는 아직 torch 미지원이라 3.13 arm64가 최소 요구사항.

### 2.2 의존성 구조

```
skills_only 모드 최소 의존성:
├── torch (data_formatter.py의 top-level import로 인해 필수)
├── fastapi + uvicorn (프록시 서버)
├── httpx (LLM API 호출)
├── tiktoken (토크나이저)
├── openai (skill evolver용, 선택)
└── pyyaml + click (설정/CLI)
```

**ISD-Bench 시사점**: C4 조건(MetaClaw Skills) 실험 환경 구축 시, torch CPU-only 설치가 필요함을 사전에 고려해야 함. 향후 MetaClaw에 lazy import PR을 제출하면 skills_only 모드에서 torch 의존성을 제거할 수 있음.

### 2.3 Gemini OAuth 연동

Gemini CLI(`~/.gemini/oauth_creds.json`)의 `access_token`을 MetaClaw에 수동 등록하여 연동 성공.

**주의사항**:
- OAuth access_token은 만료 시간이 있음 (`expiry_date` 필드)
- 장시간 실험 시 토큰 갱신 메커니즘이 필요할 수 있음
- `refresh_token`을 활용한 자동 갱신은 MetaClaw가 현재 미지원

---

## 3. 지원 LLM 프로바이더 조사

### 3.1 API Key 방식 (7개)

| 프로바이더 | 기본 모델 | Input $/M tok | Output $/M tok |
|-----------|----------|--------------|----------------|
| Qwen | qwen-plus | ~$0.004 | ~$0.012 |
| Kimi | Kimi-K2.5 | $0.60 | $2.50 |
| OpenAI | gpt-4o | $2.50 | $10.00 |
| MiniMax | (설정 필요) | 모델별 상이 | 모델별 상이 |
| Novita | (설정 필요) | 모델별 상이 | 모델별 상이 |
| OpenRouter | (설정 필요) | 모델별 상이 | 모델별 상이 |
| Volcengine | doubao-seed-2.0 | 미공개 | 미공개 |

### 3.2 OAuth Token 방식 (3개)

| 프로바이더 | 기본 모델 | Input $/M tok | Output $/M tok |
|-----------|----------|--------------|----------------|
| Anthropic | claude-sonnet-4-6 | $3.00 | $15.00 |
| OpenAI Codex | codex-mini | 미공개 | 미공개 |
| Gemini | gemini-2.5-pro | $1.25 | $10.00 |

### 3.3 ISD-Bench 실험 비용 추정

초안의 C1~C4 조건은 GPT-5.4 / Kimi-K2.5를 사용 예정. 15주 × 주당 3~5 태스크 × 9 시나리오 = 약 405~675 태스크.

각 태스크가 평균 ~5,000 input tokens + ~2,000 output tokens를 소비한다고 가정:
- **Kimi-K2.5**: 675 × (5K×$0.60 + 2K×$2.50) / 1M ≈ **$5.40** (매우 저렴)
- **GPT-5.4**: 가격 미공개 (GPT-4o 기준 추정 시 ~$22)
- **Gemini 2.5 Pro**: 675 × (5K×$1.25 + 2K×$10.00) / 1M ≈ **$17.70**

---

## 4. 테스트 실행 및 결과 분석

### 4.1 테스트 1: 단순 연산 (baseline)

**입력**: `"안녕하세요. 간단한 테스트입니다. 1+1은?"`

**응답**:
```json
{
  "model": "gemini-2.5-pro",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "2입니다. 무엇을 도와드릴까요?"
    },
    "finish_reason": "stop"
  }],
  "session_id": "tui-gemini-2.5-pro"
}
```

**분석**:
- 프록시 경유 정상 동작 확인
- `session_id` 필드가 자동 생성됨 → MetaClaw가 세션 단위로 대화를 추적
- `usage` 필드의 토큰 수가 0으로 표시됨 → Gemini OAuth 경로에서 토큰 사용량 미보고 가능성

### 4.2 테스트 2: ISD 도메인 질문

**입력**: `"교수설계(Instructional Systems Design)에서 학습자 분석의 핵심 요소 3가지를 간단히 설명해주세요."`

**응답** (전문):
```
교수설계(ISD)에서 학습자 분석의 핵심 3요소는 다음과 같습니다.

1. 사전 지식 (Prior Knowledge) / 출발점 행동 (Entry Behaviors)
   학습자가 교육을 받기 전에 이미 알고 있는 지식, 기술, 경험이 어느 정도인지를
   파악하는 것입니다. 이를 통해 교육 내용의 난이도와 시작점을 결정할 수 있습니다.

2. 학습 동기 및 태도 (Motivation and Attitude)
   학습자가 해당 교육에 대해 얼마나 흥미를 느끼고 필요성을 인식하는지, 그리고
   교육 내용에 대해 어떤 태도(긍정적, 부정적)를 가지고 있는지를 분석합니다.
   동기 수준은 학습 참여도와 성과에 직접적인 영향을 미칩니다.

3. 일반적 특성 (General Characteristics)
   학습자의 연령, 직업, 문화적 배경, 학습 스타일 등 인구통계학적, 사회적 특성을
   의미합니다. 이러한 특성은 교육에 사용될 예시, 언어, 전달 매체 등을 학습자에게
   맞게 조절하는 데 중요한 정보가 됩니다.
```

**ISD 전문성 분석**:

| 평가 기준 | 점수 (5점 만점) | 비고 |
|----------|:---:|------|
| ISD 용어 정확성 | 4 | "출발점 행동(Entry Behaviors)" 등 Dick & Carey 용어 정확히 사용 |
| 내용 완전성 | 3 | 핵심 3요소를 잘 선별했으나, "학습 환경/맥락 분석"이 누락 |
| 교수설계 모형 정합성 | 4 | Dick & Carey 모형의 학습자 분석 단계와 잘 부합 |
| 실용적 적용 가능성 | 3 | 개념 설명은 정확하나, 구체적 분석 방법이나 도구 언급 없음 |

**ISD-Bench 시사점**:
- Gemini 2.5 Pro가 ISD 기본 개념에 대해 상당한 수준의 응답 가능
- 그러나 초안의 Week 1 태스크("학습자 분석")에서 요구하는 **구체적 학습자 프로파일 작성**, **데이터 수집 도구 설계** 등 실무 수준의 산출물 생성 능력은 별도 검증 필요
- skill이 축적되지 않은 baseline 상태에서의 응답이므로, skill 주입 후 품질 변화를 비교하는 것이 중요

---

## 5. MetaClaw 아키텍처 핵심 발견

### 5.1 레포 구조 요약 (v0.4.1.2)

```
MetaClaw/
├── metaclaw/                    # 핵심 프레임워크 (28개 모듈)
│   ├── cli.py (177KB)          # CLI 엔트리포인트
│   ├── api_server.py (113KB)   # FastAPI 프록시 (skill 주입 + 대화 수집)
│   ├── skill_manager.py (24KB) # 스킬 검색/주입 (template/embedding 2모드)
│   ├── skill_evolver.py (17KB) # 실패에서 스킬 합성 (LLM 기반)
│   ├── trainer.py (28KB)       # GRPO RL 훈련 루프
│   ├── scheduler.py (10KB)     # OMLS 유휴 시간 스케줄러
│   ├── data_formatter.py (8KB) # ConversationSample → Datum 변환
│   ├── prm_scorer.py (8KB)     # Process Reward Model 채점
│   └── memory/ (21파일, 388KB) # 장기 메모리 (논문 미포함, v0.4.0 추가)
├── benchmark/                   # MetaClaw-Bench 평가 파이프라인
│   ├── data/                   # 벤치마크 데이터셋
│   ├── src/cli.py              # check → infer → score → report
│   └── scripts/                # 실험별 러너 (baseline, skills, rl 등)
├── extensions/                  # OpenClaw 플러그인
├── openclaw-metaclaw-memory/    # 메모리 사이드카 (HTTP 서비스)
└── tests/ (529+ 테스트)         # 주로 메모리 시스템 집중 커버리지
```

### 5.2 논문 vs 실제 구현 차이

| 항목 | 논문 (arXiv:2603.17187) | 실제 구현 (v0.4.1.2) |
|------|------------------------|---------------------|
| Memory 시스템 | 미언급 | SQLite+FTS5 기반 6종 메모리 + self-evolving policy |
| Skill 검색 | embedding 기반 | template(키워드) + embedding 2모드 선택 |
| RL 백엔드 | Tinker만 언급 | Tinker + MinT + Weaver 지원 |
| 에이전트 연동 | OpenClaw만 | 8종 에이전트 지원 (OpenClaw, CoPaw, IronClaw 등) |
| OAuth 인증 | 미언급 | Anthropic, OpenAI Codex, Gemini CLI 지원 |

**ISD-Bench 시사점**: 논문에 없는 Memory 시스템(v0.4.0)을 초안 실험에 포함할지 결정 필요. 포함 시 새로운 비교 조건(예: C4b: MetaClaw Skills + Memory)이 추가될 수 있음.

### 5.3 Skill 시스템 상세

**Skill 저장 형식** (`SKILL.md`, YAML frontmatter + Markdown):
```yaml
---
name: verify-file-before-modify
description: Always verify file exists before modifying
category: common_mistakes
---
Before modifying any file, verify it exists and read its contents...
```

**Skill 카테고리**: general, coding, research, data_analysis, productivity, security, communication, automation, agentic, common_mistakes

**현재 상태**: skills 디렉토리가 비어 있음 (0개). ISD 도메인 특화 seed skill을 사전 작성하여 주입하면 baseline 성능을 높일 수 있음.

### 5.4 Benchmark 파이프라인

MetaClaw-Bench의 평가 흐름:
```
check (데이터 무결성 8종 검증)
  → infer (에이전트에 태스크 전달)
    → score (정답 대비 채점)
      → report (accuracy + token usage 리포트)
```

ISD-Bench에서 차용 가능한 구조:
- `all_tests.json` 형태의 마스터 태스크 목록
- 주차(day)별 워크스페이스 분리
- 자동 채점(file-check) + 주관 평가(multi-choice) 이원 구조
- 조건별 러너 스크립트 (baseline, skills_only, memory 등)

---

## 6. 현재 제약사항 및 다음 단계

### 6.1 현재 제약사항

| 제약 | 영향 | 해결 방안 |
|------|------|---------|
| Skill evolver 비활성 | 실패에서 자동 skill 합성 불가 | Gemini를 evolver로 설정하거나 OpenAI API 키 추가 |
| 토큰 사용량 미보고 | 비용 추적 불가 | Gemini API 콘솔에서 직접 확인 |
| OAuth 토큰 만료 | 장시간 실험 시 중단 가능 | refresh_token 기반 갱신 스크립트 작성 |
| Memory 비활성 | 세션 간 맥락 미유지 | `metaclaw config memory.enabled true`로 활성화 가능 |

### 6.2 추천 다음 단계

1. **Skill evolver 활성화**: Gemini를 evolver LLM으로 설정하여 ISD 태스크 실패 시 자동 skill 합성 테스트
2. **ISD seed skill 작성**: Dick & Carey 모형 기반 ISD 핵심 원칙을 seed skill로 사전 주입
3. **ISD 태스크 시퀀스 시험**: Week 1~3 태스크를 순차적으로 보내면서 skill 축적 + 산출물 품질 변화 관찰
4. **MetaClaw-Bench 실행**: 기존 CLI 벤치마크를 돌려보며 평가 파이프라인 구조 학습
5. **ISD-Bench 프로토타입**: MetaClaw-Bench 구조를 참고하여 ISD-Bench의 `all_tests.json` + 채점 스크립트 초안 작성

---

## 부록: 실행 환경 상세

```
OS: macOS Darwin 25.3.0 (arm64)
Python: 3.13.12 (arm64, /opt/homebrew/opt/python@3.13)
PyTorch: 2.11.0 (CPU-only)
MetaClaw: 0.4.1.2 (editable install)
Gemini CLI: 0.36.0
venv 위치: /Users/sookbunlee/work/metr-isd/MetaClaw/.venv/
설정 파일: ~/.metaclaw/config.yaml
Skills 디렉토리: ~/.metaclaw/skills/ (비어 있음)
```
