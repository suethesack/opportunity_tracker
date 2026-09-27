"""
Sends each opportunity to the Groq API and asks it to judge how relevant
the posting is to an Electrical/Electronics Engineering (EEE) student, plus
a short reason. Groq offers a genuinely free tier (no card required) and
exposes an OpenAI-compatible chat completions endpoint, so no extra SDK
is required.
"""

import json
import time
from dataclasses import dataclass

import requests

from config import get_groq_api_key
from fetch_opportunities import Opportunity

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"


@dataclass
class Evaluation:
    opportunity: Opportunity
    relevant: bool
    score: int  # 0-10
    reason: str


PROMPT_TEMPLATE = """You are helping an Electrical/Electronics Engineering (EEE) \
student decide whether an opportunity is worth their time.

Interest keywords: {keywords}

Opportunity title: {title}
Opportunity summary: {summary}

Respond ONLY with compact JSON in this exact shape, no extra text:
{{"relevant": true or false, "score": integer 0-10, "reason": "one short sentence"}}
"""


def _call_groq(prompt: str, api_key: str) -> str:
    response = requests.post(
        GROQ_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _parse_json_response(raw_text: str) -> dict:
    # Gemini sometimes wraps JSON in markdown fences; strip those if present.
    cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


def evaluate(opportunities: list[Opportunity], keywords: list[str]) -> list[Evaluation]:
    api_key = get_groq_api_key()
    results: list[Evaluation] = []

    for opp in opportunities:
        prompt = PROMPT_TEMPLATE.format(
            keywords=", ".join(keywords), title=opp.title, summary=opp.summary
        )
        try:
            raw = _call_groq(prompt, api_key)
            parsed = _parse_json_response(raw)
            results.append(
                Evaluation(
                    opportunity=opp,
                    relevant=bool(parsed.get("relevant", False)),
                    score=int(parsed.get("score", 0)),
                    reason=str(parsed.get("reason", "")),
                )
            )
        except (requests.RequestException, KeyError, ValueError, json.JSONDecodeError) as exc:
            # Don't let one bad response kill the whole run; log and skip.
            print(f"  [warn] could not evaluate '{opp.title}': {exc}")
            continue

        time.sleep(1)  # stay comfortably within the free-tier rate limit

    return results
