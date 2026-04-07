# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
SafeScroll Content Moderation Environment.

Trains AI agents to make nuanced, context-aware content moderation
decisions across social media platforms. Supports three difficulty levels:

- Easy:   Obvious content classification (spam, hate speech, safe content)
- Medium: Context-dependent moderation (same text, different contexts)
- Hard:   Multi-step grooming/exploitation detection (conversation unfolds)

Each episode presents the agent with reported content and context.
The agent must decide: approve, remove, flag for review, or escalate —
along with severity, category, reasoning, and account/escalation actions.
"""

import random
from typing import Any, Dict, List, Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment

try:
    from ..models import (
        VALID_CATEGORIES,
        VALID_DECISIONS,
        VALID_SEVERITIES,
        VALID_TASK_IDS,
        ModerationAction,
        ModerationObservation,
        SafeScrollState,
    )
    from .graders import GradeResult, HardGrader, get_grader
    from .rewards import RewardShaper
    from .scenarios import SCENARIOS
except ImportError:
    from models import (
        VALID_CATEGORIES,
        VALID_DECISIONS,
        VALID_SEVERITIES,
        VALID_TASK_IDS,
        ModerationAction,
        ModerationObservation,
        SafeScrollState,
    )
    from server.graders import GradeResult, HardGrader, get_grader
    from server.rewards import RewardShaper
    from server.scenarios import SCENARIOS


# ---------------------------------------------------------------------------
# SafeScroll Environment
# ---------------------------------------------------------------------------

class SafeScrollEnvironment(Environment):
    """
    Content Moderation & Child Safety training environment.

    Presents AI agents with reported social media content and evaluates
    their moderation decisions against expert-labeled ground truth.

    Three difficulty levels:
        - easy:   Obvious violations or clearly safe content (1 step)
        - medium: Context-dependent decisions (1 step)
        - hard:   Multi-step conversation analysis (3-5 steps)
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self) -> None:
        self._state = SafeScrollState(episode_id=str(uuid4()), step_count=0)
        self._current_scenario: Optional[Dict[str, Any]] = None
        self._current_task_id: str = "easy"
        self._episode_rewards: List[float] = []
        self._current_step_in_conversation: int = 0
        self._step_grade_results: List[GradeResult] = []
        self._last_grade_result: Optional[GradeResult] = None
        self._reward_shaper = RewardShaper()
        self._rng = random.Random()

    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs: Any) -> ModerationObservation:
        """
        Start a new moderation episode.

        Accepts an optional `task_id` kwarg ("easy", "medium", or "hard")
        to select the difficulty level.  A random scenario is drawn from
        the matching pool.
        """
        task_id = kwargs.get("task_id", "easy")
        if task_id not in VALID_TASK_IDS:
            task_id = "easy"

        if seed is not None:
            self._rng = random.Random(seed)

        scenario_pool = SCENARIOS.get(task_id, SCENARIOS["easy"])
        scenario = self._rng.choice(scenario_pool)

        self._current_scenario = scenario
        self._current_task_id = task_id
        self._episode_rewards = []
        self._current_step_in_conversation = 0
        self._step_grade_results = []
        self._last_grade_result = None

        self._state = SafeScrollState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            task_id=task_id,
            scenario_id=scenario["scenario_id"],
            total_reward=0.0,
            decisions_made=[],
        )

        return self._build_observation(
            done=False,
            reward=None,
            feedback="Review the reported content and provide your moderation decision.",
            reward_breakdown=None,
        )

    def step(self, action: ModerationAction, **kwargs: Any) -> ModerationObservation:  # type: ignore[override]
        """
        Process the agent's moderation decision and return graded feedback.

        Workflow:
        1. Validate and grade the action via RewardShaper
        2. For hard tasks: accumulate per-step grades, compute episode
           aggregate on the final step
        3. Return observation with reward, breakdown, and feedback

        The RewardShaper adds input validation penalties, consistency
        bonuses, and asymmetric safety weighting on top of the raw
        grader scores.
        """
        if self._current_scenario is None:
            return ModerationObservation(
                done=True,
                reward=0.0,
                feedback="Error: No active episode. Call reset() first.",
            )

        self._state.step_count += 1
        self._state.decisions_made.append(action.decision)
        self._current_step_in_conversation += 1

        gt = self._current_scenario["ground_truth"]
        max_steps = self._current_scenario.get("max_steps", 1)
        done = self._state.step_count >= max_steps

        if self._current_task_id == "hard":
            # Multi-step: grade this step, accumulate
            step_idx = self._state.step_count - 1
            step_output = self._reward_shaper.compute_step_reward(
                action, gt, self._current_task_id, step_idx,
            )
            # Store the underlying GradeResult for episode aggregation
            grader = get_grader(self._current_task_id)
            if isinstance(grader, HardGrader):
                step_grade = grader.grade_step(action, gt, step_idx)
                self._step_grade_results.append(step_grade)
                self._last_grade_result = step_grade

            if done:
                # Final step: compute episode-level reward
                episode_output = self._reward_shaper.compute_episode_reward(
                    self._step_grade_results,
                    gt,
                    self._current_task_id,
                    self._state.decisions_made,
                    max_steps,
                )
                reward = episode_output.reward
                breakdown = episode_output.breakdown
                feedback = episode_output.feedback
            else:
                reward = step_output.reward
                breakdown = step_output.breakdown
                feedback = step_output.feedback
        else:
            # Single-step (easy/medium)
            reward_output = self._reward_shaper.compute_reward(
                action, gt, self._current_task_id,
            )
            reward = reward_output.reward
            breakdown = reward_output.breakdown
            feedback = reward_output.feedback
            self._last_grade_result = GradeResult(
                score=reward, breakdown=breakdown, feedback=feedback,
                is_critical_miss=reward_output.is_critical_miss,
            )

        self._episode_rewards.append(reward)
        self._state.total_reward += reward

        return self._build_observation(
            done=done,
            reward=reward,
            feedback=feedback,
            reward_breakdown=breakdown,
        )

    @property
    def state(self) -> SafeScrollState:
        """Return current episode metadata."""
        return self._state

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_observation(
        self,
        done: bool,
        reward: Optional[float],
        feedback: str,
        reward_breakdown: Optional[Dict[str, float]],
    ) -> ModerationObservation:
        """Construct the observation the agent will receive."""
        scenario = self._current_scenario
        if scenario is None:
            return ModerationObservation(done=True, reward=0.0, feedback=feedback)

        message_history = None
        if scenario.get("message_history") is not None:
            step_idx = min(
                self._current_step_in_conversation,
                len(scenario["message_history"]),
            )
            revealed: List[Dict] = []
            for i in range(step_idx):
                revealed.extend(scenario["message_history"][i])
            message_history = revealed if revealed else None

        return ModerationObservation(
            done=done,
            reward=reward,
            content_text=scenario["content_text"],
            content_type=scenario["content_type"],
            platform=scenario["platform"],
            community_context=scenario["community_context"],
            poster_profile=scenario["poster_profile"],
            target_user_profile=scenario.get("target_user_profile"),
            reporter_info=scenario["reporter_info"],
            message_history=message_history,
            task_id=self._current_task_id,
            scenario_id=scenario["scenario_id"],
            step_count=self._state.step_count,
            max_steps=scenario.get("max_steps", 1),
            feedback=feedback,
            reward_breakdown=reward_breakdown,
        )

    @property
    def last_grade_result(self) -> Optional[GradeResult]:
        """Return the most recent grading result (used by /grader endpoint)."""
        return self._last_grade_result
