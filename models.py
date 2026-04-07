# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the SafeScroll Content Moderation Environment.

SafeScroll trains AI agents to make nuanced, context-aware content
moderation decisions across social media platforms. These typed models
define the complete interface between the agent and the environment.
"""

from typing import Dict, List, Optional

from openenv.core.env_server.types import Action, Observation, State
from pydantic import Field


# ---------------------------------------------------------------------------
# Constants — shared between server, client, and graders
# ---------------------------------------------------------------------------

VALID_DECISIONS = ["approve", "remove", "flag_review", "escalate"]

VALID_SEVERITIES = ["none", "low", "medium", "high", "critical"]

VALID_CATEGORIES = [
    "safe",
    "spam",
    "hate_speech",
    "harassment",
    "explicit_adult",
    "violence_graphic",
    "child_exploitation",
    "grooming",
    "self_harm",
    "misinformation",
    "impersonation",
    "privacy_violation",
]

VALID_ACCOUNT_ACTIONS = ["none", "warn", "restrict", "suspend"]

VALID_ESCALATION_TARGETS = [
    "none",
    "human_review",
    "child_safety_team",
    "law_enforcement",
]

VALID_CONTENT_TYPES = [
    "post",
    "comment",
    "dm",
    "reel_description",
    "story",
    "group_post",
]

VALID_PLATFORMS = ["instagram", "facebook", "whatsapp", "twitter", "telegram"]

VALID_COMMUNITIES = [
    "gaming",
    "education",
    "fitness",
    "kids",
    "general",
    "news",
    "comedy",
    "art",
    "technology",
]

VALID_TASK_IDS = ["easy", "medium", "hard"]


# ---------------------------------------------------------------------------
# Action — what the agent sends to the environment
# ---------------------------------------------------------------------------

class ModerationAction(Action):
    """
    A content moderation decision made by the agent.

    The agent reviews reported content and must provide a complete
    moderation decision including the action to take, severity assessment,
    violation category, reasoning, account-level action, and escalation path.
    """

    decision: str = Field(
        ...,
        description="Primary moderation decision: approve, remove, flag_review, or escalate",
    )
    severity: str = Field(
        ...,
        description="Assessed severity level: none, low, medium, high, or critical",
    )
    category: str = Field(
        ...,
        description="Violation category (e.g., spam, hate_speech, grooming, safe)",
    )
    reasoning: str = Field(
        ...,
        description="Agent's explanation for why this decision was made, including context factors considered",
    )
    account_action: str = Field(
        default="none",
        description="Action to take on the poster's account: none, warn, restrict, or suspend",
    )
    escalate_to: str = Field(
        default="none",
        description="Escalation target: none, human_review, child_safety_team, or law_enforcement",
    )


# ---------------------------------------------------------------------------
# Observation — what the agent sees from the environment
# ---------------------------------------------------------------------------

class ModerationObservation(Observation):
    """
    A content moderation scenario presented to the agent.

    Contains the reported content, platform and community context,
    user profiles of the poster and (optionally) the target, and
    metadata about the current task and episode state.

    Inherited fields from Observation:
        done: bool — whether the episode is finished
        reward: Optional[float] — reward from the previous step
    """

    # --- Content being reviewed ---
    content_text: str = Field(
        default="",
        description="The text content or description of the reported media",
    )
    content_type: str = Field(
        default="post",
        description="Type of content: post, comment, dm, reel_description, story, group_post",
    )

    # --- Platform and community context ---
    platform: str = Field(
        default="instagram",
        description="Social media platform where the content was posted",
    )
    community_context: str = Field(
        default="general",
        description="Community or topic area where the content appeared",
    )

    # --- People involved ---
    poster_profile: Dict = Field(
        default_factory=dict,
        description="Profile metadata of the content poster (age, account_age_days, followers, etc.)",
    )
    target_user_profile: Optional[Dict] = Field(
        default=None,
        description="Profile metadata of the recipient (for DMs) or targeted user",
    )
    reporter_info: Dict = Field(
        default_factory=dict,
        description="Information about who reported and why (auto-flagged or user-reported)",
    )

    # --- Conversation thread (for multi-step Task 3) ---
    message_history: Optional[List[Dict]] = Field(
        default=None,
        description="Conversation messages revealed so far (for multi-step grooming detection)",
    )

    # --- Task and episode metadata ---
    task_id: str = Field(
        default="easy",
        description="Current task difficulty: easy, medium, or hard",
    )
    scenario_id: str = Field(
        default="",
        description="Unique identifier for the current scenario",
    )
    step_count: int = Field(
        default=0,
        description="Current step within this episode",
    )
    max_steps: int = Field(
        default=1,
        description="Maximum steps allowed for this episode",
    )

    # --- Feedback from previous action ---
    feedback: str = Field(
        default="",
        description="Grader feedback on the previous action (empty on first step)",
    )
    reward_breakdown: Optional[Dict[str, float]] = Field(
        default=None,
        description="Per-signal reward decomposition from the previous step",
    )


# ---------------------------------------------------------------------------
# State — episode metadata exposed via state()
# ---------------------------------------------------------------------------

class SafeScrollState(State):
    """
    Episode-level metadata for the SafeScroll environment.

    Inherited fields from State:
        episode_id: Optional[str] — unique episode identifier
        step_count: int — steps taken so far
    """

    task_id: str = Field(default="", description="Current task difficulty level")
    scenario_id: str = Field(default="", description="Current scenario identifier")
    total_reward: float = Field(default=0.0, description="Cumulative reward this episode")
    decisions_made: List[str] = Field(
        default_factory=list,
        description="List of decisions made so far in this episode",
    )
