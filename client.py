# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
SafeScroll Content Moderation Environment — Client.

Provides a typed WebSocket client that translates between Python objects
and the wire format used by the SafeScroll FastAPI server.
"""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult

try:
    from .models import ModerationAction, ModerationObservation, SafeScrollState
except ImportError:
    from models import ModerationAction, ModerationObservation, SafeScrollState  # type: ignore[no-redef]


class SafeScrollEnv(
    EnvClient[ModerationAction, ModerationObservation, SafeScrollState]
):
    """
    Client for the SafeScroll Content Moderation Environment.

    Maintains a persistent WebSocket connection to the environment server.
    Each client instance gets its own dedicated environment session.

    Example (sync):
        >>> with SafeScrollEnv(base_url="http://localhost:8000").sync() as env:
        ...     result = env.reset(task_id="easy")
        ...     print(result.observation.content_text)
        ...
        ...     action = ModerationAction(
        ...         decision="remove",
        ...         severity="medium",
        ...         category="spam",
        ...         reasoning="Obvious follower-selling spam with suspicious link",
        ...     )
        ...     result = env.step(action)
        ...     print(f"Score: {result.reward}")

    Example (async):
        >>> async with SafeScrollEnv(base_url="http://localhost:8000") as env:
        ...     result = await env.reset(task_id="medium")
        ...     result = await env.step(action)
    """

    def _step_payload(self, action: ModerationAction) -> Dict:
        """Convert ModerationAction to JSON payload for the WebSocket message."""
        return {
            "decision": action.decision,
            "severity": action.severity,
            "category": action.category,
            "reasoning": action.reasoning,
            "account_action": action.account_action,
            "escalate_to": action.escalate_to,
        }

    def _parse_result(self, payload: Dict) -> StepResult[ModerationObservation]:
        """Parse server response into a typed StepResult."""
        obs_data = payload.get("observation", {})

        observation = ModerationObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            content_text=obs_data.get("content_text", ""),
            content_type=obs_data.get("content_type", "post"),
            platform=obs_data.get("platform", "instagram"),
            community_context=obs_data.get("community_context", "general"),
            poster_profile=obs_data.get("poster_profile", {}),
            target_user_profile=obs_data.get("target_user_profile"),
            reporter_info=obs_data.get("reporter_info", {}),
            message_history=obs_data.get("message_history"),
            task_id=obs_data.get("task_id", "easy"),
            scenario_id=obs_data.get("scenario_id", ""),
            step_count=obs_data.get("step_count", 0),
            max_steps=obs_data.get("max_steps", 1),
            feedback=obs_data.get("feedback", ""),
            reward_breakdown=obs_data.get("reward_breakdown"),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> SafeScrollState:
        """Parse server response into SafeScrollState."""
        return SafeScrollState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_id=payload.get("task_id", ""),
            scenario_id=payload.get("scenario_id", ""),
            total_reward=payload.get("total_reward", 0.0),
            decisions_made=payload.get("decisions_made", []),
        )
