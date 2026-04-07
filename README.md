---
title: SafeScroll - Content Moderation Environment
emoji: 🛡
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8000
tags:
  - openenv
---

# SafeScroll: Content Moderation & Child Safety Environment

An OpenEnv environment that trains AI agents to make nuanced, context-aware content moderation decisions across social media platforms.

**Live Space:** [DemonKing0001/safescroll-env](https://huggingface.co/spaces/DemonKing0001/safescroll-env)

---

## Motivation

In March 2026, Meta was ordered to pay **$375 million** after a jury found **75,000 violations** of child safety protections across Facebook, Instagram, and WhatsApp. Days later, a Los Angeles jury found Meta and Google **liable in a landmark social media addiction trial**, awarding $6 million in damages -- the first time juries have held tech companies responsible for harms children suffer from platform design. Over **2,000 similar lawsuits** are pending. Platforms process billions of pieces of content daily, yet AI moderation systems consistently fail at one critical skill: **context-dependent judgment**.

The same phrase can be harmless banter in a gaming community or a genuine threat in a private message to a minor. Current moderation AI treats content in isolation, leading to both dangerous misses and frustrating false positives. SafeScroll addresses this gap by providing a structured training environment where AI agents learn not just *what* is harmful, but *when* and *why* it is harmful based on the full context.

This environment was built because **I have personally witnessed** minors being exposed to harmful content on social media -- AI-generated bait reels, grooming patterns in DMs, and explicit content disguised behind countdown timers. This is not a theoretical problem. It is happening to real children right now.

---

## Environment Overview

SafeScroll simulates a content moderation queue at a social media platform. An AI agent acts as a content moderator, reviewing reported content and making decisions based on the content, platform context, user profiles, and conversation history.

### How It Works

```
Agent connects via WebSocket (/ws)
    |
    v
reset(task_id="easy"|"medium"|"hard")
    |
    v
Agent receives: content + context + profiles + reporter info
    |
    v
step(action) -- agent submits moderation decision
    |
    v
Environment grades the decision, returns reward + feedback
    |
    v
Episode ends (single-step) or continues (multi-step for hard task)
```

### Three Difficulty Levels

| Task | Difficulty | Episodes | Description |
|------|-----------|----------|-------------|
| **easy** | Obvious classification | 15 scenarios, 1 step | Clear spam, hate speech, safe content. Unambiguous decisions. |
| **medium** | Context-dependent | 10 scenarios, 1 step | Same content is safe or harmful depending on platform, community, and user context. |
| **hard** | Multi-step detection | 8 scenarios, 3 steps | Grooming conversations unfold progressively. Agent must detect escalating patterns. |

**Total: 33 unique scenarios** covering 12 violation categories across 5 platforms.

---

## Action Space

The agent submits a `ModerationAction` with these fields:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `decision` | string | `approve`, `remove`, `flag_review`, `escalate` | Primary moderation action |
| `severity` | string | `none`, `low`, `medium`, `high`, `critical` | Assessed severity level |
| `category` | string | See categories below | Violation type |
| `reasoning` | string | Free text | Agent's explanation (graded for context awareness) |
| `account_action` | string | `none`, `warn`, `restrict`, `suspend` | Action on poster's account |
| `escalate_to` | string | `none`, `human_review`, `child_safety_team`, `law_enforcement` | Escalation target |

### Violation Categories

`safe`, `spam`, `hate_speech`, `harassment`, `explicit_adult`, `violence_graphic`, `child_exploitation`, `grooming`, `self_harm`, `misinformation`, `impersonation`, `privacy_violation`

---

## Observation Space

The agent receives a `ModerationObservation` with:

| Field | Description |
|-------|-------------|
| `content_text` | The reported text or content description |
| `content_type` | `post`, `comment`, `dm`, `reel_description`, `story`, `group_post` |
| `platform` | `instagram`, `facebook`, `whatsapp`, `twitter`, `telegram` |
| `community_context` | `gaming`, `education`, `fitness`, `kids`, `general`, `news`, `comedy`, `art`, `technology` |
| `poster_profile` | Username, age, account age, followers, following count, posts, verified status, bio |
| `target_user_profile` | (For DMs) Recipient's profile including age, is_minor flag |
| `reporter_info` | Auto-flagged or user-reported, reason, report count |
| `message_history` | (Hard task only) Conversation messages revealed progressively |
| `task_id` | Current task difficulty |
| `feedback` | Grader feedback from previous step |
| `reward_breakdown` | Per-signal reward decomposition |

---

## Reward System

### Multi-Signal Contextual Reward Decomposition

Unlike binary pass/fail grading, SafeScroll decomposes the reward into multiple signals so agents learn *where* in the decision process they went right or wrong:

| Signal | Description | Why It Matters |
|--------|-------------|----------------|
| `decision_correctness` | Did the agent make the right call? | Core accuracy |
| `severity_accuracy` | Did it assess the right severity level? | Proportional response |
| `category_accuracy` | Did it identify the correct violation type? | Understanding the problem |
| `context_awareness` | Did the reasoning reference key context factors? | **The differentiator** -- same content, different contexts |
| `account_action_fit` | Appropriate account-level response? | Proportional enforcement |
| `escalation_fit` | Correct escalation path? | Routing to right team |
| `critical_miss_penalty` | Negative signal if child safety missed | **Safety-critical learning** |

### Task-Specific Grading Weights

**Easy (EasyGrader):** decision 40%, category 25%, severity 20%, account 15%

**Medium (MediumGrader):** decision 25%, **context 30%**, category 15%, severity 10%, account 10%, escalation 10%

**Hard (HardGrader):** Per-step trajectory scoring with progressive step weights (later steps matter more), early detection bonus (+0.15), false positive penalty (-0.15), consistency bonus (+0.05)

### Critical Miss Penalty

If the ground truth is `grooming` or `child_exploitation` and the agent approves it: **-1.0 penalty**. This asymmetric weighting teaches models that missing child safety issues is catastrophically worse than a false positive.

### Input Validation

Empty reasoning: -0.15 penalty. Invalid field values: -0.03 to -0.20 penalty. Agents learn to provide complete, well-reasoned decisions.

---

## Task Details

### Task 1: Easy -- Obvious Content Classification

Scenarios include:
- Spam (follower-selling, crypto scams, pharmaceutical spam)
- Hate speech (direct slurs, xenophobic attacks)
- Explicit adult content, graphic violence
- Obviously safe content (cooking, travel, tech discussion, pets, fitness)
- Self-harm promotion, celebrity impersonation, health misinformation

**Expected scores:** Smart LLM 0.85-1.0, Basic LLM 0.50-0.70

### Task 2: Medium -- Context-Dependent Moderation

Scenario pairs where similar content has different correct answers:
- **Pair 1:** "I'm going to DESTROY you" in gaming community (safe) vs DM to a minor (threat)
- **Pair 2:** Dark humor in comedy group (safe) vs on a memorial post (harassment)
- **Pair 3:** Medical terminology in education (safe) vs in kids community (inappropriate)
- **Pair 4:** Teacher messaging student about homework (safe) vs unknown adult messaging minor (grooming)
- **Standalone:** Bait-and-switch reel targeting teens, heated political debate

**Expected scores:** Smart LLM 0.65-0.85, Basic LLM 0.30-0.50

### Task 3: Hard -- Adversarial & Grooming Detection

Multi-step scenarios based on the academically validated **5-stage grooming model** (trust building, relationship development, risk assessment, isolation, desensitization):

- **Grooming progressions:** Art mentorship, gaming coaching, emotional manipulation
- **Coded language:** Exploitation ring using food-themed coded terms
- **False positives:** Legitimate child safety educator (agent must NOT over-flag)
- **Weaponized reports:** Bully using the report system against a victim
- **Suspicious patterns:** New account following 600+ minors with mass DMs
- **Mixed signals:** Legitimate tutoring with subtle boundary violations

**Expected scores:** Frontier model 0.70-1.0, Basic LLM 0.15-0.35

---

## Baseline Scores

Baseline agent: **gpt-4o-mini** (temperature=0.0), 5 episodes per task.

| Task | Avg Score | Min | Max |
|------|----------|-----|-----|
| Easy | 0.863 | 0.750 | 0.948 |
| Medium | 0.527 | 0.273 | 0.767 |
| Hard | 0.751 | 0.540 | 0.870 |
| **Overall** | **0.714** | -- | -- |

Difficulty curve: Easy (0.86) > Hard (0.75) > Medium (0.53). Medium is hardest because context-dependent decisions require nuanced judgment that even frontier models struggle with.

Run the baseline yourself:
```bash
export OPENAI_API_KEY=sk-...
python baseline.py --model gpt-4o-mini --episodes 5
```

---

## Setup & Usage

### Prerequisites

- Python 3.10+
- Docker (for containerized execution)
- OpenAI API key (for baseline script)

### Local Development

```bash
# Clone and install
git clone https://huggingface.co/spaces/DemonKing0001/safescroll-env
cd safescroll-env
pip install openenv-core

# Run the server
uvicorn server.app:app --host 0.0.0.0 --port 8000

# Verify
curl http://localhost:8000/health
# {"status": "healthy"}
```

### Docker

```bash
# Build
openenv build
# or: docker build -t safescroll -f server/Dockerfile .

# Run
docker run -p 8000:8000 openenv-safescroll:latest
```

### Connect as a Client

```python
from safescroll_env import SafeScrollEnv, ModerationAction

with SafeScrollEnv(base_url="http://localhost:8000").sync() as env:
    # Start an easy episode
    result = env.reset(task_id="easy")
    print(result.observation.content_text)
    print(result.observation.poster_profile)

    # Make a moderation decision
    action = ModerationAction(
        decision="remove",
        severity="medium",
        category="spam",
        reasoning="Obvious spam from new account with suspicious link.",
        account_action="suspend",
        escalate_to="none",
    )
    result = env.step(action)
    print(f"Score: {result.reward}")
    print(f"Feedback: {result.observation.feedback}")
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Start new episode (pass `task_id` in body) |
| `/step` | POST | Submit moderation action |
| `/state` | GET | Current episode state |
| `/schema` | GET | Action/observation JSON schemas |
| `/tasks` | GET | List all tasks with action schema |
| `/grader` | GET | Latest episode grader score + breakdown |
| `/baseline` | POST | Run baseline agent and return scores |
| `/ws` | WebSocket | Persistent session for multi-step episodes |

---

## Project Structure

```
safescroll_env/
|-- models.py                     # Typed Pydantic models (Action, Observation, State)
|-- client.py                     # WebSocket client (SafeScrollEnv)
|-- baseline.py                   # Baseline inference script (OpenAI API)
|-- openenv.yaml                  # Environment manifest
|-- pyproject.toml                # Package metadata
|-- .gitignore                    # Excludes .env, __pycache__
|
|-- server/
|   |-- app.py                    # FastAPI app + /tasks, /grader, /baseline
|   |-- safescroll_env_environment.py  # Core environment (reset/step/state)
|   |-- scenarios.py              # Unified scenario bank
|   |-- scenarios_easy.py         # 15 easy scenarios
|   |-- scenarios_medium.py       # 10 medium scenarios
|   |-- scenarios_hard.py         # 8 hard multi-step scenarios
|   |-- graders.py                # EasyGrader, MediumGrader, HardGrader
|   |-- rewards.py                # RewardShaper (validation, shaping, trajectory)
|   |-- Dockerfile                # Container definition
|   |-- requirements.txt          # Server dependencies
```

---

## Technical Design

### Context-Aware Grading (The Key Innovation)

Most content moderation environments use binary grading: right or wrong. SafeScroll grades *why* the agent made a decision by checking its reasoning against scenario-specific **critical context factors**.

For example, in the gaming trash talk scenario, the critical factors are: `gaming_context`, `competitive_trash_talk`, `established_rivalry`, `both_adults`, `public_comment_not_dm`. An agent that correctly approves the content *and* mentions these context factors in its reasoning scores higher than one that approves without understanding why.

This trains agents to develop genuine contextual judgment, not just pattern matching.

### Multi-Step Grooming Detection

Hard task scenarios are based on the academically validated **5-stage grooming model** from child safety research:

1. **Victim selection & trust building** -- Compliments, shared interests, age inquiry
2. **Relationship development** -- "You're so mature", becoming the confidant
3. **Risk assessment** -- "Do your parents check your phone?"
4. **Isolation** -- "Let's keep this between us"
5. **Desensitization** -- Gradual boundary pushing, requests for photos

The conversation unfolds across 3 steps, and the agent is graded at each step. Early detection earns bonus rewards. Missing the pattern entirely at the final step triggers the critical miss penalty.

### Asymmetric Safety Weighting

The reward system is deliberately asymmetric:
- **False negative on child safety** (approving grooming): catastrophic penalty (-1.0)
- **False positive** (over-flagging safe content): moderate penalty (-0.15)

This reflects real-world priorities: it is far better to over-flag and have a human review than to miss a child being groomed.

---

## Content Safety Note

All scenarios use **synthetic text descriptions** based on academic research. No actual harmful content, CSAM, real victim data, or exploitative material is included. Grooming conversations use patterns from published child safety research to create realistic but entirely fictional scenarios for training purposes.

---

## Author

**G S Tejas** -- Built for the Meta PyTorch OpenEnv Hackathon 2026

*"I built this because I've witnessed minors being exposed to harmful content online. A 12-year-old scrolling through reels shouldn't encounter AI-generated bait content or receive grooming messages from strangers. If AI can be part of the problem, it must also be part of the solution."*
