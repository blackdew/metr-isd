#!/usr/bin/env python3
"""ISD-Bench Pilot: Skill Evolution 실험 v3

MetaClaw의 자동 skill evolution이 ISD 도메인에서 트리거되는지 검증한다.

핵심 설정:
- session_id 고정 → 같은 세션에 턴이 누적되어 evolution 조건 충족
- turn_type=main 명시 → session_id 있을 때 기본값이 "side"이므로 반드시 명시
- session_done=True → 마지막 턴에서 잔여 턴도 evolution 트리거

Usage:
    python run_evolution_v3.py
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from experiments.pilot.tasks import EVOLUTION_TASKS, SCENARIO, SYSTEM_PROMPT

PROXY_URL = "http://localhost:30000/v1"
MODEL = "gemini-2.5-pro"
SESSION_ID = "isd-evolution-v3"
RESULTS_DIR = Path(__file__).parent / "results_v3" / "evolution"


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key="metaclaw", base_url=PROXY_URL)
    system_prompt = SYSTEM_PROMPT + "\n\n모든 응답은 반드시 한국어로 작성하시오."

    total_tasks = len(EVOLUTION_TASKS)
    print(f"=== ISD Skill Evolution 실험 v3 ===")
    print(f"모델: {MODEL}")
    print(f"세션: {SESSION_ID}")
    print(f"태스크: {total_tasks}개")
    print(f"evolution_every_n_turns: 3 (3턴 후 첫 evolution)")
    print(f"=" * 35)

    for i, task in enumerate(EVOLUTION_TASKS):
        task_id = task["id"]
        title = task["title"]
        is_last = (i == total_tasks - 1)

        print(f"\n[{i+1}/{total_tasks}] {title} ({task_id})...")
        if is_last:
            print("  → 마지막 턴: session_done=True")

        user_prompt = task["prompt"].format(**SCENARIO)

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=8192,
                temperature=0.7,
                extra_body={
                    "session_id": SESSION_ID,
                    "turn_type": "main",
                    "session_done": is_last,
                },
            )
            response_text = response.choices[0].message.content or ""
        except Exception as e:
            print(f"  [오류] {e}")
            response_text = f"ERROR: {e}"

        result = {
            "task_id": task_id,
            "title": title,
            "task_index": i + 1,
            "total_tasks": total_tasks,
            "session_id": SESSION_ID,
            "turn_type": "main",
            "session_done": is_last,
            "prompt_sent": user_prompt,
            "response": response_text,
            "response_length": len(response_text),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
        }

        output_path = RESULTS_DIR / f"task{i+1}_{task_id}_response.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  완료 ({len(response_text):,}자) → {output_path.name}")

        # 3턴 후 evolution 트리거를 기다림
        if (i + 1) == 3:
            print("\n  ⏳ 3턴 완료 — evolution 트리거 대기 (5초)...")
            time.sleep(5)
            check_evolved_skills()

    # 세션 종료 후 최종 확인
    print("\n  ⏳ 세션 종료 — 최종 evolution 대기 (10초)...")
    time.sleep(10)

    print("\n=== 실험 완료 ===\n")
    check_evolved_skills()
    collect_artifacts()


def check_evolved_skills():
    """자동 합성된 skill 파일 확인."""
    skills_dir = Path.home() / ".metaclaw" / "skills"
    skill_files = list(skills_dir.glob("*/SKILL.md"))
    if skill_files:
        print(f"  ✓ 합성된 skill {len(skill_files)}개 발견:")
        for sf in skill_files:
            print(f"    - {sf.parent.name}")
    else:
        print("  ✗ 합성된 skill 없음")


def collect_artifacts():
    """evolution 결과물을 실험 디렉토리에 수집."""
    skills_dir = Path.home() / ".metaclaw" / "skills"
    artifacts_dir = RESULTS_DIR / "evolved_skills"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 합성된 skill 사본
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                dest = artifacts_dir / f"{skill_dir.name}.md"
                dest.write_text(skill_file.read_text())
                print(f"  수집: {skill_dir.name} → {dest.name}")

    # evolution history
    history_paths = [
        skills_dir / "evolution_history.jsonl",
        Path.home() / ".metaclaw" / "memory_data" / "skills" / "evolution_history.jsonl",
    ]
    for hp in history_paths:
        if hp.exists():
            dest = RESULTS_DIR / "evolution_history.jsonl"
            dest.write_text(hp.read_text())
            print(f"  수집: evolution_history.jsonl")
            break

    print(f"\n결과 저장 위치: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
