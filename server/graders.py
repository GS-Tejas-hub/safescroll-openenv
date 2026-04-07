# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
SafeScroll Grading System.

Three deterministic graders that evaluate agent moderation decisions
against expert-labeled ground truth, producing scores in [0.0, 1.0].

    EasyGrader   — Direct field-by-field match (Task 1)
    MediumGrader — Field match + context-awareness scoring (Task 2)
    HardGrader   — Multi-step trajectory scoring with early-detection
                   bonus and false-positive penalties (Task 3)

All graders are stateless and deterministic: same (action, ground_truth)
input will always produce the same score.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    from ..models import ModerationAction
except ImportError:
    from models import ModerationAction


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------

@dataclass
class GradeResult:
    """Outcome of grading a single action (or an entire episode)."""

    score: float                          # Final score in [0.0, 1.0]
    breakdown: Dict[str, float]           # Per-signal scores
    feedback: str                         # Human-readable feedback
    is_critical_miss: bool = False        # True if child-safety issue missed


@dataclass
class EpisodeGradeResult:
    """Aggregated grading outcome for a multi-step (Task 3) episode."""

    score: float                          # Final episode score in [0.0, 1.0]
    step_scores: List[float]              # Per-step scores
    breakdown: Dict[str, float]           # Aggregated breakdown
    feedback: str
    early_detection_bonus: float = 0.0
    is_critical_miss: bool = False


# ---------------------------------------------------------------------------
# Shared scoring primitives
# ---------------------------------------------------------------------------

_SEVERITY_LEVELS = ["none", "low", "medium", "high", "critical"]
_ACCOUNT_ACTIONS = ["none", "warn", "restrict", "suspend"]
_ESCALATION_TARGETS = ["none", "human_review", "child_safety_team", "law_enforcement"]
_CHILD_SAFETY_CATEGORIES = {"child_exploitation", "grooming"}


def _score_decision(agent: str, expected: str) -> float:
    """Score decision match with partial credit for related actions."""
    if agent == expected:
        return 1.0
    # flag_review and escalate are adjacent — partial credit
    if {agent, expected} <= {"flag_review", "escalate"}:
        return 0.6
    # remove when flag/escalate expected — acted but under-escalated
    if agent == "remove" and expected in ("flag_review", "escalate"):
        return 0.3
    # flag/escalate when remove expected — over-escalated but safe direction
    if agent in ("flag_review", "escalate") and expected == "remove":
        return 0.4
    # approve when any action expected — worst
    if agent == "approve" and expected != "approve":
        return 0.0
    # remove/flag/escalate when approve expected — false positive
    if expected == "approve" and agent != "approve":
        return 0.15
    return 0.0


def _score_ordinal(agent_val: str, expected_val: str, scale: List[str], penalty_per_step: float = 0.25) -> float:
    """Score an ordinal field (severity, account_action) with distance-based partial credit."""
    try:
        agent_idx = scale.index(agent_val)
        expected_idx = scale.index(expected_val)
    except ValueError:
        return 0.0
    distance = abs(agent_idx - expected_idx)
    return max(0.0, 1.0 - distance * penalty_per_step)


def _score_escalation(agent_val: str, expected_val: str) -> float:
    """Score escalation target match with partial credit."""
    if agent_val == expected_val:
        return 1.0
    # Both escalated, just wrong target
    if agent_val != "none" and expected_val != "none":
        return 0.4
    # Escalated when shouldn't have
    if expected_val == "none" and agent_val != "none":
        return 0.2
    # Didn't escalate when should have
    if expected_val != "none" and agent_val == "none":
        return 0.0
    return 0.0


_RELATED_CATEGORIES = {
    ("grooming", "child_exploitation"): 0.6,
    ("child_exploitation", "grooming"): 0.6,
    ("harassment", "hate_speech"): 0.4,
    ("hate_speech", "harassment"): 0.4,
    ("explicit_adult", "child_exploitation"): 0.3,
    ("harassment", "grooming"): 0.3,
}


def _score_category(agent_cat: str, expected_cat: str) -> float:
    if agent_cat == expected_cat:
        return 1.0
    return _RELATED_CATEGORIES.get((agent_cat, expected_cat), 0.0)


def _score_context_awareness(reasoning: str, critical_factors: List[str]) -> float:
    """
    Score how well the agent's reasoning addresses critical context factors.

    Each factor is an underscore-separated label. We require at least TWO
    keywords from a factor to appear in the reasoning (or the full factor
    phrase) for it to count as a hit. Single common words don't count.
    """
    if not critical_factors:
        return 0.5

    reasoning_lower = reasoning.lower()
    hits = 0
    for factor in critical_factors:
        # Check if the full factor phrase (with underscores replaced by spaces) appears
        phrase = factor.lower().replace("_", " ")
        if phrase in reasoning_lower:
            hits += 1
            continue

        # Otherwise, require at least 2 keywords (length > 2) to match
        keywords = [kw for kw in phrase.split() if len(kw) > 3]
        if not keywords:
            keywords = [kw for kw in phrase.split() if len(kw) > 2]

        matched = sum(1 for kw in keywords if kw in reasoning_lower)
        if len(keywords) >= 2 and matched >= 2:
            hits += 1
        elif len(keywords) == 1 and matched >= 1:
            hits += 1

    return min(hits / len(critical_factors), 1.0)


def _critical_miss_penalty(action: ModerationAction, gt: Dict[str, Any]) -> float:
    """
    Return a penalty for missing child-safety issues.

    -1.0 if agent approves grooming/child_exploitation.
    -0.3 if agent removes but doesn't escalate.
     0.0 otherwise.
    """
    if gt["category"] not in _CHILD_SAFETY_CATEGORIES:
        return 0.0
    if action.decision == "approve":
        return -1.0
    if action.decision == "remove" and gt["decision"] == "escalate":
        return -0.3
    return 0.0


def _build_feedback_lines(
    action: ModerationAction,
    gt: Dict[str, Any],
    breakdown: Dict[str, float],
    score: float,
    done: bool,
) -> str:
    """Build human-readable feedback from grading results."""
    lines: List[str] = []

    # Decision feedback
    if action.decision == gt["decision"]:
        lines.append(f"Correct decision: {action.decision}.")
    else:
        lines.append(
            f"Decision '{action.decision}' was incorrect. "
            f"Expected: '{gt['decision']}'."
        )

    # Category feedback
    if action.category != gt["category"]:
        lines.append(
            f"Category '{action.category}' was incorrect. "
            f"Expected: '{gt['category']}'."
        )

    # Severity feedback
    if action.severity != gt["severity"]:
        lines.append(
            f"Severity '{action.severity}' differs from expected '{gt['severity']}'."
        )

    # Context awareness feedback
    ctx_score = breakdown.get("context_awareness", 1.0)
    if ctx_score < 0.5:
        factors = gt.get("critical_context_factors", [])
        if factors:
            shown = ", ".join(f.replace("_", " ") for f in factors[:3])
            lines.append(f"Your reasoning missed key context factors: {shown}.")

    # Critical miss warning
    penalty = breakdown.get("critical_miss_penalty", 0.0)
    if penalty < 0:
        lines.append(
            "CRITICAL: A child-safety issue was missed or under-escalated. "
            "This type of error is heavily penalized."
        )

    # Episode score
    if done:
        lines.append(f"Episode complete. Final score: {score:.3f}")

    return " ".join(lines)


# ---------------------------------------------------------------------------
# EasyGrader — Task 1
# ---------------------------------------------------------------------------

class EasyGrader:
    """
    Grades obvious content classification decisions.

    Weighting emphasises getting the core decision and category right,
    since the scenarios are unambiguous.

    Weights:
        decision_correctness   40%
        category_accuracy      25%
        severity_accuracy      20%
        account_action_fit     15%
    """

    WEIGHTS: Dict[str, float] = {
        "decision_correctness": 0.40,
        "category_accuracy": 0.25,
        "severity_accuracy": 0.20,
        "account_action_fit": 0.15,
    }

    def grade(self, action: ModerationAction, gt: Dict[str, Any]) -> GradeResult:
        breakdown: Dict[str, float] = {}

        breakdown["decision_correctness"] = _score_decision(action.decision, gt["decision"])
        breakdown["category_accuracy"] = _score_category(action.category, gt["category"])
        breakdown["severity_accuracy"] = _score_ordinal(
            action.severity, gt["severity"], _SEVERITY_LEVELS, penalty_per_step=0.3
        )
        breakdown["account_action_fit"] = _score_ordinal(
            action.account_action, gt["account_action"], _ACCOUNT_ACTIONS, penalty_per_step=0.35
        )

        score = sum(breakdown[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        score = max(0.0, min(1.0, score))

        feedback = _build_feedback_lines(action, gt, breakdown, score, done=True)
        return GradeResult(score=score, breakdown=breakdown, feedback=feedback)


# ---------------------------------------------------------------------------
# MediumGrader — Task 2
# ---------------------------------------------------------------------------

class MediumGrader:
    """
    Grades context-dependent moderation decisions.

    Compared to EasyGrader, this puts heavy weight on *context awareness* —
    whether the agent's reasoning mentions the critical context factors that
    make the same content safe in one setting but harmful in another.

    Weights:
        decision_correctness   25%
        context_awareness      30%   ← the differentiator
        category_accuracy      15%
        severity_accuracy      10%
        account_action_fit     10%
        escalation_fit         10%
    """

    WEIGHTS: Dict[str, float] = {
        "decision_correctness": 0.25,
        "context_awareness": 0.30,
        "category_accuracy": 0.15,
        "severity_accuracy": 0.10,
        "account_action_fit": 0.10,
        "escalation_fit": 0.10,
    }

    def grade(self, action: ModerationAction, gt: Dict[str, Any]) -> GradeResult:
        breakdown: Dict[str, float] = {}

        breakdown["decision_correctness"] = _score_decision(action.decision, gt["decision"])
        breakdown["context_awareness"] = _score_context_awareness(
            action.reasoning, gt.get("critical_context_factors", [])
        )
        breakdown["category_accuracy"] = _score_category(action.category, gt["category"])
        breakdown["severity_accuracy"] = _score_ordinal(
            action.severity, gt["severity"], _SEVERITY_LEVELS, penalty_per_step=0.3
        )
        breakdown["account_action_fit"] = _score_ordinal(
            action.account_action, gt["account_action"], _ACCOUNT_ACTIONS, penalty_per_step=0.35
        )
        breakdown["escalation_fit"] = _score_escalation(
            action.escalate_to, gt["escalate_to"]
        )

        # Critical miss penalty applied as a modifier, not a weighted signal
        penalty = _critical_miss_penalty(action, gt)
        is_critical = penalty < 0

        score = sum(breakdown[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        score = max(0.0, min(1.0, score + penalty * 0.10))

        feedback = _build_feedback_lines(action, gt, {**breakdown, "critical_miss_penalty": penalty}, score, done=True)
        return GradeResult(
            score=score,
            breakdown={**breakdown, "critical_miss_penalty": penalty},
            feedback=feedback,
            is_critical_miss=is_critical,
        )


# ---------------------------------------------------------------------------
# HardGrader — Task 3
# ---------------------------------------------------------------------------

class HardGrader:
    """
    Grades multi-step moderation decisions (grooming, coded language, etc.).

    Each step in the episode is scored independently, and the episode score
    is a weighted combination of per-step scores plus bonuses/penalties.

    Per-step scoring uses the same signals as MediumGrader.

    Episode-level modifiers:
        - Early detection bonus: +0.15 if the agent flags/escalates at step 1
          when the final ground truth is escalate/flag_review.
        - Late detection penalty: -0.10 if the agent only catches it at the
          last step.
        - False positive penalty: if ground truth is 'approve' (safe) but the
          agent over-flags, the penalty scales with how aggressively they acted.
        - Critical miss penalty: if the agent approves grooming/exploitation
          at the final step.

    Final episode score = weighted_avg(step_scores)
                        + early_detection_bonus
                        + critical_miss_penalty
        clamped to [0.0, 1.0]
    """

    STEP_WEIGHTS: Dict[str, float] = {
        "decision_correctness": 0.25,
        "context_awareness": 0.25,
        "category_accuracy": 0.15,
        "severity_accuracy": 0.10,
        "account_action_fit": 0.10,
        "escalation_fit": 0.15,
    }

    def grade_step(
        self,
        action: ModerationAction,
        gt: Dict[str, Any],
        step_idx: int,
    ) -> GradeResult:
        """Grade a single step within a multi-step episode."""
        breakdown: Dict[str, float] = {}

        # For intermediate steps, we check against per_step_expected if available
        per_step = gt.get("per_step_expected", [])
        if step_idx < len(per_step):
            step_gt = per_step[step_idx]
            min_decision = step_gt.get("min_decision", "approve")
            key_signals = step_gt.get("key_signals", [])

            # Decision score: did agent at least meet the minimum bar?
            decision_score = self._score_step_decision(action.decision, min_decision, gt["decision"])
            breakdown["decision_correctness"] = decision_score

            # Context: check for step-specific key signals
            breakdown["context_awareness"] = _score_context_awareness(
                action.reasoning, key_signals
            )
        else:
            # Final step — grade against the full ground truth
            breakdown["decision_correctness"] = _score_decision(action.decision, gt["decision"])
            breakdown["context_awareness"] = _score_context_awareness(
                action.reasoning, gt.get("critical_context_factors", [])
            )

        breakdown["category_accuracy"] = _score_category(action.category, gt["category"])
        breakdown["severity_accuracy"] = _score_ordinal(
            action.severity, gt["severity"], _SEVERITY_LEVELS, penalty_per_step=0.3
        )
        breakdown["account_action_fit"] = _score_ordinal(
            action.account_action, gt["account_action"], _ACCOUNT_ACTIONS, penalty_per_step=0.35
        )
        breakdown["escalation_fit"] = _score_escalation(
            action.escalate_to, gt["escalate_to"]
        )

        penalty = _critical_miss_penalty(action, gt)
        breakdown["critical_miss_penalty"] = penalty

        step_score = sum(breakdown[k] * self.STEP_WEIGHTS.get(k, 0) for k in breakdown if k in self.STEP_WEIGHTS)
        step_score = max(0.0, min(1.0, step_score + penalty * 0.05))

        feedback = _build_feedback_lines(action, gt, breakdown, step_score, done=False)
        return GradeResult(
            score=step_score,
            breakdown=breakdown,
            feedback=feedback,
            is_critical_miss=penalty < -0.5,
        )

    def grade_episode(
        self,
        step_results: List[GradeResult],
        gt: Dict[str, Any],
        total_steps: int,
    ) -> EpisodeGradeResult:
        """
        Aggregate per-step grades into a final episode score.

        Later steps are weighted more heavily than earlier ones because the
        final decision matters most.
        """
        if not step_results:
            return EpisodeGradeResult(
                score=0.0, step_scores=[], breakdown={},
                feedback="No steps completed.", is_critical_miss=False,
            )

        n = len(step_results)

        # Progressive step weights: later steps matter more
        # e.g., 3 steps → weights [0.2, 0.3, 0.5]
        raw_weights = [(i + 1) ** 2 for i in range(n)]
        total_w = sum(raw_weights)
        step_weights = [w / total_w for w in raw_weights]

        step_scores = [r.score for r in step_results]
        weighted_avg = sum(s * w for s, w in zip(step_scores, step_weights))

        # Early detection bonus
        early_bonus = 0.0
        if gt["decision"] in ("escalate", "flag_review"):
            # Check if the agent flagged/escalated at step 1
            if n > 1 and step_results[0].breakdown.get("decision_correctness", 0) >= 0.6:
                early_bonus = 0.08
            elif n > 2 and step_results[1].breakdown.get("decision_correctness", 0) >= 0.6:
                early_bonus = 0.04

        # False positive penalty for safe scenarios
        false_positive_penalty = 0.0
        if gt["category"] == "safe" and gt["decision"] == "approve":
            final = step_results[-1]
            final_decision = None
            # Check if the agent's final decision was not approve
            if final.breakdown.get("decision_correctness", 1.0) < 0.5:
                false_positive_penalty = -0.20

        # Critical miss on final step
        final_critical = step_results[-1].is_critical_miss
        critical_penalty = -0.20 if final_critical else 0.0

        episode_score = weighted_avg + early_bonus + false_positive_penalty + critical_penalty
        episode_score = max(0.0, min(1.0, episode_score))

        # Aggregate breakdown (average across steps)
        agg_breakdown: Dict[str, float] = {}
        all_keys = set()
        for r in step_results:
            all_keys.update(r.breakdown.keys())
        for key in all_keys:
            vals = [r.breakdown.get(key, 0.0) for r in step_results]
            agg_breakdown[key] = sum(v * w for v, w in zip(vals, step_weights))
        agg_breakdown["early_detection_bonus"] = early_bonus
        agg_breakdown["false_positive_penalty"] = false_positive_penalty

        # Build feedback
        feedback_parts = [f"Episode complete ({n} steps)."]
        for i, sr in enumerate(step_results):
            feedback_parts.append(f"Step {i+1}: {sr.score:.3f}")
        if early_bonus > 0:
            feedback_parts.append(f"Early detection bonus: +{early_bonus:.2f}")
        if false_positive_penalty < 0:
            feedback_parts.append(f"False positive penalty: {false_positive_penalty:.2f}")
        if final_critical:
            feedback_parts.append("CRITICAL: Child-safety issue missed at final step.")
        feedback_parts.append(f"Final episode score: {episode_score:.3f}")

        return EpisodeGradeResult(
            score=episode_score,
            step_scores=step_scores,
            breakdown=agg_breakdown,
            feedback=" ".join(feedback_parts),
            early_detection_bonus=early_bonus,
            is_critical_miss=final_critical,
        )

    @staticmethod
    def _score_step_decision(agent_decision: str, min_decision: str, final_gt_decision: str) -> float:
        """
        Score an intermediate step's decision against the minimum expected bar.

        At early steps we don't expect the agent to have full certainty.
        Meeting the minimum bar (e.g. flag_review) earns partial credit;
        exceeding the final target at an early step incurs an over-confidence
        penalty; falling below the minimum earns low credit.
        """
        decision_rank = {"approve": 0, "flag_review": 1, "remove": 1, "escalate": 2}
        agent_rank = decision_rank.get(agent_decision, 0)
        min_rank = decision_rank.get(min_decision, 0)
        final_rank = decision_rank.get(final_gt_decision, 0)

        if agent_rank >= final_rank:
            return 0.7  # Over-confidence penalty: exceeding final target at early step
        if agent_rank >= min_rank:
            return 0.8  # Meets the minimum bar for this step
        if agent_rank > 0:
            return 0.3  # At least did something (not approve)
        return 0.0  # Approved when should have flagged


# ---------------------------------------------------------------------------
# Grader factory
# ---------------------------------------------------------------------------

_GRADERS: Dict[str, Any] = {
    "easy": EasyGrader(),
    "medium": MediumGrader(),
    "hard": HardGrader(),
}


def get_grader(task_id: str) -> EasyGrader | MediumGrader | HardGrader:
    """Return the grader instance for the given task_id."""
    return _GRADERS.get(task_id, _GRADERS["easy"])
