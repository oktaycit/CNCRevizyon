#!/usr/bin/env python3
"""Submit a goal into the Raspberry Pi goal queue."""

import argparse
import json

from pi_agent_runner import submit_goal


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit a goal to the Pi agent queue")
    parser.add_argument("--title", required=True, help="Kısa hedef başlığı")
    parser.add_argument("--prompt", required=True, help="Hedef açıklaması")
    parser.add_argument(
        "--goal-type",
        default="ai",
        choices=["ai", "simulator_check"],
        help="Hedef tipi",
    )
    parser.add_argument(
        "--mode",
        default="parallel",
        choices=["single", "parallel", "voting", "aggregate"],
        help="AI çalışma modu",
    )
    parser.add_argument("--task-type", default=None, help="code/debug/review gibi yönlendirme etiketi")
    args = parser.parse_args()

    goal = submit_goal(
        title=args.title,
        prompt=args.prompt,
        goal_type=args.goal_type,
        mode=args.mode,
        task_type=args.task_type,
    )
    print(json.dumps(goal, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
