"""
SafeScroll Interactive Test Script.

Run this to play through scenarios yourself and see how the environment
grades your decisions. Works against both local and remote servers.

Usage:
    python test_interactive.py
    python test_interactive.py --task medium
    python test_interactive.py --task hard --url http://localhost:8000
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import ModerationAction
from server.safescroll_env_environment import SafeScrollEnvironment


def print_scenario(obs):
    """Pretty-print the scenario for the user."""
    print()
    print("=" * 70)
    print(f"  SCENARIO: {obs.scenario_id}  |  Task: {obs.task_id}  |  Step {obs.step_count}/{obs.max_steps}")
    print("=" * 70)
    print(f"  Platform:  {obs.platform}")
    print(f"  Community: {obs.community_context}")
    print(f"  Type:      {obs.content_type}")
    print()
    print(f"  CONTENT:")
    print(f"  {obs.content_text}")
    print()

    poster = obs.poster_profile
    if poster:
        print(f"  POSTER: @{poster.get('username', '?')}")
        print(f"    Age: {poster.get('age', '?')} | Account: {poster.get('account_age_days', '?')} days")
        print(f"    Followers: {poster.get('followers', '?')} | Following: {poster.get('following', '?')}")
        print(f"    Posts: {poster.get('posts', '?')} | Verified: {poster.get('verified', False)}")
        if poster.get('bio'):
            print(f"    Bio: {poster['bio']}")
        if poster.get('following_minors_count'):
            print(f"    Following minors: {poster['following_minors_count']}")

    target = obs.target_user_profile
    if target:
        print()
        print(f"  TARGET: @{target.get('username', '?')}")
        print(f"    Age: {target.get('age', '?')} | Minor: {target.get('is_minor', '?')}")
        if target.get('bio'):
            print(f"    Bio: {target['bio']}")

    reporter = obs.reporter_info
    if reporter:
        print()
        print(f"  REPORTED BY: {reporter.get('type', '?')} | Reason: {reporter.get('reason', '?')}")

    if obs.message_history:
        print()
        print(f"  CONVERSATION ({len(obs.message_history)} messages):")
        for msg in obs.message_history:
            print(f"    [{msg['sender']}]: {msg['text']}")

    if obs.feedback and obs.step_count > 0:
        print()
        print(f"  PREVIOUS FEEDBACK: {obs.feedback}")

    print()
    print("-" * 70)


def get_user_decision():
    """Prompt the user for their moderation decision."""
    print()
    print("  YOUR DECISION:")
    print("    Decisions:  approve | remove | flag_review | escalate")
    print("    Severities: none | low | medium | high | critical")
    print("    Categories: safe | spam | hate_speech | harassment | explicit_adult")
    print("                violence_graphic | child_exploitation | grooming")
    print("                self_harm | misinformation | impersonation | privacy_violation")
    print()

    decision = input("  Decision:       ").strip() or "flag_review"
    severity = input("  Severity:       ").strip() or "medium"
    category = input("  Category:       ").strip() or "safe"
    reasoning = input("  Reasoning:      ").strip() or "No reasoning provided"
    account_action = input("  Account action (none/warn/restrict/suspend): ").strip() or "none"
    escalate_to = input("  Escalate to (none/human_review/child_safety_team/law_enforcement): ").strip() or "none"

    return ModerationAction(
        decision=decision,
        severity=severity,
        category=category,
        reasoning=reasoning,
        account_action=account_action,
        escalate_to=escalate_to,
    )


def print_result(obs):
    """Print the grading result."""
    print()
    print("=" * 70)
    print(f"  RESULT")
    print("=" * 70)
    print(f"  Score:    {obs.reward:.3f}")
    print(f"  Done:     {obs.done}")
    print()
    print(f"  Feedback: {obs.feedback}")
    print()
    if obs.reward_breakdown:
        print(f"  Breakdown:")
        for k, v in obs.reward_breakdown.items():
            bar = "#" * int(max(0, v) * 20)
            print(f"    {k:30s} {v:+.3f}  {bar}")
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SafeScroll Interactive Test")
    parser.add_argument("--task", default="easy", choices=["easy", "medium", "hard"])
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    env = SafeScrollEnvironment()

    print()
    print("  SafeScroll Interactive Test")
    print(f"  Task: {args.task}")
    print()

    kwargs = {"task_id": args.task}
    if args.seed is not None:
        kwargs["seed"] = args.seed

    obs = env.reset(**kwargs)
    print_scenario(obs)

    while not obs.done:
        action = get_user_decision()
        obs = env.step(action)
        print_result(obs)

        if not obs.done:
            print_scenario(obs)

    print()
    state = env.state
    print(f"  Episode complete!")
    print(f"  Total reward: {state.total_reward:.3f}")
    print(f"  Decisions made: {state.decisions_made}")
    print()

    again = input("  Play another? (y/n): ").strip().lower()
    if again == "y":
        main()


if __name__ == "__main__":
    main()
