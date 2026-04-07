#!/usr/bin/env python3
"""ISD-Bench Pilot Experiment Runner v2

MetaClaw 프록시를 우회하고 Gemini API를 직접 호출하여
프롬프트 오염 없이 baseline vs skills 비교를 수행한다.

Usage:
    python run_experiment_v2.py --condition baseline
    python run_experiment_v2.py --condition skills
    python run_experiment_v2.py evaluate   # LLM-as-judge 평가
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from experiments.pilot.tasks import (
    EVOLUTION_TASKS,
    SCENARIO,
    SYSTEM_PROMPT,
    WEEK_TASKS,
)

MODEL = "gemini-2.5-pro"

RESULTS_DIR = Path(__file__).parent / "results_v2"

# ─── ISD Seed Skills (직접 주입용) ────────────────────────────

ISD_SKILLS_BLOCK = """
## Active Skills

### isd-learner-analysis
_학습자 분석 시 Dick & Carey 모형의 세 가지 분석 영역과 데이터 수집 방법을 반드시 포함_

학습자 분석 산출물을 작성할 때 반드시 다음 세 영역을 체계적으로 포함하라:
1. **출발점 행동 (Entry Behaviors)**: 선수학습 요소를 목록화하고 각각의 예상 달성 수준을 기술. 진단 방법: 사전평가(pre-test), 선수학습 체크리스트
2. **사전 지식 (Prior Knowledge)**: 관련 영역의 경험, 배경 지식, 오개념(misconception) 분석. 진단 방법: 개념 지도(concept map), 면담, 설문
3. **학습자 특성 (General Characteristics)**: 동기(ARCS 모델 기반), 학습 스타일(VARK), 태도, 자기효능감. 인구통계: 연령, 학업 수준, 사회문화적 배경. 진단 방법: ARCS 동기 설문, 학습양식 검사
Anti-pattern: 학습자를 "고등학생"으로만 뭉뚱그려 기술하지 말 것. 구체적 데이터에 기반한 프로파일을 제시하라.

### isd-learning-objectives
_학습목표 작성 시 ABCD 형식과 Bloom's Taxonomy 인지적 영역 수준을 정확히 적용_

학습목표를 작성할 때 반드시 ABCD 형식을 준수하라:
- A (Audience): 대상을 명시
- B (Behavior): 관찰 가능한 행동 동사 사용. 피할 것: "이해한다", "안다". 사용할 것: "풀 수 있다", "설명할 수 있다"
- C (Condition): 학습 조건 명시
- D (Degree): 수행 기준 명시 (정확도, 시간, 비율)
각 목표에 Bloom's Taxonomy 수준을 명시하라: 기억→이해→적용→분석→평가→창조
목표 간 계열화(sequencing)를 제시하고 선후 관계의 근거를 설명하라.

### isd-gap-analysis
_격차 분석 시 현재/목표 수준을 구체적으로 기술하고 교수적 해결 적절성을 판단_

격차 분석에서 반드시 다음 구조를 따르라:
1. 현재 수준: 학습자 분석 데이터에 근거 (추측이 아닌 증거 기반), 영역별(지식/기능/태도) 구분
2. 목표 수준: 교육과정 성취기준에 기반, 측정 가능한 수준으로 표현
3. 격차: 현재와 목표의 차이를 영역별 매핑, 격차 크기를 상/중/하로 판정
4. 원인 분석: 교수적 요인과 학습자 요인 구분
5. 교수적 해결 적절성: 교수설계로 해결 가능한 격차와 비교수적 해결이 필요한 격차 구분

### isd-document-structure
_ISD 산출물의 공통 문서 구조를 체계적으로 작성_

모든 ISD 산출물은 다음 구조를 따르라:
1. 제목 및 메타 정보 2. 목적 3. 이전 단계 요약 4. 본문 5. 근거 및 참조 6. 다음 단계와의 연결 7. 제한점
표, 매트릭스, 체크리스트를 적극 활용. 에세이 형식으로 장황하게 쓰지 말 것.

### isd-cross-reference
_이전 주차 산출물을 명시적으로 참조하고 논리적 일관성을 유지_

각 주차 산출물은 이전 주차 결과를 명시적으로 참조해야 한다:
- 이전 주차 핵심 발견/결론을 직접 인용
- "학습자 분석에서 확인된 바와 같이..." 형태로 구체적 연결
- 새로운 주장 시 이전 단계의 어떤 근거에서 도출되었는지 명시
일관성 검증: 학습자분석→격차분석 연결, 격차→학습목표 매핑 확인
"""

# ─── LLM-as-Judge 평가 프롬프트 ────────────────────────────

JUDGE_SYSTEM = """당신은 교수설계(ISD) 전문가이자 학술 평가자입니다.
주어진 ISD 산출물을 아래 5개 기준으로 평가하시오.
각 기준에 대해 1~5점 척도로 점수를 부여하고, 근거를 1~2문장으로 설명하시오.

반드시 아래 JSON 형식으로만 응답하시오. 다른 텍스트를 포함하지 마시오.

{
  "criteria": {
    "terminology": {"score": N, "reason": "..."},
    "completeness": {"score": N, "reason": "..."},
    "model_alignment": {"score": N, "reason": "..."},
    "practicality": {"score": N, "reason": "..."},
    "context_linkage": {"score": N, "reason": "..."}
  },
  "total": N,
  "overall_comment": "..."
}

평가 기준:
1. terminology (ISD 용어 정확성): 1=미사용, 2=일부 오류, 3=기본 정확, 4=풍부, 5=모형 특화 용어까지 정확
2. completeness (내용 완전성): 1=대부분 누락, 2=절반 누락, 3=핵심 포함 일부 누락, 4=대부분 포함, 5=모든 요소 완전
3. model_alignment (교수설계 모형 정합성): 1=무관, 2=일부 반영, 3=기본 준수, 4=원칙 충실, 5=심화 원칙 적용
4. practicality (실용적 적용 가능성): 1=불가, 2=수정 필요, 3=기본 적용, 4=구체적 방법, 5=즉시 현장 적용
5. context_linkage (맥락 연결성): 1=무관, 2=형식적, 3=기본 연결, 4=논리적 연결, 5=심층 활용

total은 5개 점수의 합산 (최대 25점)."""

JUDGE_USER_TEMPLATE = """다음은 {week_title} 태스크에 대한 AI 에이전트의 산출물입니다.

[태스크 지시문]
{prompt}

[에이전트 산출물]
{response}

위 산출물을 5개 기준으로 평가하시오. JSON으로만 응답하시오."""


PROXY_URL = "http://localhost:30000/v1"


def get_client() -> OpenAI:
    """MetaClaw 프록시 클라이언트 (LLM 라우팅만 사용, skill 주입은 직접 제어)."""
    return OpenAI(api_key="metaclaw", base_url=PROXY_URL)


def call_model(
    client: OpenAI, system_prompt: str, user_prompt: str, max_tokens: int
) -> str:
    """MetaClaw 프록시 경유 호출. system_prompt를 직접 제어하여 프롬프트 오염 방지.

    핵심: 프록시가 skill을 추가 주입하더라도, 우리가 제어하는 system_prompt에
    ISD 맥락을 충분히 담으면 모델이 ISD 태스크에 집중한다.
    또한 turn_type='tool'로 설정하여 프록시의 skill injection을 우회한다.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
        extra_body={"turn_type": "tool"},  # skill injection 우회
    )
    return response.choices[0].message.content or ""


def run_week_tasks(client: OpenAI, condition: str, max_tokens: int) -> None:
    """Week 1~3 순차 실행. condition에 따라 system prompt 구성."""
    output_dir = RESULTS_DIR / condition
    output_dir.mkdir(parents=True, exist_ok=True)

    if condition == "skills":
        system_prompt = SYSTEM_PROMPT + "\n\n" + ISD_SKILLS_BLOCK
        print(f"  [Skills 주입] {len(ISD_SKILLS_BLOCK)} 자 추가됨")
    else:
        system_prompt = SYSTEM_PROMPT

    # 언어 제약 추가 (v1에서 발견된 언어 전환 문제 방지)
    system_prompt += "\n\n모든 응답은 반드시 한국어로 작성하시오."

    previous_output: str | None = None

    for task in WEEK_TASKS:
        week = task["week"]
        title = task["title"]
        print(f"\n[Week {week}] {title} 실행 중...")

        if task.get("uses_previous"):
            user_prompt = task["prompt"].format(
                **SCENARIO,
                previous_output=previous_output or "(이전 산출물 없음)",
            )
        else:
            user_prompt = task["prompt"].format(**SCENARIO)

        try:
            response_text = call_model(client, system_prompt, user_prompt, max_tokens)
        except Exception as e:
            print(f"  [오류] Week {week}: {e}")
            response_text = f"ERROR: {e}"

        result = {
            "condition": condition,
            "week": week,
            "title": title,
            "system_prompt_length": len(system_prompt),
            "prompt_sent": user_prompt,
            "response": response_text,
            "response_length": len(response_text),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "api": "direct_gemini",
        }

        output_path = output_dir / f"week{week}_response.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        previous_output = response_text
        print(f"  완료 ({len(response_text)} 자) → {output_path.name}")


def run_evaluation(client: OpenAI) -> None:
    """LLM-as-judge로 baseline vs skills 정량 평가."""
    eval_dir = RESULTS_DIR / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)

    all_scores = {}

    for condition in ["baseline", "skills"]:
        scores = []
        for week in [1, 2, 3]:
            result_path = RESULTS_DIR / condition / f"week{week}_response.json"
            if not result_path.exists():
                print(f"  [건너뜀] {result_path} 없음")
                continue

            with open(result_path, encoding="utf-8") as f:
                data = json.load(f)

            # ERROR 응답은 건너뜀
            if data["response"].startswith("ERROR"):
                print(f"  [건너뜀] {condition}/week{week} — 오류 응답")
                scores.append(None)
                continue

            print(f"\n[평가] {condition}/Week {week} ({data['title']})...")

            judge_prompt = JUDGE_USER_TEMPLATE.format(
                week_title=f"Week {week}: {data['title']}",
                prompt=data["prompt_sent"][:2000],  # 프롬프트는 2000자로 제한
                response=data["response"],
            )

            try:
                judge_response = call_model(
                    client, JUDGE_SYSTEM, judge_prompt, 1000
                )
                # JSON 파싱 (```json ... ``` 래퍼 제거)
                clean = judge_response.strip()
                if clean.startswith("```"):
                    clean = clean.split("\n", 1)[1]
                    clean = clean.rsplit("```", 1)[0]
                score_data = json.loads(clean)
            except (json.JSONDecodeError, Exception) as e:
                print(f"  [평가 오류] {e}")
                print(f"  원본 응답: {judge_response[:200]}")
                score_data = {"error": str(e), "raw": judge_response[:500]}

            score_data["condition"] = condition
            score_data["week"] = week
            score_data["title"] = data["title"]
            scores.append(score_data)

            # 개별 평가 저장
            eval_path = eval_dir / f"{condition}_week{week}_eval.json"
            with open(eval_path, "w", encoding="utf-8") as f:
                json.dump(score_data, f, ensure_ascii=False, indent=2)

            if "criteria" in score_data:
                total = score_data.get("total", "N/A")
                print(f"  총점: {total}/25")

        all_scores[condition] = scores

    # 비교 요약 생성
    print("\n" + "=" * 60)
    print("평가 결과 비교")
    print("=" * 60)

    header = f"{'기준':<20} {'Baseline':>10} {'Skills':>10} {'차이':>10}"
    print(header)
    print("-" * 50)

    criteria_names = {
        "terminology": "ISD 용어 정확성",
        "completeness": "내용 완전성",
        "model_alignment": "모형 정합성",
        "practicality": "실용적 적용성",
        "context_linkage": "맥락 연결성",
    }

    summary = {"baseline": {}, "skills": {}}

    for key, label in criteria_names.items():
        for cond in ["baseline", "skills"]:
            vals = []
            for s in all_scores.get(cond, []):
                if s and "criteria" in s and key in s["criteria"]:
                    vals.append(s["criteria"][key]["score"])
            summary[cond][key] = sum(vals) / len(vals) if vals else 0

        b = summary["baseline"][key]
        s = summary["skills"][key]
        diff = s - b
        sign = "+" if diff > 0 else ""
        print(f"{label:<20} {b:>10.2f} {s:>10.2f} {sign}{diff:>9.2f}")

    # 총점 비교
    b_total = sum(summary["baseline"].values())
    s_total = sum(summary["skills"].values())
    diff_total = s_total - b_total
    sign = "+" if diff_total > 0 else ""
    print("-" * 50)
    print(f"{'총점 (평균)':<20} {b_total:>10.2f} {s_total:>10.2f} {sign}{diff_total:>9.2f}")
    print(f"{'25점 만점 환산':<20} {b_total:>10.2f}/25 {s_total:>10.2f}/25")

    # 요약 JSON 저장
    comparison = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "baseline_summary": summary["baseline"],
        "skills_summary": summary["skills"],
        "baseline_total": b_total,
        "skills_total": s_total,
        "difference": diff_total,
        "all_scores": {
            k: [s for s in v if s] for k, v in all_scores.items()
        },
    }
    comp_path = eval_dir / "comparison_summary.json"
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    print(f"\n비교 요약 저장: {comp_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ISD-Bench Pilot v2 (Direct API)")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="실험 실행")
    run_p.add_argument("--condition", required=True, choices=["baseline", "skills"])
    run_p.add_argument("--max-tokens", type=int, default=4096, dest="max_tokens")

    sub.add_parser("evaluate", help="LLM-as-judge 평가 실행")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    client = get_client()

    if args.command == "run":
        print(f"=== ISD-Bench Pilot v2 ===")
        print(f"조건: {args.condition}")
        print(f"모델: {MODEL} (직접 호출, 프록시 우회)")
        print(f"최대 토큰: {args.max_tokens}")
        print("=" * 26)
        run_week_tasks(client, args.condition, args.max_tokens)
        print("\n=== 실험 완료 ===")

    elif args.command == "evaluate":
        print("=== LLM-as-Judge 평가 ===")
        run_evaluation(client)
        print("\n=== 평가 완료 ===")


if __name__ == "__main__":
    main()
