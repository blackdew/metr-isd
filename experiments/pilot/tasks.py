"""ISD Pilot Experiment Task Prompts"""

SYSTEM_PROMPT = """당신은 교수설계(Instructional Systems Design, ISD) 전문가입니다.
Dick & Carey 모형에 기반하여 체계적인 교수설계를 수행합니다.
모든 산출물은 학술적으로 정확하고, 실무에서 즉시 활용 가능한 수준으로 작성하시오."""

SCENARIO = {
    "subject": "고등학교 수학",
    "unit": "미적분 (극한, 미분, 적분의 기초)",
    "learners": "미적분을 처음 배우는 고등학교 2학년 학생 30명",
    "context": "1학기 정규 수업, 주 4시간, 교과서 기반",
}

# Week 1-3 for experiments 1 & 2 (baseline & skills comparison)
WEEK_TASKS = [
    {
        "week": 1,
        "title": "학습자 분석",
        "prompt": """다음 맥락에서 학습자 분석 보고서를 작성하시오.

[맥락]
- 교과: {subject}
- 단원: {unit}
- 대상: {learners}
- 환경: {context}

[요구사항]
다음 세 영역을 반드시 포함하여 체계적인 학습자 분석 보고서를 작성하시오:
1. 출발점 행동 (Entry Behaviors): 미적분 학습에 필요한 선수학습 요소와 학습자의 예상 달성 수준
2. 사전 지식 (Prior Knowledge): 관련 수학 영역(함수, 수열, 극한 개념)에 대한 배경 지식
3. 학습자 특성: 동기 수준, 학습 스타일, 수학에 대한 태도, 인구통계학적 특성

각 영역에 대해 데이터 수집 방법(설문, 면담, 사전평가 등)을 구체적으로 제시하시오.""",
        "uses_previous": False,
    },
    {
        "week": 2,
        "title": "격차 분석",
        "prompt": """아래의 학습자 분석 결과를 바탕으로, 문제 정의 및 격차 분석을 수행하시오.

[이전 주차 산출물]
{previous_output}

[요구사항]
1. 현재 수준 (Current State): 학습자 분석에서 도출된 학습자의 현재 역량 수준을 요약
2. 목표 수준 (Desired State): 미적분 단원 학습 후 도달해야 할 역량 수준을 구체적으로 기술
3. 격차 (Gap): 현재 수준과 목표 수준 사이의 차이를 영역별로 분석
4. 원인 분석: 격차가 발생하는 주요 원인을 교수적 요인과 학습자 요인으로 구분하여 분석
5. 교수적 해결의 적절성: 이 격차가 교수설계를 통해 해결 가능한지 판단하고 근거 제시""",
        "uses_previous": True,
    },
    {
        "week": 3,
        "title": "학습목표 설계",
        "prompt": """아래의 격차 분석 결과를 바탕으로, 학습목표를 설계하시오.

[이전 주차 산출물]
{previous_output}

[요구사항]
1. ABCD 형식에 따른 학습목표 5개를 작성하시오:
   - A (Audience): 학습 대상자
   - B (Behavior): 관찰 가능한 행동 동사로 기술
   - C (Condition): 학습이 이루어지는 조건
   - D (Degree): 수행 기준 (정확도, 시간, 비율 등)
2. 각 목표에 Bloom's Taxonomy의 인지적 영역 수준을 명시하시오 (기억/이해/적용/분석/평가/창조)
3. 목표 간 계열화 (sequencing)를 제시하고, 선후 관계의 근거를 설명하시오
4. 각 목표가 격차 분석의 어떤 격차를 해소하는지 매핑하시오""",
        "uses_previous": True,
    },
]

# Experiment 3: harder tasks for failure induction (Week 5-7 level)
EVOLUTION_TASKS = [
    {
        "id": "arcs_motivation",
        "title": "ARCS 동기 설계",
        "prompt": """다음 맥락에서 Keller의 ARCS 모델에 기반한 동기 설계 전략을 수립하시오.

[맥락]
- 교과: {subject}
- 단원: {unit}
- 대상: {learners}
- 문제: 학습자들이 미적분의 추상적 개념에 대해 낮은 동기와 높은 불안감을 보임

[요구사항]
1. ARCS 4개 요소(Attention, Relevance, Confidence, Satisfaction)별로:
   a. 현재 학습자 동기 상태 진단 (구체적 증거 기반)
   b. 동기 설계 전략 최소 2개씩 (총 8개 이상)
   c. 각 전략을 실현하는 구체적 교수 활동 설계 (시간, 자료, 교사 행동 포함)
   d. 전략의 효과 측정 방법
2. 전략 간 통합 시나리오: 50분 수업 1차시에서 ARCS 요소가 어떻게 연동되는지 시간 흐름으로 제시
3. 잠재적 위험(동기 저하 요인)과 대응 방안""",
    },
    {
        "id": "gagne_lesson",
        "title": "Gagné 수업 설계",
        "prompt": """Gagné의 9 events of instruction에 따른 90분 수업 설계안을 작성하시오.

[맥락]
- 교과: {subject}
- 단원: 미분의 정의와 기본 공식
- 대상: {learners}
- 수업 시간: 90분 (블록 수업)

[요구사항]
1. 9개 교수 사건(instructional events) 각각에 대해:
   a. 구체적 교수-학습 활동 (교사 활동 + 학습자 활동)
   b. 소요 시간 (총 90분 내 배분)
   c. 사용할 매체/자료
   d. 학습자 반응 예측 및 피드백 전략
2. 각 사건 간 전이(transition) 전략
3. 차시별 연결: 이전 차시(극한의 개념) 복습 연결과 다음 차시(미분의 응용) 예고
4. 평가: 각 사건에서의 형성적 점검 방법
5. 개별화: 상/중/하 수준별 차별화 전략""",
    },
    {
        "id": "formative_eval",
        "title": "형성평가 설계",
        "prompt": """미적분 단원에 대한 형성평가 체계를 설계하시오.

[맥락]
- 교과: {subject}
- 단원: {unit}
- 대상: {learners}

[요구사항]
1. 진단평가 (Diagnostic Assessment):
   - 미적분 선수학습 진단 도구 설계 (최소 10문항)
   - 각 문항의 측정 목표와 난이도 명시
   - 진단 결과에 따른 수준별 처방 매트릭스
2. 과정평가 (Process Assessment):
   - 주차별(4주) 형성평가 도구 설계
   - 관찰 체크리스트, 자기평가 도구, 동료평가 도구 각 1종
   - 피드백 제공 방법 및 시점
3. 총괄평가 (Summative Assessment):
   - 수행과제(performance task) 1개 설계
   - 분석적 채점 루브릭 (4수준 × 5개 준거)
   - 신뢰도 확보 방안 (채점자 간 일치도)
4. 평가 도구 간 정합성: 학습목표-평가 정렬(alignment) 매트릭스""",
    },
]
