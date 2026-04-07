"""
SafeScroll Environment Tests.

Validates core functionality: scenarios load, graders are deterministic,
scores are in [0.0, 1.0], all tasks work, and the environment meets
the OpenEnv spec requirements.
"""

import os
import sys

import pytest

# Ensure imports work from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import (
    VALID_ACCOUNT_ACTIONS,
    VALID_CATEGORIES,
    VALID_CONTENT_TYPES,
    VALID_DECISIONS,
    VALID_ESCALATION_TARGETS,
    VALID_PLATFORMS,
    VALID_SEVERITIES,
    VALID_TASK_IDS,
    ModerationAction,
    ModerationObservation,
    SafeScrollState,
)
from server.graders import EasyGrader, HardGrader, MediumGrader, get_grader
from server.safescroll_env_environment import SafeScrollEnvironment
from server.scenarios import SCENARIO_COUNTS, SCENARIOS


# ---------------------------------------------------------------------------
# Scenario validation
# ---------------------------------------------------------------------------


class TestScenarios:
    """Verify all scenarios have correct structure and valid field values."""

    def test_scenario_counts(self):
        assert len(SCENARIOS) == 3
        assert SCENARIO_COUNTS["easy"] >= 3
        assert SCENARIO_COUNTS["medium"] >= 3
        assert SCENARIO_COUNTS["hard"] >= 3
        total = sum(SCENARIO_COUNTS.values())
        assert total >= 9, f"Need at least 9 scenarios, got {total}"

    @pytest.mark.parametrize("task_id", VALID_TASK_IDS)
    def test_all_scenarios_have_required_fields(self, task_id):
        for s in SCENARIOS[task_id]:
            assert "scenario_id" in s
            assert "content_text" in s
            assert "content_type" in s
            assert "platform" in s
            assert "community_context" in s
            assert "poster_profile" in s
            assert "reporter_info" in s
            assert "max_steps" in s
            assert "ground_truth" in s

    @pytest.mark.parametrize("task_id", VALID_TASK_IDS)
    def test_ground_truth_has_valid_values(self, task_id):
        for s in SCENARIOS[task_id]:
            gt = s["ground_truth"]
            assert gt["decision"] in VALID_DECISIONS, f"{s['scenario_id']}: invalid decision {gt['decision']}"
            assert gt["severity"] in VALID_SEVERITIES, f"{s['scenario_id']}: invalid severity"
            assert gt["category"] in VALID_CATEGORIES, f"{s['scenario_id']}: invalid category"
            assert gt["account_action"] in VALID_ACCOUNT_ACTIONS
            assert gt["escalate_to"] in VALID_ESCALATION_TARGETS
            assert "critical_context_factors" in gt

    def test_no_duplicate_scenario_ids(self):
        all_ids = [s["scenario_id"] for pool in SCENARIOS.values() for s in pool]
        assert len(all_ids) == len(set(all_ids)), "Duplicate scenario IDs found"

    def test_hard_scenarios_have_message_history(self):
        for s in SCENARIOS["hard"]:
            assert s.get("message_history") is not None, f"{s['scenario_id']} missing message_history"
            assert s["max_steps"] >= 2, f"{s['scenario_id']} hard task should be multi-step"


# ---------------------------------------------------------------------------
# Environment tests
# ---------------------------------------------------------------------------


class TestEnvironment:
    """Verify the environment meets the OpenEnv spec."""

    def setup_method(self):
        self.env = SafeScrollEnvironment()

    def test_reset_returns_observation(self):
        obs = self.env.reset(task_id="easy")
        assert isinstance(obs, ModerationObservation)
        assert obs.done is False
        assert obs.content_text != ""
        assert obs.task_id == "easy"

    def test_step_returns_observation_with_reward(self):
        self.env.reset(seed=0, task_id="easy")
        action = ModerationAction(
            decision="approve", severity="none", category="safe",
            reasoning="Safe content", account_action="none", escalate_to="none",
        )
        obs = self.env.step(action)
        assert isinstance(obs, ModerationObservation)
        assert obs.done is True
        assert obs.reward is not None
        assert 0.0 <= obs.reward <= 1.0
        assert obs.reward_breakdown is not None

    def test_state_returns_state(self):
        self.env.reset(task_id="easy")
        state = self.env.state
        assert isinstance(state, SafeScrollState)
        assert state.episode_id is not None
        assert state.step_count == 0

    def test_reset_clears_state(self):
        self.env.reset(seed=0, task_id="easy")
        action = ModerationAction(
            decision="approve", severity="none", category="safe",
            reasoning="test", account_action="none", escalate_to="none",
        )
        self.env.step(action)
        assert self.env.state.step_count == 1

        self.env.reset(seed=1, task_id="easy")
        assert self.env.state.step_count == 0
        assert self.env.state.total_reward == 0.0

    @pytest.mark.parametrize("task_id", VALID_TASK_IDS)
    def test_all_tasks_work(self, task_id):
        obs = self.env.reset(seed=0, task_id=task_id)
        assert obs.task_id == task_id
        for _ in range(obs.max_steps):
            action = ModerationAction(
                decision="flag_review", severity="medium", category="safe",
                reasoning="Reviewing", account_action="none", escalate_to="none",
            )
            obs = self.env.step(action)
        assert obs.done is True

    def test_hard_task_is_multistep(self):
        obs = self.env.reset(seed=0, task_id="hard")
        assert obs.max_steps >= 2

        action = ModerationAction(
            decision="flag_review", severity="medium", category="grooming",
            reasoning="Monitoring", account_action="none", escalate_to="human_review",
        )
        obs = self.env.step(action)
        assert obs.done is False  # Should not be done after 1 step

    def test_step_without_reset_returns_error(self):
        env = SafeScrollEnvironment()
        action = ModerationAction(
            decision="approve", severity="none", category="safe",
            reasoning="test", account_action="none", escalate_to="none",
        )
        obs = env.step(action)
        assert obs.done is True
        assert "Error" in obs.feedback


# ---------------------------------------------------------------------------
# Grader tests
# ---------------------------------------------------------------------------


class TestGraders:
    """Verify graders are deterministic and produce scores in [0.0, 1.0]."""

    def test_grader_factory(self):
        assert isinstance(get_grader("easy"), EasyGrader)
        assert isinstance(get_grader("medium"), MediumGrader)
        assert isinstance(get_grader("hard"), HardGrader)

    def test_easy_grader_deterministic(self):
        grader = EasyGrader()
        action = ModerationAction(
            decision="remove", severity="medium", category="spam",
            reasoning="Spam detected", account_action="suspend", escalate_to="none",
        )
        gt = {"decision": "remove", "severity": "medium", "category": "spam",
              "account_action": "suspend", "escalate_to": "none",
              "critical_context_factors": []}
        scores = [grader.grade(action, gt).score for _ in range(5)]
        assert len(set(scores)) == 1, f"Not deterministic: {scores}"

    def test_scores_in_range(self):
        env = SafeScrollEnvironment()
        for task in VALID_TASK_IDS:
            for seed in range(10):
                obs = env.reset(seed=seed, task_id=task)
                for _ in range(obs.max_steps):
                    action = ModerationAction(
                        decision="flag_review", severity="medium", category="grooming",
                        reasoning="Potential issue detected",
                        account_action="warn", escalate_to="human_review",
                    )
                    obs = env.step(action)
                assert 0.0 <= obs.reward <= 1.0, f"Score {obs.reward} out of range for {task} seed={seed}"

    def test_graders_produce_variable_scores(self):
        env = SafeScrollEnvironment()
        scores = set()
        for task in VALID_TASK_IDS:
            for seed in range(5):
                obs = env.reset(seed=seed, task_id=task)
                for _ in range(obs.max_steps):
                    action = ModerationAction(
                        decision="approve", severity="none", category="safe",
                        reasoning="Safe", account_action="none", escalate_to="none",
                    )
                    obs = env.step(action)
                scores.add(round(obs.reward, 3))
        assert len(scores) > 1, "All scores are identical — grader always returns same score"

    def test_correct_answer_scores_higher(self):
        env = SafeScrollEnvironment()
        # Find a spam scenario
        obs = env.reset(seed=31, task_id="easy")
        correct = ModerationAction(
            decision="remove", severity="medium", category="spam",
            reasoning="Obvious spam from new account selling followers with suspicious link",
            account_action="suspend", escalate_to="none",
        )
        obs_correct = env.step(correct)

        obs = env.reset(seed=31, task_id="easy")
        wrong = ModerationAction(
            decision="approve", severity="none", category="safe",
            reasoning="Fine", account_action="none", escalate_to="none",
        )
        obs_wrong = env.step(wrong)
        assert obs_correct.reward > obs_wrong.reward

    def test_empty_reasoning_penalized(self):
        env = SafeScrollEnvironment()
        obs = env.reset(seed=31, task_id="easy")
        with_reasoning = ModerationAction(
            decision="remove", severity="medium", category="spam",
            reasoning="Spam from new account with suspicious link and zero posts",
            account_action="suspend", escalate_to="none",
        )
        score_with = env.step(with_reasoning).reward

        obs = env.reset(seed=31, task_id="easy")
        no_reasoning = ModerationAction(
            decision="remove", severity="medium", category="spam",
            reasoning="",
            account_action="suspend", escalate_to="none",
        )
        score_without = env.step(no_reasoning).reward
        assert score_with > score_without, "Empty reasoning should be penalized"
