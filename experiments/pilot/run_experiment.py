#!/usr/bin/env python3
"""ISD-Bench Pilot Experiment Runner

Usage:
    python run_experiment.py --condition baseline    # Experiment 1
    python run_experiment.py --condition skills       # Experiment 2
    python run_experiment.py --condition evolution     # Experiment 3
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.pilot.tasks import (
    EVOLUTION_TASKS,
    SCENARIO,
    SYSTEM_PROMPT,
    WEEK_TASKS,
)

PROXY_BASE_URL = "http://localhost:30000/v1"
API_KEY = "metaclaw"
MODEL = "gemini-2.5-pro"

RESULTS_DIR = Path(__file__).parent / "results"


def build_week_prompt(task: dict, previous_output: str | None = None) -> str:
    """Fill in scenario placeholders and optionally inject previous output."""
    prompt = task["prompt"].format(**SCENARIO)
    if task.get("uses_previous") and previous_output:
        # previous_output placeholder is already in the template
        pass
    elif task.get("uses_previous") and not previous_output:
        prompt = prompt.replace("{previous_output}", "(이전 산출물 없음)")
    return prompt


def build_evolution_prompt(task: dict) -> str:
    """Fill in scenario placeholders for evolution tasks."""
    return task["prompt"].format(**SCENARIO)


def call_model(client: OpenAI, prompt: str, max_tokens: int) -> str:
    """Call the MetaClaw proxy and return the response text."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def save_result(output_path: Path, data: dict) -> None:
    """Write result JSON to disk, creating directories as needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  -> 저장 완료: {output_path}")


def run_week_tasks(client: OpenAI, condition: str, max_tokens: int) -> None:
    """Run week 1-3 tasks sequentially, chaining previous output."""
    output_dir = RESULTS_DIR / condition
    previous_output: str | None = None

    for task in WEEK_TASKS:
        week = task["week"]
        title = task["title"]
        print(f"\n[Week {week}] {title} 실행 중...")

        # Build prompt: inject previous output if needed
        if task.get("uses_previous"):
            raw_prompt = task["prompt"].format(
                **SCENARIO, previous_output=previous_output or "(이전 산출물 없음)"
            )
        else:
            raw_prompt = task["prompt"].format(**SCENARIO)

        try:
            response_text = call_model(client, raw_prompt, max_tokens)
        except Exception as e:
            print(f"  [오류] Week {week} 호출 실패: {e}")
            response_text = f"ERROR: {e}"

        result = {
            "condition": condition,
            "week": week,
            "title": title,
            "uses_previous": task.get("uses_previous", False),
            "prompt_sent": raw_prompt,
            "response": response_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
        }

        output_path = output_dir / f"week{week}_response.json"
        save_result(output_path, result)

        # Chain: next task receives this response as context
        previous_output = response_text
        print(f"  완료 (응답 길이: {len(response_text)} 자)")


def run_evolution_tasks(client: OpenAI, condition: str, max_tokens: int) -> None:
    """Run evolution tasks independently (no chaining)."""
    output_dir = RESULTS_DIR / condition

    for task in EVOLUTION_TASKS:
        task_id = task["id"]
        title = task["title"]
        print(f"\n[Evolution] {title} ({task_id}) 실행 중...")

        raw_prompt = build_evolution_prompt(task)

        try:
            response_text = call_model(client, raw_prompt, max_tokens)
        except Exception as e:
            print(f"  [오류] {task_id} 호출 실패: {e}")
            response_text = f"ERROR: {e}"

        result = {
            "condition": condition,
            "task_id": task_id,
            "title": title,
            "prompt_sent": raw_prompt,
            "response": response_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
        }

        output_path = output_dir / f"task{task_id}_response.json"
        save_result(output_path, result)
        print(f"  완료 (응답 길이: {len(response_text)} 자)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ISD-Bench Pilot Experiment Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--condition",
        required=True,
        choices=["baseline", "skills", "evolution"],
        help="실험 조건 선택",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        dest="max_tokens",
        help="최대 응답 토큰 수 (기본값: 4096)",
    )
    args = parser.parse_args()

    print(f"=== ISD-Bench Pilot Experiment ===")
    print(f"조건: {args.condition}")
    print(f"모델: {MODEL}")
    print(f"프록시: {PROXY_BASE_URL}")
    print(f"최대 토큰: {args.max_tokens}")
    print(f"결과 저장 위치: {RESULTS_DIR / args.condition}")
    print("=" * 34)

    client = OpenAI(api_key=API_KEY, base_url=PROXY_BASE_URL)

    if args.condition in ("baseline", "skills"):
        run_week_tasks(client, args.condition, args.max_tokens)
    elif args.condition == "evolution":
        run_evolution_tasks(client, args.condition, args.max_tokens)

    print("\n=== 실험 완료 ===")


if __name__ == "__main__":
    main()
