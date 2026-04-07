# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
SafeScroll Reward System.

Transforms raw grader scores into rich, RL-appropriate training signals.
The reward system sits between the graders and the environment, adding:

    1. Input validation penalties  (invalid fields, empty reasoning)
    2. Asymmetric safety weighting (missing child harm >> false positive)
    3. Multi-step trajectory shaping (consistency bonus, progressive signal)
    4. Informative breakdown        (agents see WHY they scored what they did)

Design principle: A reward should teach the agent not just WHAT was wrong,
but WHERE in the decision process the error occurred, and whether the
mistake was dangerous (child safety) or merely inaccurate (wrong severity).

All rewards are clamped to [0.0, 1.0] for the final score returned
to the agent.  The breakdown dict preserves unclamped signal values
so that RL training can use shaped rewards with richer gradients.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .graders import (
    EasyGrader,
    EpisodeGradeResult,
    GradeResult,
    HardGrader,
    MediumGrader,
    get_grader,
)

try:
    from ..models import (
        VALID_ACCOUNT_ACTIONS,
        VALID_CATEGORIES,
        VALID_DECISIONS,
        VALID_ESCALATION_TARGETS,
        VALID_SEVERITIES,
        ModerationAction,
    )
except ImportError:
    from models import (
        VALID_ACCOUNT_ACTIONS,
        VALID_CATEGORIES,
        VALID_DECISIONS,
        VALID_ESCALATION_TARGETS,
        VALID_SEVERITIES,
        ModerationAction,
    )


# ---------------------------------------------------------------------------
# Reward output container
# ---------------------------------------------------------------------------

@dataclass
class RewardOutput:
    """Full reward signal returned to the environment."""

    reward: float                          # Clamped [0.0, 1.0] for the agent
    raw_reward: float                      # Unclamped for RL training use
    breakdown: Dict[str, float]            # Per-signal decomposition
    feedback: str                          # Human-readable explanation
    is_critical_miss: bool = False         # True if child-safety was missed
    validation_penalties: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def _validate_action(action: ModerationAction) -> Dict[str, float]:
    """
    Check the action for invalid or missing fields and return penalties.

    Returns a dict of penalty_name -> penalty_value (all <= 0).
    An empty dict means the action is fully valid.
    """
    penalties: Dict[str, float] = {}

    # Empty or trivially short reasoning
    reasoning = action.reasoning.strip()
    if len(reasoning) == 0:
        penalties["empty_reasoning"] = -0.15
    elif len(reasoning) < 20:
        penalties["shallow_reasoning"] = -0.05

    # Invalid enum values (graceful degradation, not crash)
    if action.decision not in VALID_DECISIONS:
        penalties["invalid_decision"] = -0.20
    if action.severity not in VALID_SEVERITIES:
        penalties["invalid_severity"] = -0.05
    if action.category not in VALID_CATEGORIES:
        penalties["invalid_category"] = -0.10
    if action.account_action not in VALID_ACCOUNT_ACTIONS:
        penalties["invalid_account_action"] = -0.03
    if action.escalate_to not in VALID_ESCALATION_TARGETS:
        penalties["invalid_escalation"] = -0.03

    return penalties


# ---------------------------------------------------------------------------
# Reward shaping for multi-step episodes
# ---------------------------------------------------------------------------

def _consistency_bonus(decisions: List[str], gt_decision: str) -> float:
    """
    Bonus for maintaining a consistent and appropriate assessment direction
    across multi-step episodes.

    If the ground truth is 'escalate' and the agent consistently flags or
    escalates (never approves after flagging), that shows systematic
    detection capability -- worth a small bonus.
    """
    if len(decisions) < 2:
        return 0.0

    decision_rank = {"approve": 0, "flag_review": 1, "remove": 1, "escalate": 2}

    ranks = [decision_rank.get(d, 0) for d in decisions]

    # Check if the agent never "retreated" (went from flag -> approve)
    monotonic = all(ranks[i] <= ranks[i + 1] for i in range(len(ranks) - 1))

    if gt_decision in ("escalate", "flag_review"):
        # For harmful content: reward monotonically increasing vigilance
        if monotonic and ranks[-1] >= 1:
            return 0.05
    elif gt_decision == "approve":
        # For safe content: reward consistent approval (not flip-flopping)
        if all(r == 0 for r in ranks):
            return 0.05

    return 0.0


# ---------------------------------------------------------------------------
# RewardShaper — the main entry point
# ---------------------------------------------------------------------------

class RewardShaper:
    """
    Transforms grader output into RL training signals.

    Usage:
        shaper = RewardShaper()

        # Single-step (easy/medium)
        output = shaper.compute_reward(action, ground_truth, task_id)

        # Multi-step (hard) — per-step
        output = shaper.compute_step_reward(action, ground_truth, task_id, step_idx)

        # Multi-step (hard) — episode aggregate
        output = shaper.compute_episode_reward(
            step_outputs, ground_truth, task_id, decisions_made
        )
    """

    def compute_reward(
        self,
        action: ModerationAction,
        ground_truth: Dict[str, Any],
        task_id: str,
    ) -> RewardOutput:
        """
        Compute the full reward for a single-step episode (easy/medium).

        1. Validate the action
        2. Run the task-specific grader
        3. Apply validation penalties
        4. Build the informative breakdown
        """
        # Step 1: Validate
        penalties = _validate_action(action)

        # Step 2: Grade
        grader = get_grader(task_id)
        grade_result: GradeResult = grader.grade(action, ground_truth)

        # Step 3: Apply penalties
        total_penalty = sum(penalties.values())
        raw_reward = grade_result.score + total_penalty
        clamped_reward = max(0.0, min(1.0, raw_reward))

        # Step 4: Build breakdown
        breakdown = {**grade_result.breakdown}
        for k, v in penalties.items():
            breakdown[k] = v

        # Enrich feedback with validation issues
        feedback = grade_result.feedback
        if penalties:
            penalty_msgs = []
            if "empty_reasoning" in penalties:
                penalty_msgs.append("Penalty: empty reasoning provided")
            if "shallow_reasoning" in penalties:
                penalty_msgs.append("Penalty: reasoning too brief (< 20 chars)")
            if any(k.startswith("invalid_") for k in penalties):
                invalid = [k.replace("invalid_", "") for k in penalties if k.startswith("invalid_")]
                penalty_msgs.append(f"Penalty: invalid field values for {', '.join(invalid)}")
            feedback = feedback + " " + " ".join(penalty_msgs)

        return RewardOutput(
            reward=clamped_reward,
            raw_reward=raw_reward,
            breakdown=breakdown,
            feedback=feedback,
            is_critical_miss=grade_result.is_critical_miss,
            validation_penalties=penalties,
        )

    def compute_step_reward(
        self,
        action: ModerationAction,
        ground_truth: Dict[str, Any],
        task_id: str,
        step_idx: int,
    ) -> RewardOutput:
        """
        Compute the reward for a single step within a multi-step episode.

        For hard tasks, each step gets its own reward signal so that the
        agent receives trajectory-level feedback, not just end-of-episode.
        """
        penalties = _validate_action(action)

        grader = get_grader(task_id)
        if not isinstance(grader, HardGrader):
            # Fallback: shouldn't happen, but handle gracefully
            return self.compute_reward(action, ground_truth, task_id)

        step_result: GradeResult = grader.grade_step(action, ground_truth, step_idx)

        total_penalty = sum(penalties.values())
        raw_reward = step_result.score + total_penalty
        clamped_reward = max(0.0, min(1.0, raw_reward))

        breakdown = {**step_result.breakdown}
        for k, v in penalties.items():
            breakdown[k] = v

        feedback = step_result.feedback
        if penalties:
            penalty_msgs = []
            if "empty_reasoning" in penalties:
                penalty_msgs.append("Penalty: empty reasoning")
            if "shallow_reasoning" in penalties:
                penalty_msgs.append("Penalty: reasoning too brief")
            feedback = feedback + " " + " ".join(penalty_msgs)

        return RewardOutput(
            reward=clamped_reward,
            raw_reward=raw_reward,
            breakdown=breakdown,
            feedback=feedback,
            is_critical_miss=step_result.is_critical_miss,
            validation_penalties=penalties,
        )

    def compute_episode_reward(
        self,
        step_grade_results: List[GradeResult],
        ground_truth: Dict[str, Any],
        task_id: str,
        decisions_made: List[str],
        max_steps: int,
    ) -> RewardOutput:
        """
        Compute the aggregate reward for a completed multi-step episode.

        Combines:
        - Weighted average of per-step scores (later steps matter more)
        - HardGrader's episode-level modifiers (early detection, false positive)
        - Consistency bonus
        """
        grader = get_grader(task_id)
        if not isinstance(grader, HardGrader):
            # Shouldn't happen
            if step_grade_results:
                last = step_grade_results[-1]
                return RewardOutput(
                    reward=last.score, raw_reward=last.score,
                    breakdown=last.breakdown, feedback=last.feedback,
                )
            return RewardOutput(reward=0.0, raw_reward=0.0, breakdown={}, feedback="No steps.")

        episode_result: EpisodeGradeResult = grader.grade_episode(
            step_grade_results, ground_truth, max_steps
        )

        # Add consistency bonus
        c_bonus = _consistency_bonus(decisions_made, ground_truth["decision"])

        raw_reward = episode_result.score + c_bonus
        clamped_reward = max(0.0, min(1.0, raw_reward))

        breakdown = {**episode_result.breakdown}
        if c_bonus > 0:
            breakdown["consistency_bonus"] = c_bonus

        feedback = episode_result.feedback
        if c_bonus > 0:
            feedback += f" Consistency bonus: +{c_bonus:.2f}"

        return RewardOutput(
            reward=clamped_reward,
            raw_reward=raw_reward,
            breakdown=breakdown,
            feedback=feedback,
            is_critical_miss=episode_result.is_critical_miss,
        )
