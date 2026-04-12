---
title: SupportENV
emoji: 🎫
colorFrom: green
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# SupportEnv — Customer Support Ticket Triage

An **OpenEnv-compatible** environment where an AI agent receives customer support tickets and must **classify**, **prioritize**, and optionally **draft a reply**. The environment exposes Pydantic v2 models for observations, actions, and rewards, and includes a fully deterministic grader.

---

## Environment Overview

The agent processes one support ticket per episode. Depending on the task difficulty, it must produce varying levels of output:

| Task | Difficulty | Agent Must Provide |
|---|---|---|
| `classify` | Easy | `category` only |
| `prioritize` | Medium | `category` + `priority` |
| `resolve` | Hard | `category` + `priority` + `reply` |

---

## Observation Space

| Field | Type | Description |
|---|---|---|
| `ticket_id` | `str` | Unique identifier for the ticket |
| `ticket_text` | `str` | The customer's message |
| `task_name` | `str` | Current task (`classify`, `prioritize`, `resolve`) |
| `step_number` | `int` | Current step in the episode |

## Action Space

| Field | Type | Description |
|---|---|---|
| `category` | `str` | One of `billing`, `technical`, `general` |
| `priority` | `str` | One of `low`, `medium`, `high`, `urgent` |
| `reply` | `str` | Agent's drafted reply (optional for `classify`/`prioritize`) |

## Reward Range

`[0.0, 1.0]` — fully deterministic, based on exact match and keyword overlap.

---

## Scoring Breakdown

### Task 1 — `classify`
- **1.0** if `category` is correct, **0.0** otherwise.

### Task 2 — `prioritize`
- **0.5** × category match + **0.5** × priority match.

### Task 3 — `resolve`
- **0.3** × category match + **0.3** × priority match + **0.4** × reply quality.
- Reply quality = proportion of 5 ideal keywords found in the reply, scaled by 0.4.
- **−0.1 penalty** if the reply is empty or under 10 words.

---

## Setup & Running

### Prerequisites
- Docker installed, **or** Python 3.11+ with `pip`.

### Option A — Docker (recommended)

```bash
# Build the image
docker build -t supportenv .

# Run inference (set your HuggingFace token)
docker run -e HF_TOKEN="hf_your_token_here" supportenv
```

### Option B — Local Python

```bash
pip install pydantic openai pyyaml

# Set environment variables
export HF_TOKEN="hf_your_token_here"
# export API_BASE_URL="https://router.huggingface.co/v1"   # default
# export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"           # default

python inference.py
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `API_BASE_URL` | `https://router.huggingface.co/v1` | OpenAI-compatible API endpoint |
| `MODEL_NAME` | `Qwen/Qwen2.5-72B-Instruct` | Model identifier |
| `HF_TOKEN` | — | API / bearer token |

---

## Example Output

```
[START] task=classify env=supportenv model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action={"category":"billing","priority":"high","reply":""} reward=1.00 done=true error=null
[END] success=true steps=1 score=1.00 rewards=1.00
```

---

## Example Baseline Scores

Approximate scores using **Qwen2.5-72B-Instruct** with zero-shot prompting:

| Task | Expected Score |
|---|---|
| `classify` | ~0.85 |
| `prioritize` | ~0.65 |
| `resolve` | ~0.45 |

Scores will vary depending on the random ticket selection per episode.

---

## Project Structure

```
SupportENV/
├── app.py             # Flask server (web UI + REST API)
├── environment.py     # SupportEnv class + Pydantic models
├── tasks.py           # Task configs + 30 sample tickets
├── grader.py          # Deterministic scoring function
├── inference.py       # LLM agent loop (9 episodes)
├── openenv.yaml       # OpenEnv manifest
├── templates/
│   └── index.html     # Interactive web dashboard
├── static/            # Legacy static assets
├── Dockerfile         # Container setup
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/reset` | Start a new episode (accepts `task_name` in JSON body) |
| `POST` | `/step` | Submit an action (`category`, `priority`, `reply`) |
| `GET` | `/state` | Get current environment state |

---

## License

This project is provided as-is for educational and benchmarking purposes.
