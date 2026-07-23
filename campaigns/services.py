"""
campaigns/services.py

Talks to Groq's OpenAI-compatible Chat Completions API to auto-generate a
professional campaign brief (title, description, requirements, deliverables,
hashtags, posting guidelines) from a few basic inputs the brand provides.

Kept out of views.py on purpose: views should stay thin (HTTP + permissions),
this file owns the "business logic" of talking to the external AI API.
"""
import os
import json
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
REQUEST_TIMEOUT_SECONDS = 20


class CampaignAIGenerationError(Exception):
    """Raised for any failure while generating campaign content via Groq."""
    pass


SYSTEM_PROMPT = (
    "You are a senior influencer-marketing strategist who writes campaign briefs "
    "for a brand-influencer collaboration platform called EaseMyCollab. "
    "Given a short campaign brief from a brand, generate a complete, professional "
    "campaign brief. "
    "Respond with ONLY a valid JSON object — no markdown fences, no commentary, "
    "no text outside the JSON — with EXACTLY these keys:\n"
    '  "title": string — a punchy campaign title, under 12 words.\n'
    '  "description": string — 3-5 sentence detailed campaign description covering '
    "what the brand wants and why.\n"
    '  "influencer_requirements": string — bullet-style text (use "- " per line) '
    "describing minimum follower count, niche fit, audience demographics and "
    "engagement rate expectations.\n"
    '  "deliverables": string — bullet-style text (use "- " per line) listing the '
    "exact content deliverables, e.g. number of reels/posts/stories and timeline.\n"
    '  "hashtags": array of 6 to 10 strings, each starting with "#", no spaces, '
    "relevant to the brand/category/platform.\n"
    '  "posting_guidelines": string — bullet-style text (use "- " per line) on tone, '
    "mandatory disclosure (#ad / paid partnership tag), posting window, and brand "
    "tagging rules."
)


def _build_user_prompt(brand_name, category, target_influencers, budget, objectives, platform):
    return (
        f"Brand name: {brand_name}\n"
        f"Campaign category: {category}\n"
        f"Target influencers: {target_influencers}\n"
        f"Budget: {budget}\n"
        f"Campaign objectives: {objectives}\n"
        f"Primary platform: {platform}\n"
    )


def generate_campaign_content(brand_name, category, target_influencers, budget, objectives, platform):
    """
    Returns a dict:
    {
        "title": str, "description": str, "influencer_requirements": str,
        "deliverables": str, "hashtags": list[str], "posting_guidelines": str,
    }
    Raises CampaignAIGenerationError on any failure.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise CampaignAIGenerationError(
            "GROQ_API_KEY is not configured on the server. Set it as an environment variable."
        )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(
                brand_name, category, target_influencers, budget, objectives, platform
            )},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.exceptions.RequestException as e:
        raise CampaignAIGenerationError(f"Could not reach Groq API: {e}")

    if resp.status_code != 200:
        raise CampaignAIGenerationError(
            f"Groq API returned an error ({resp.status_code}): {resp.text[:300]}"
        )

    try:
        raw_content = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(raw_content)
    except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
        raise CampaignAIGenerationError(f"Could not parse the AI response: {e}")

    hashtags = parsed.get("hashtags", [])
    if isinstance(hashtags, str):
        hashtags = [h.strip() for h in hashtags.replace(",", " ").split() if h.strip()]
    hashtags = [h if h.startswith("#") else f"#{h}" for h in hashtags]

    return {
        "title": str(parsed.get("title", "")).strip(),
        "description": str(parsed.get("description", "")).strip(),
        "influencer_requirements": str(parsed.get("influencer_requirements", "")).strip(),
        "deliverables": str(parsed.get("deliverables", "")).strip(),
        "hashtags": hashtags,
        "posting_guidelines": str(parsed.get("posting_guidelines", "")).strip(),
    }