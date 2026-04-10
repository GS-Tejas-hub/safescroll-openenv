"""
SafeScroll Inference Script.

Runs an LLM agent against the SafeScroll Content Moderation environment
using the mandatory hackathon format.

Environment variables:
    API_BASE_URL  - The API endpoint for the LLM
    MODEL_NAME    - The model identifier
    HF_TOKEN      - API key for authentication

Usage:
    API_BASE_URL=https://api.openai.com/v1 MODEL_NAME=gpt-4o-mini HF_TOKEN=sk-... python inference.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

# --- Configuration from environment ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional — if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

BENCHMARK = "safescroll_env"
IMAGE_NAME = "openenv-safescroll:latest"
TASK_NAMES = ["easy", "medium", "hard"]
MAX_STEPS = 5  # Max steps per episode (hard tasks have 3)
EPISODES_PER_TASK = 3
SUCCESS_SCORE_THRESHOLD = 0.5

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
# Structured logging (mandatory hackathon format)
# ---------------------------------------------------------------------------

def log_start(task: str, env: str, model: str):
    """Emit a [START] log line with task, env, and model info."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None):
    """Emit a [STEP] log line after each environment step."""
    parts = [f"[STEP] step={step}", f"action={action}", f"reward={reward:.4f}", f"done={str(done).lower()}"]
    if error:
        # Replace spaces in error to keep key=value parsing simple
        safe_error = str(error).replace(" ", "_")
        parts.append(f"error={safe_error}")
    print(" ".join(parts), flush=True)


def log_end(task: str, success: bool, steps: int, score: float, rewards: List[float]):
    """Emit an [END] log line with final results."""
    rewards_str = ",".join(f"{r:.4f}" for r in rewards)
    print(
        f"[END] task={task} success={str(success).lower()} steps={steps} score={score:.4f} rewards={rewards_str}",
        flush=True,
    )


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
# Convert observation object to dict for prompt building
# ---------------------------------------------------------------------------

def obs_to_dict(obs) -> Dict[str, Any]:
    """Convert a ModerationObservation into a plain dict for prompt building."""
    return {
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


# ---------------------------------------------------------------------------
# Run a single episode (direct SafeScrollEnvironment -- synchronous)
# ---------------------------------------------------------------------------

def run_episode_direct(
    env,
    client: OpenAI,
    task_id: str,
    seed: int,
) -> Dict[str, Any]:
    """Run one complete episode using the local SafeScrollEnvironment and return results."""
    obs = env.reset(seed=seed, task_id=task_id)
    obs_dict = obs_to_dict(obs)

    total_reward = 0.0
    step_num = 0
    step_rewards: List[float] = []

    while not obs.done:
        prompt = build_user_prompt(obs_dict)
        error_msg = None

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=500,
            )
            llm_text = response.choices[0].message.content or ""
        except Exception as e:
            error_msg = str(e)
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
        step_num += 1

        step_reward = obs.reward if obs.reward is not None else 0.0
        step_rewards.append(step_reward)
        total_reward = obs.reward if obs.done else total_reward

        # Log this step
        log_step(
            step=step_num,
            action=action.decision,
            reward=step_reward,
            done=obs.done,
            error=error_msg,
        )

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
        "score": obs.reward if obs.reward is not None else 0.0,
        "total_reward": state.total_reward,
        "steps": step_num,
        "decisions": state.decisions_made,
        "step_rewards": step_rewards,
    }


# ---------------------------------------------------------------------------
# Run a single episode (async client -- from_docker_image path)
# ---------------------------------------------------------------------------

async def run_episode_async(
    env,
    client: OpenAI,
    task_id: str,
    seed: int,
) -> Dict[str, Any]:
    """Run one complete episode using the async SafeScrollEnv client."""
    result = await env.reset(task_id=task_id)
    obs = result.observation

    obs_dict = obs_to_dict(obs)

    total_reward = 0.0
    step_num = 0
    step_rewards: List[float] = []

    while not obs.done:
        prompt = build_user_prompt(obs_dict)
        error_msg = None

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=500,
            )
            llm_text = response.choices[0].message.content or ""
        except Exception as e:
            error_msg = str(e)
            llm_text = json.dumps({
                "decision": "flag_review",
                "severity": "medium",
                "category": "safe",
                "reasoning": f"API error: {e}",
                "account_action": "none",
                "escalate_to": "none",
            })

        action = parse_llm_response(llm_text)
        result = await env.step(action)
        obs = result.observation
        step_num += 1

        step_reward = result.reward if result.reward is not None else 0.0
        step_rewards.append(step_reward)
        total_reward = result.reward if result.done else total_reward

        # Log this step
        log_step(
            step=step_num,
            action=action.decision,
            reward=step_reward,
            done=result.done,
            error=error_msg,
        )

        # Update obs_dict for next step
        obs_dict.update({
            "message_history": [m for m in obs.message_history] if obs.message_history else None,
            "step_count": obs.step_count,
            "feedback": obs.feedback,
        })

    state = await env.state()
    return {
        "scenario_id": state.scenario_id,
        "task_id": task_id,
        "score": result.reward if result.reward is not None else 0.0,
        "total_reward": state.total_reward,
        "steps": step_num,
        "decisions": state.decisions_made,
        "step_rewards": step_rewards,
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    """Run the SafeScroll inference agent across all tasks."""
    if not HF_TOKEN:
        print(
            "ERROR: No API key found. Set HF_TOKEN environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    # ------------------------------------------------------------------
    # Try async client (from_docker_image), fall back to direct env
    # ------------------------------------------------------------------
    use_docker = False
    env = None

    # Determine which docker image to use (validator passes via LOCAL_IMAGE_NAME)
    image_name = LOCAL_IMAGE_NAME or IMAGE_NAME

    try:
        from client import SafeScrollEnv

        env = await SafeScrollEnv.from_docker_image(image_name)
        use_docker = True
        print(f"[INFO] Using async client via docker image: {image_name}", flush=True)
    except Exception as docker_err:
        # Fall back to direct local environment
        print(f"[INFO] from_docker_image failed ({docker_err}), falling back to direct env", flush=True)
        from server.safescroll_env_environment import SafeScrollEnvironment

        env = SafeScrollEnvironment()
        use_docker = False
        print("[INFO] Using direct SafeScrollEnvironment (local)", flush=True)

    print(f"[INFO] Model: {MODEL_NAME}", flush=True)
    print(f"[INFO] API Base: {API_BASE_URL}", flush=True)
    print(f"[INFO] Tasks: {TASK_NAMES}", flush=True)
    print(f"[INFO] Episodes per task: {EPISODES_PER_TASK}", flush=True)
    print("=" * 60, flush=True)

    all_results: Dict[str, List[Dict[str, Any]]] = {}
    overall_scores: List[float] = []
    start_time = time.time()

    for task_id in TASK_NAMES:
        log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

        task_results: List[Dict[str, Any]] = []
        task_rewards: List[float] = []

        for episode_idx in range(EPISODES_PER_TASK):
            seed = episode_idx * 7 + hash(task_id) % 100  # Reproducible seeds

            try:
                if use_docker:
                    result = await run_episode_async(env, client, task_id, seed)
                else:
                    result = run_episode_direct(env, client, task_id, seed)

                task_results.append(result)
                episode_score = result["score"]
                task_rewards.append(episode_score)
                overall_scores.append(episode_score)

                print(
                    f"  [{task_id}] ep={episode_idx + 1}/{EPISODES_PER_TASK} "
                    f"scenario={result['scenario_id']} "
                    f"score={episode_score:.3f} "
                    f"steps={result['steps']} "
                    f"decisions={result['decisions']}",
                    flush=True,
                )

            except Exception as e:
                print(
                    f"  [{task_id}] ep={episode_idx + 1}/{EPISODES_PER_TASK} ERROR: {e}",
                    file=sys.stderr,
                    flush=True,
                )
                task_rewards.append(0.0)
                overall_scores.append(0.0)

        # End-of-task summary
        avg_score = sum(task_rewards) / len(task_rewards) if task_rewards else 0.0
        task_success = avg_score >= SUCCESS_SCORE_THRESHOLD

        log_end(
            task=task_id,
            success=task_success,
            steps=sum(r.get("steps", 0) for r in task_results),
            score=round(avg_score, 4),
            rewards=task_rewards,
        )

        all_results[task_id] = task_results
        print(f"  [{task_id}] Average score: {avg_score:.3f}\n", flush=True)

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    elapsed = time.time() - start_time
    overall_avg = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0

    print("=" * 60, flush=True)
    print("FINAL RESULTS", flush=True)
    print("=" * 60, flush=True)
    for task_id in TASK_NAMES:
        if task_id in all_results:
            scores = [r["score"] for r in all_results[task_id]]
            avg = sum(scores) / len(scores) if scores else 0.0
            mn = min(scores) if scores else 0.0
            mx = max(scores) if scores else 0.0
            print(
                f"  {task_id:8s}: avg={avg:.3f}  min={mn:.3f}  max={mx:.3f}  (n={len(scores)})",
                flush=True,
            )
    print(
        f"  {'overall':8s}: avg={overall_avg:.3f}  (n={len(overall_scores)})",
        flush=True,
    )
    print(f"\nCompleted in {elapsed:.1f}s", flush=True)

    # Clean up async client if used
    if use_docker and env is not None:
        try:
            await env.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
