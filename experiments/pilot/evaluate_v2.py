#!/usr/bin/env python3
"""ISD-Bench 파일럿 실험 정성평가 스크립트

LLM-as-judge 방식으로 baseline vs skills 산출물을 정성평가한다.
평가자는 먼저 정성적 분석을 수행한 후, 그 분석에 기반하여 점수를 부여한다.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

RESULTS_DIR = Path(__file__).parent / "results_v2"
EVAL_DIR = RESULTS_DIR / "evaluation_final"

RUBRIC = """
당신은 교수설계(ISD) 전문가로서 15년 이상의 실무 경험을 가진 평가자입니다.
지금부터 AI 에이전트가 생성한 ISD 산출물을 엄격하게 평가합니다.

## 평가 원칙
- 교수설계 전문가의 관점에서 비판적으로 평가하시오
- AI가 생성했다는 사실에 관대하지 마시오. 인간 전문가 수준을 기준으로 삼으시오
- 표면적으로 그럴듯한 내용과 실제로 정확하고 유용한 내용을 구분하시오
- 장점과 단점을 모두 구체적으로 지적하시오

## 평가 기준 (5개, 각 1~5점)

### 1. ISD 용어 정확성 (Terminology Accuracy)
교수설계 전문 용어의 사용이 정확하고 적절한가?
- 1점: ISD 전문 용어를 거의 사용하지 않거나, 사용한 용어가 부정확함
- 2점: 일부 ISD 용어를 사용하나 오용이 있음 (예: Entry Behaviors와 Prior Knowledge를 혼동)
- 3점: 기본적인 ISD 용어를 정확하게 사용함
- 4점: Dick & Carey, ADDIE 등 모형 특화 용어를 풍부하고 정확하게 사용함
- 5점: 하위 개념 수준의 전문 용어까지 정확히 구사하며, 용어 간 관계도 정확함

### 2. 내용 완전성 (Content Completeness)
태스크에서 요구한 모든 요소가 빠짐없이 포함되었는가?
- 1점: 요구사항의 핵심 요소 대부분이 누락됨
- 2점: 요구사항의 절반 이상이 누락되거나 표면적으로만 다룸
- 3점: 핵심 요소는 포함되었으나 일부 세부 요소가 누락됨
- 4점: 거의 모든 요소가 포함되고, 세부사항도 충분히 다룸
- 5점: 요구된 모든 요소가 완전히 포함되고, 추가적 통찰까지 제공함

### 3. 교수설계 모형 정합성 (Model Alignment)
Dick & Carey 체제적 교수설계 모형의 원칙과 절차에 충실한가?
- 1점: ISD 모형과 무관한 일반적 내용
- 2점: ISD 모형을 언급하지만 원칙을 제대로 반영하지 않음
- 3점: 기본 절차는 준수하나 모형의 핵심 원칙(체계성, 데이터 기반 등)이 미흡
- 4점: 모형의 핵심 원칙에 충실하며, 각 단계 간 연결이 논리적
- 5점: 모형의 심화 원칙(반복적 수정, 형성적 평가 연계 등)까지 적용함

### 4. 실용적 적용 가능성 (Practical Applicability)
실제 교육 현장에서 이 산출물을 바로 활용할 수 있는가?
- 1점: 추상적이고 일반적인 내용으로 실무 적용 불가
- 2점: 방향성은 맞으나 구체성이 부족하여 상당한 수정 필요
- 3점: 기본적으로 적용 가능하나 세부 조정이 필요함
- 4점: 구체적인 방법과 도구를 제시하여 약간의 수정만으로 적용 가능
- 5점: 즉시 현장에 적용할 수 있을 정도로 구체적이고 실용적

### 5. 맥락 연결성 (Context Linkage)
이전 주차 산출물의 결과를 적절히 참조하고 논리적으로 연결하는가?
(Week 1의 경우, 주어진 맥락 정보를 얼마나 잘 활용했는지로 평가)
- 1점: 이전 산출물/맥락과 무관하게 독립적으로 작성됨
- 2점: 형식적으로만 참조하고 실질적 연결이 없음
- 3점: 기본적인 연결은 있으나 피상적
- 4점: 이전 산출물의 주요 발견을 논리적으로 연결하여 활용
- 5점: 이전 산출물의 세부 내용까지 심층적으로 활용하여 발전시킴

## 응답 형식

반드시 아래 형식을 따르시오:

### 정성 분석

[각 기준에 대해 구체적인 근거를 들어 2~3문장으로 분석하시오.
장점과 단점을 모두 포함하시오. 산출물의 구체적인 내용을 인용하시오.]

**1. ISD 용어 정확성:**
[분석]

**2. 내용 완전성:**
[분석]

**3. 교수설계 모형 정합성:**
[분석]

**4. 실용적 적용 가능성:**
[분석]

**5. 맥락 연결성:**
[분석]

### 점수

| 기준 | 점수 |
|------|------|
| ISD 용어 정확성 | N/5 |
| 내용 완전성 | N/5 |
| 교수설계 모형 정합성 | N/5 |
| 실용적 적용 가능성 | N/5 |
| 맥락 연결성 | N/5 |
| **합계** | **N/25** |

### 종합 평가
[이 산출물의 전반적인 강점과 개선점을 2~3문장으로 요약]
"""


def evaluate_one(client, condition, week, task_data):
    """단일 산출물에 대한 정성평가를 수행한다."""

    user_prompt = f"""## 평가 대상

**조건:** {condition}
**주차:** Week {week} — {task_data['title']}

### 태스크 지시문
{task_data['prompt_sent']}

### AI 에이전트 산출물 (전문)
{task_data['response']}

---

위 산출물을 5개 평가 기준에 따라 엄격하게 평가하시오.
정성 분석을 먼저 수행한 후, 그에 기반하여 점수를 부여하시오."""

    response = client.chat.completions.create(
        model="gemini-2.5-pro",
        messages=[
            {"role": "system", "content": RUBRIC},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=4096,
        temperature=0.7,
        extra_body={"turn_type": "tool"},
    )
    return response.choices[0].message.content or ""


def extract_scores(eval_text):
    """평가 텍스트에서 점수 테이블을 추출한다."""
    scores = {}
    criteria_map = {
        "isd 용어 정확성": "terminology",
        "용어 정확성": "terminology",
        "내용 완전성": "completeness",
        "교수설계 모형 정합성": "model_alignment",
        "모형 정합성": "model_alignment",
        "실용적 적용 가능성": "practicality",
        "적용 가능성": "practicality",
        "맥락 연결성": "context_linkage",
    }

    for line in eval_text.split("\n"):
        for kr_name, en_name in criteria_map.items():
            if kr_name in line.lower():
                # N/5 패턴 찾기
                match = re.search(r'(\d+)\s*/\s*5', line)
                if match:
                    scores[en_name] = int(match.group(1))
                    break

    # 합계 계산
    if len(scores) == 5:
        scores["total"] = sum(scores.values())

    return scores


def main():
    client = OpenAI(api_key="metaclaw", base_url="http://localhost:30000/v1")
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    all_evals = {}

    for condition in ["baseline", "skills"]:
        all_evals[condition] = {}
        for week in [1, 2, 3]:
            path = RESULTS_DIR / condition / f"week{week}_response.json"
            if not path.exists():
                print(f"  [건너뜀] {path}")
                continue

            with open(path) as f:
                data = json.load(f)

            if data["response"].startswith("ERROR"):
                print(f"  [건너뜀] {condition}/Week {week} — 오류 응답")
                continue

            print(f"\n{'='*60}")
            print(f"평가: {condition.upper()} / Week {week} ({data['title']})")
            print(f"산출물 길이: {len(data['response']):,}자")
            print(f"{'='*60}")

            eval_text = evaluate_one(client, condition, week, data)
            scores = extract_scores(eval_text)

            result = {
                "condition": condition,
                "week": week,
                "title": data["title"],
                "response_length": len(data["response"]),
                "evaluation": eval_text,
                "scores": scores,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            all_evals[condition][f"week{week}"] = result

            # 개별 저장
            eval_path = EVAL_DIR / f"{condition}_week{week}_eval.json"
            with open(eval_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # 평가 결과 출력
            print(eval_text)
            if scores:
                print(f"\n추출된 점수: {scores}")

    # ─── 비교 요약 생성 ─────────────────────────
    print("\n\n" + "=" * 78)
    print("                    BASELINE vs SKILLS 비교 요약")
    print("=" * 78)

    criteria = ["terminology", "completeness", "model_alignment", "practicality", "context_linkage"]
    labels = {
        "terminology": "ISD 용어 정확성",
        "completeness": "내용 완전성",
        "model_alignment": "모형 정합성",
        "practicality": "실용적 적용성",
        "context_linkage": "맥락 연결성",
    }

    print(f"\n{'기준':<16} │ {'Baseline':^19} │ {'Skills':^19} │ {'차이':^6}")
    print(f"{'':16} │ {'W1':>4} {'W2':>4} {'W3':>4} {'평균':>5} │ {'W1':>4} {'W2':>4} {'W3':>4} {'평균':>5} │")
    print("─" * 70)

    b_total, s_total = 0, 0
    for c in criteria:
        b_vals = []
        s_vals = []
        for w in [1, 2, 3]:
            bk = f"week{w}"
            b_score = all_evals.get("baseline", {}).get(bk, {}).get("scores", {}).get(c, "?")
            s_score = all_evals.get("skills", {}).get(bk, {}).get("scores", {}).get(c, "?")
            b_vals.append(b_score)
            s_vals.append(s_score)

        b_nums = [v for v in b_vals if isinstance(v, int)]
        s_nums = [v for v in s_vals if isinstance(v, int)]
        b_avg = sum(b_nums) / len(b_nums) if b_nums else 0
        s_avg = sum(s_nums) / len(s_nums) if s_nums else 0
        diff = s_avg - b_avg
        b_total += b_avg
        s_total += s_avg

        print(f"{labels[c]:<16} │ {str(b_vals[0]):>4} {str(b_vals[1]):>4} {str(b_vals[2]):>4} {b_avg:>5.1f} │ {str(s_vals[0]):>4} {str(s_vals[1]):>4} {str(s_vals[2]):>4} {s_avg:>5.1f} │ {diff:>+5.1f}")

    print("─" * 70)
    diff = s_total - b_total
    print(f"{'합계':<16} │ {'':>14} {b_total:>5.1f} │ {'':>14} {s_total:>5.1f} │ {diff:>+5.1f}")
    print(f"{'(25점 만점)':<16} │ {'':>14} /25   │ {'':>14} /25   │")

    # 응답 길이 비교
    print(f"\n{'응답 길이':16} │ {'Baseline':>10} │ {'Skills':>10} │ {'변화율':>10}")
    print("─" * 55)
    for w in [1, 2, 3]:
        bl = all_evals.get("baseline", {}).get(f"week{w}", {}).get("response_length", 0)
        sl = all_evals.get("skills", {}).get(f"week{w}", {}).get("response_length", 0)
        d = sl - bl
        pct = (d / bl * 100) if bl else 0
        print(f"  Week {w}         │ {bl:>8,}자 │ {sl:>8,}자 │ {pct:>+8.1f}%")

    # 전체 요약 저장
    summary = {
        "evaluations": {
            cond: {k: {
                "scores": v.get("scores", {}),
                "response_length": v.get("response_length", 0),
            } for k, v in evals.items()}
            for cond, evals in all_evals.items()
        },
        "baseline_avg_total": b_total,
        "skills_avg_total": s_total,
        "delta": s_total - b_total,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    summary_path = EVAL_DIR / "comparison_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n요약 저장: {summary_path}")


if __name__ == "__main__":
    main()
