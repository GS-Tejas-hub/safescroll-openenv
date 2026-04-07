# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
SafeScroll Scenario Bank — unified access to all task scenarios.

Aggregates easy, medium, and hard scenario modules into a single
mapping keyed by task_id for use by the SafeScrollEnvironment.
"""

from typing import Any, Dict, List

from .scenarios_easy import EASY_SCENARIOS
from .scenarios_hard import HARD_SCENARIOS
from .scenarios_medium import MEDIUM_SCENARIOS

SCENARIOS: Dict[str, List[Dict[str, Any]]] = {
    "easy": EASY_SCENARIOS,
    "medium": MEDIUM_SCENARIOS,
    "hard": HARD_SCENARIOS,
}

SCENARIO_COUNTS: Dict[str, int] = {
    task_id: len(pool) for task_id, pool in SCENARIOS.items()
}
