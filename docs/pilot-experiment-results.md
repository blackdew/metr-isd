# ISD-Bench 파일럿 실험 최종 결과 보고서

**작성일**: 2026-04-07  
**생성 모델**: Gemini 2.5 Pro (MetaClaw v0.4.1.2, skills_only 모드)  
**평가 모델**: Claude Opus 4.6 (생성 모델과 분리된 교차 평가)  
**시나리오**: 고등학교 수학 미적분, 고2 학생 30명

---

## 1. 실험 개요

ISD-Bench 연구의 사전 검증으로 3단계 파일럿 실험을 수행하였다.

| 실험 | 목적 | 조건 | 연구 질문 |
|------|------|------|----------|
| 실험 1 | Baseline ISD 능력 측정 | skill 없음 | RQ1 기초 데이터 |
| 실험 2 | Seed Skill 주입 효과 | ISD seed skill 5개 직접 주입 | RQ1, RQ4 |
| 실험 3 | 자동 Skill Evolution | MetaClaw evolver로 skill 자동 합성 | RQ4 |

### 실험 환경

| 항목 | 내용 |
|------|------|
| MetaClaw | v0.4.1.2, `skills_only` 모드, 프록시 `http://localhost:30000` |
| LLM | Gemini 2.5 Pro (OAuth 경유) |
| Evolver | Gemini 2.5 Pro (MetaClaw 프록시 경유, `enable_skill_evolution=true`) |
| Python | 3.13.12 (arm64), venv |
| 평가 | Claude Opus 4.6 독립 평가 (자기 평가 편향 방지) |

---

## 2. 실험 1·2: Baseline vs Seed Skill 비교

### 2.1 태스크 구성

Week 1~3의 ISD 태스크를 순차 실행. 이전 주차 출력을 다음 주차 input으로 전달 (체이닝).

| Week | 태스크 | 요구사항 |
|------|--------|---------|
| 1 | 학습자 분석 | 3영역(출발점 행동/사전 지식/학습자 특성) + 데이터 수집 방법 |
| 2 | 격차 분석 | 현재/목표/격차/원인/교수적 해결 적절성 |
| 3 | 학습목표 설계 | ABCD 형식 5개 + Bloom's Taxonomy + 계열화 + 격차 매핑 |

### 2.2 Seed Skill (5개)

| Skill | 핵심 지시 |
|-------|----------|
| `isd-learner-analysis` | Dick & Carey 학습자 분석 3영역 + 데이터 수집 방법 명시 |
| `isd-learning-objectives` | ABCD 형식 + Bloom's Taxonomy + 관찰 가능한 행동 동사 |
| `isd-gap-analysis` | 현재/목표/격차 영역별 매핑 + 교수적 해결 적절성 판단 |
| `isd-document-structure` | 체계적 문서 구조 (목적/본문/근거/연결) + 표/매트릭스 활용 |
| `isd-cross-reference` | 이전 주차 산출물 명시적 참조 + 일관성 검증 |

### 2.3 응답 길이 비교

| Week | Baseline | Skills | 변화 |
|------|:--------:|:------:|:----:|
| 1 학습자 분석 | 3,590자 | 4,289자 | +19.5% |
| 2 격차 분석 | 3,159자 | 3,293자 | +4.2% |
| 3 학습목표 설계 | 3,215자 | 3,138자 | -2.4% |

### 2.4 정성 평가 (Claude 독립 평가)

**평가 기준**: T(용어 정확성), C(내용 완전성), M(모형 정합성), P(실용성), L(맥락 연결성), 각 1~5점

#### Week 1: 학습자 분석

| 기준 | Baseline | Skills | 차이 | 근거 |
|------|:---:|:---:|:---:|------|
| T | 4 | 4 | 0 | 양쪽 모두 핵심 ISD 용어 정확 사용. VARK 등 특정 모형 미연결 |
| C | 4 | **5** | **+1** | Skills: 수준별 분류(상20/중60/하20%) 구체적 제시. Baseline: "중상"으로 뭉뚱그림 |
| M | 3 | **4** | **+1** | Skills: "종합 분석 및 교수-학습 전략 시사점" 섹션 추가로 후속 단계 연결 명시 |
| P | 3 | **4** | **+1** | Skills: Geogebra, 풀이 과정 분석 등 구체적 도구/방법 추가 |
| L | 3 | 3 | 0 | 양쪽 모두 맥락 반영은 하나 심층 활용 부족 |
| **소계** | **17** | **20** | **+3** | |

#### Week 2: 격차 분석

| 기준 | Baseline | Skills | 차이 |
|------|:---:|:---:|:---:|
| T | 4 | 4 | 0 |
| C | 5 | 5 | 0 |
| M | 4 | 4 | 0 |
| P | 4 | 4 | 0 |
| L | 5 | 5 | 0 |
| **소계** | **22** | **22** | **0** |

Week 1의 품질이 체이닝되어 양쪽 모두 높은 수준. Skill보다 이전 산출물의 품질이 지배적 변수.

#### Week 3: 학습목표 설계

| 기준 | Baseline | Skills | 차이 |
|------|:---:|:---:|:---:|
| T | 5 | 5 | 0 |
| C | 5 | 5 | 0 |
| M | 5 | 4 | -1 |
| P | 4 | 5 | +1 |
| L | 5 | 5 | 0 |
| **소계** | **24** | **24** | **0** |

Baseline: Bloom's 위계(이해→적용→분석→평가→창조) 정확. Skills: 목표 4가 "적용"으로 위계 깨짐(-1), 대신 수행 기준이 더 구체적(+1).

### 2.5 종합 비교

| 기준 | Baseline 평균 | Skills 평균 | Δ |
|------|:---:|:---:|:---:|
| T (용어 정확성) | 4.3 | 4.3 | 0.0 |
| C (내용 완전성) | 4.7 | 5.0 | **+0.3** |
| M (모형 정합성) | 4.0 | 4.0 | 0.0 |
| P (실용성) | 3.7 | 4.3 | **+0.7** |
| L (맥락 연결) | 4.3 | 4.3 | 0.0 |
| **합계** | **21.0/25** | **22.0/25** | **+1.0** |

**핵심 발견**:
- Skill 효과는 **Week 1(구조화된 태스크)**에서 집중적으로 나타남 (+3점)
- **내용 완전성(C)과 실용성(P)**에서 가장 큰 개선
- Week 2~3에서는 **체이닝 효과**가 skill보다 지배적 → 점수 동일
- Baseline도 21/25로 양호 → **천장 효과**로 개선 여지 제한적

---

## 3. 실험 3: 자동 Skill Evolution

### 3.1 설정

5개 ISD 태스크(Week 5~7 수준)를 동일 세션(`session_id` 고정, `turn_type=main` 명시)으로 전송하여 MetaClaw의 자동 skill evolution 트리거.

| 태스크 | 내용 | 응답 길이 |
|--------|------|:--------:|
| ARCS 동기 설계 | Keller의 ARCS 모델 기반 4요소별 전략 | 6,938자 |
| Gagné 수업 설계 | 9 events of instruction, 90분 수업 | 6,516자 |
| 형성평가 설계 | 진단/과정/총괄 평가 3종 + 루브릭 | 5,602자 |
| Merrill e-러닝 설계 | First Principles 기반 온라인 모듈 | 4,344자 |
| 차별화 교수 설계 | Tomlinson 기반 수준별 전략 | 5,408자 |

### 3.2 Evolution 결과

4회 evolution이 발생하여 **총 8개 skill이 자동 합성**되었다.

| Skill | 카테고리 | 내용 요약 |
|-------|---------|----------|
| `apply-instructional-design-frameworks` | general | ISD 모형의 구성요소를 응답 구조로 적용 |
| `integrate-dick-and-carey-model` | general | ARCS, Gagné 등 하위 모형을 Dick & Carey 프레임워크 안에 배치 |
| `uphold-instructional-design-persona` | agentic | 요청된 하위 모형이 있어도 핵심 Dick & Carey 페르소나 유지 |
| `produce-formal-pedagogical-documents` | communication | 학술적 문서 형식 (계층 구조, 표, 루브릭) 준수 |
| `propose-outline-for-structured-output` | agentic | 복잡한 ISD 문서 작성 전 개요를 먼저 제안 |
| `match-request-language` | communication | 프롬프트 언어와 응답 언어 일치 유지 |
| `avoid-skill-duplication` | common_mistakes | 기존 skill과 중복되는 새 skill 합성 방지 |
| `focus-on-failure-pattern` | agentic | 실패 분석 시 주제가 아닌 행동 패턴에 집중 |

### 3.3 합성된 Skill 분석

**ISD 도메인 특화 비율: 75% (6/8)**

합성된 8개 skill 중 6개가 ISD 원칙에 직접 관련된다. 특히 주목할 점:

1. **Dick & Carey 통합 전략**: 시스템 프롬프트에 "Dick & Carey 모형 기반"이라고만 명시했는데, evolver가 이를 발전시켜 "하위 모형을 Dick & Carey 안에 배치하는 구체적 전략"을 합성. 단순 규칙 반복이 아닌 **전문적 통찰을 추출**한 사례.

2. **언어 문제 자동 해결**: 이전 실험에서 형성평가 태스크가 중국어로 응답된 문제를 evolver가 **자동으로 인식**하고 `match-request-language` 규칙을 합성. Skill evolution이 관찰된 문제를 자동 교정할 수 있음을 보여줌.

3. **메타 skill 합성**: `avoid-skill-duplication`과 `focus-on-failure-pattern`은 evolver 자체의 동작을 개선하는 자기 참조적(self-referential) skill. MetaClaw의 evolver가 단순 도메인 규칙 추출을 넘어 **자기 개선 능력**을 보유함을 시사.

### 3.4 Evolution 타임라인

```
태스크 1~3 완료 (ARCS, Gagné, 형성평가)
  ↓ 3턴 누적 → 1차 evolution (비동기)
태스크 4~5 완료 (Merrill, 차별화 교수) + session_done=True
  ↓ 세션 종료 → 2차~4차 evolution 연쇄 트리거
──────────────────────────────────────────
결과: 4회 evolution × 2개/회 = 8개 skill 합성
```

**참고**: Evolution은 비동기 실행. 스크립트 종료 시점에는 "합성 없음"으로 표시되나, 이후 `~/.metaclaw/skills/` 디렉토리와 `evolution_history.jsonl`에서 결과 확인 가능.

---

## 4. 종합 논의

### 4.1 ISD에서 Skill 효과의 본질은 CLI와 다르다

| | CLI 태스크 (MetaClaw-Bench) | ISD 태스크 (ISD-Bench) |
|---|---|---|
| 핵심 요구 | 규칙 준수 (날짜 포맷, .bak 생성 등) | 전문 지식의 깊이 |
| Skill의 역할 | 정답 규칙을 직접 알려줌 | 구조를 안내하지만 내용 품질은 사전 지식에 의존 |
| 효과 패턴 | 중간 난이도에서 극대화 | 초반 구조화된 태스크에서 극대화 |

Seed skill은 **내용 완전성(+0.3)과 실용성(+0.7)**을 개선했지만, **용어 정확성과 모형 정합성**에는 영향 없음. 이는 skill이 "무엇을 포함하라"는 구조적 안내에는 효과적이지만, "전문 지식을 더 깊이 적용하라"는 요구에는 한계가 있음을 시사.

### 4.2 체이닝이 adaptation보다 강력한 변수

Week 2~3에서 baseline과 skills의 점수가 동일한 것은, 이전 주차 출력이 현재 품질을 좌우하기 때문. 이는 ISD-Bench 15주 설계에서 **초기 오류의 복리 효과**와 **체이닝 vs skill 효과의 분리**가 핵심 과제임을 의미.

### 4.3 자기 평가 편향

| 평가 설계 | 결과 | 변별력 |
|----------|------|:---:|
| Gemini → Gemini (자기 평가) | 전원 25/25 만점 | 없음 |
| Claude → Gemini (교차 평가) | 17~24/25 범위 | 있음 |

생성 모델과 평가 모델의 분리는 필수. 교육 도메인에서 LLM-as-judge의 신뢰도 분석 자체가 연구 기여 가능.

### 4.4 MetaClaw의 ISD 활용 가능성

| 기능 | 상태 | 비고 |
|------|------|------|
| Skill 검색/주입 | 가능 (설정 주의 필요) | `turn_type=main` 명시, 프록시 오염 우회 |
| 자동 Skill Evolution | **성공** | `enable_skill_evolution=true`, evolver API 설정 필수 |
| ISD Skill 합성 품질 | **우수** (75% 도메인 특화) | Dick & Carey 통합 전략까지 자동 추출 |
| RL 훈련 | 미검증 | Tinker 계정 필요 |

### 4.5 논문 포지셔닝 강화

| 기여 | 파일럿 근거 |
|------|-----------|
| ISD 최초 벤치마크 | Baseline 21/25 → 충분히 가능한 도메인. "어떤 조건에서 얼마나 좋아지는가"가 핵심 |
| MetaClaw 교육 도메인 확장 | 8개 ISD skill 자동 합성 성공. 도메인 적응 방법론 자체가 기여 |
| 인간-AI 종단 비교 | 체이닝 효과 발견 → "체이닝 vs skill 효과 분리" 분석이 차별적 가치 |
| LLM-as-judge 검증 | 자기 평가 편향 실증 → 교차 평가 필수성 입증 |

---

## 5. 다음 단계

1. **자동 합성 skill 효과 검증**: evolution으로 합성된 8개 skill 주입 후 Week 1~3 재실행 → seed skill 결과와 비교
2. Week 5~7 복잡한 태스크에서 baseline vs skills 비교 (천장 효과 회피)
3. 체이닝 효과 통제 실험 설계 (표준 산출물 전달 조건 추가)
4. 인간 ISD 전문가의 루브릭 평가와 Claude 교차 평가 간 ICC 비교
5. Kimi-K2.5 등 baseline이 낮은 모델에서의 실험
6. "실용성(P)" 기준 세분화 (P1/P2/P3) 후 변별력 재검증
