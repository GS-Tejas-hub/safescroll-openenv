#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
SafeScroll Baseline Helper (used by /baseline HTTP endpoint).

This module provides the `run_baseline()` function that the FastAPI
`/baseline` endpoint calls when judges trigger a baseline run via HTTP.

NOTE: For the official hackathon evaluation, the canonical entry point
is `inference.py` at the repo root (which emits the mandatory
[START]/[STEP]/[END] structured logs). This file exists as a
programmatic helper for the HTTP `/baseline` endpoint that returns
JSON-shaped baseline scores.

Usage (CLI):
    export OPENAI_API_KEY=sk-...
    python baseline.py
    python baseline.py --model gpt-4o-mini --episodes 5
    python baseline.py --task easy

Requirements:
    pip install openai python-dotenv
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Load .env before anything else
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI

# ---------------------------------------------------------------------------
# Ensure local imports work
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from models import (
    VALID_ACCOUNT_ACTIONS,
    VALID_CATEGORIES,
    VALID_DECISIONS,
    VALID_ESCALATION_TARGETS,
    VALID_SEVERITIES,
    ModerationAction,
)
from server.safescroll_env_environment import SafeScrollEnvironment


# ---------------------------------------------------------------------------
# System prompt for the LLM
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert content moderator for a social media platform.
You will be given reported content along with context (platform, community, poster profile, target profile, reporter info, and optionally a conversation history).

You must provide a JSON moderation decision with these exact fields:
{
    "decision": "approve" | "remove" | "flag_review" | "escalate",
    "severity": "none" | "low" | "medium" | "high" | "critical",
    "category": one of ["safe","spam","hate_speech","harassment","explicit_adult","violence_graphic","child_exploitation","grooming","self_harm","misinformation","impersonation","privacy_violation"],
    "reasoning": "Your detailed explanation of why you made this decision, referencing specific context factors",
    "account_action": "none" | "warn" | "restrict" | "suspend",
    "escalate_to": "none" | "human_review" | "child_safety_team" | "law_enforcement"
}

Guidelines:
- Consider the CONTEXT carefully: platform, community, who posted it, who is the target
- The same content can be safe in one context and harmful in another
- Child safety is the highest priority. When in doubt about potential grooming or exploitation, escalate
- Provide detailed reasoning that references specific context factors you considered
- For multi-step conversations, assess the FULL pattern, not just individual messages

Respond with ONLY the JSON object. No markdown, no explanation outside the JSON."""


# ---------------------------------------------------------------------------
# Build user prompt from observation
# ---------------------------------------------------------------------------

def build_user_prompt(obs_dict: Dict[str, Any]) -> str:
    """Convert an observation dictionary into a structured prompt for the LLM."""
    lines = ["## Reported Content for Review\n"]

    lines.append(f"**Content Type:** {obs_dict.get('content_type', 'post')}")
    lines.append(f"**Platform:** {obs_dict.get('platform', 'unknown')}")
    lines.append(f"**Community:** {obs_dict.get('community_context', 'general')}")
    lines.append(f"\n**Content Text:**\n{obs_dict.get('content_text', '')}\n")

    # Poster profile
    poster = obs_dict.get("poster_profile", {})
    if poster:
        lines.append("**Poster Profile:**")
        for k, v in poster.items():
            lines.append(f"  - {k}: {v}")

    # Target profile (for DMs)
    target = obs_dict.get("target_user_profile")
    if target:
        lines.append("\n**Target User Profile:**")
        for k, v in target.items():
            lines.append(f"  - {k}: {v}")

    # Reporter info
    reporter = obs_dict.get("reporter_info", {})
    if reporter:
        lines.append("\n**Reporter Info:**")
        for k, v in reporter.items():
            lines.append(f"  - {k}: {v}")

    # Message history (for multi-step / hard tasks)
    messages = obs_dict.get("message_history")
    if messages:
        lines.append("\n**Conversation History:**")
        for msg in messages:
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")
            lines.append(f"  [{sender}]: {text}")

    # Feedback from previous step
    feedback = obs_dict.get("feedback", "")
    if feedback and obs_dict.get("step_count", 0) > 0:
        lines.append(f"\n**Previous Step Feedback:** {feedback}")

    lines.append(f"\n**Task:** {obs_dict.get('task_id', 'easy')}")
    lines.append(f"**Step:** {obs_dict.get('step_count', 0) + 1} of {obs_dict.get('max_steps', 1)}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Parse LLM response into a ModerationAction
# ---------------------------------------------------------------------------

def parse_llm_response(text: str) -> ModerationAction:
    """Parse the LLM's JSON response into a ModerationAction, with fallbacks."""
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                data = json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

    def safe_get(key: str, valid: list, default: str) -> str:
        val = data.get(key, default)
        return val if val in valid else default

    return ModerationAction(
        decision=safe_get("decision", VALID_DECISIONS, "flag_review"),
        severity=safe_get("severity", VALID_SEVERITIES, "medium"),
        category=safe_get("category", VALID_CATEGORIES, "safe"),
        reasoning=data.get("reasoning", "No reasoning provided"),
        account_action=safe_get("account_action", VALID_ACCOUNT_ACTIONS, "none"),
        escalate_to=safe_get("escalate_to", VALID_ESCALATION_TARGETS, "none"),
    )


# ---------------------------------------------------------------------------
# Run a single episode
# ---------------------------------------------------------------------------

def run_episode(
    env: SafeScrollEnvironment,
    client: OpenAI,
    model: str,
    task_id: str,
    seed: int,
) -> Dict[str, Any]:
    """Run one complete episode and return results."""
    obs = env.reset(seed=seed, task_id=task_id)

    obs_dict = {
        "content_text": obs.content_text,
        "content_type": obs.content_type,
        "platform": obs.platform,
        "community_context": obs.community_context,
        "poster_profile": obs.poster_profile,
        "target_user_profile": obs.target_user_profile,
        "reporter_info": obs.reporter_info,
        "message_history": [m for m in obs.message_history] if obs.message_history else None,
        "task_id": obs.task_id,
        "scenario_id": obs.scenario_id,
        "step_count": obs.step_count,
        "max_steps": obs.max_steps,
        "feedback": obs.feedback,
    }

    total_reward = 0.0
    steps = 0

    while not obs.done:
        prompt = build_user_prompt(obs_dict)

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=500,
            )
            llm_text = response.choices[0].message.content or ""
        except Exception as e:
            llm_text = json.dumps({
                "decision": "flag_review",
                "severity": "medium",
                "category": "safe",
                "reasoning": f"API error: {e}",
                "account_action": "none",
                "escalate_to": "none",
            })

        action = parse_llm_response(llm_text)
        obs = env.step(action)
        steps += 1
        total_reward = obs.reward if obs.done else total_reward

        # Update obs_dict for next step (multi-step episodes)
        obs_dict.update({
            "message_history": [m for m in obs.message_history] if obs.message_history else None,
            "step_count": obs.step_count,
            "feedback": obs.feedback,
        })

    state = env.state
    return {
        "scenario_id": state.scenario_id,
        "task_id": task_id,
        "score": obs.reward,
        "total_reward": state.total_reward,
        "steps": steps,
        "decisions": state.decisions_made,
    }


# ---------------------------------------------------------------------------
# Run baseline across all tasks
# ---------------------------------------------------------------------------

def run_baseline(
    model: str = "gpt-4o-mini",
    tasks: Optional[List[str]] = None,
    episodes_per_task: int = 5,
) -> Dict[str, Any]:
    """
    Run the baseline agent against SafeScroll and report scores.

    Returns a dict with per-task and aggregate scores.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not set. "
            "Set it as an environment variable or in a .env file."
        )

    client = OpenAI(api_key=api_key)
    env = SafeScrollEnvironment()

    if tasks is None:
        tasks = ["easy", "medium", "hard"]

    results: Dict[str, Any] = {}

    for task_id in tasks:
        task_results = []
        for i in range(episodes_per_task):
            seed = i * 7 + hash(task_id) % 100  # Reproducible seeds
            result = run_episode(env, client, model, task_id, seed)
            task_results.append(result)
            print(
                f"  [{task_id}] {result['scenario_id']}: "
                f"score={result['score']:.3f} "
                f"decisions={result['decisions']}"
            )

        scores = [r["score"] for r in task_results]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        results[task_id] = {
            "avg_score": round(avg_score, 4),
            "min_score": round(min(scores), 4) if scores else 0.0,
            "max_score": round(max(scores), 4) if scores else 0.0,
            "episodes": len(task_results),
            "details": task_results,
        }
        print(f"  [{task_id}] Average: {avg_score:.3f}\n")

    # Aggregate
    all_scores = [
        r["score"]
        for task_data in results.values()
        for r in task_data["details"]
    ]
    results["aggregate"] = {
        "avg_score": round(sum(all_scores) / len(all_scores), 4) if all_scores else 0.0,
        "total_episodes": len(all_scores),
    }

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="SafeScroll Baseline - run an LLM agent against all tasks"
    )
    parser.add_argument(
        "--model", default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--task", default=None, choices=["easy", "medium", "hard"],
        help="Run only a specific task (default: all)"
    )
    parser.add_argument(
        "--episodes", type=int, default=5,
        help="Episodes per task (default: 5)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Save results to JSON file"
    )
    args = parser.parse_args()

    tasks = [args.task] if args.task else None

    print(f"SafeScroll Baseline")
    print(f"Model: {args.model}")
    print(f"Episodes per task: {args.episodes}")
    print("=" * 50)

    start = time.time()
    results = run_baseline(
        model=args.model,
        tasks=tasks,
        episodes_per_task=args.episodes,
    )
    elapsed = time.time() - start

    print("=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    for task_id in ["easy", "medium", "hard"]:
        if task_id in results:
            data = results[task_id]
            print(f"  {task_id:8s}: avg={data['avg_score']:.3f}  min={data['min_score']:.3f}  max={data['max_score']:.3f}  (n={data['episodes']})")
    if "aggregate" in results:
        print(f"  {'overall':8s}: avg={results['aggregate']['avg_score']:.3f}  (n={results['aggregate']['total_episodes']})")
    print(f"\nCompleted in {elapsed:.1f}s")

    if args.output:
        # Remove detailed episode data for clean output
        clean = {}
        for k, v in results.items():
            if isinstance(v, dict) and "details" in v:
                clean[k] = {kk: vv for kk, vv in v.items() if kk != "details"}
            else:
                clean[k] = v
        with open(args.output, "w") as f:
            json.dump(clean, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
