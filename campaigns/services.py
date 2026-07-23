"""
campaigns/services.py

Talks to Groq's OpenAI-compatible Chat Completions API to expand a brand's
rough 3-4 bullet points into a polished, detailed campaign title + description.
No new DB columns needed — output maps directly onto Campaign.title /
Campaign.description.

Kept out of views.py on purpose: views stay thin (HTTP + permissions), this
file owns the "business logic" of talking to the external AI API.
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
    "The brand will give you a handful of rough bullet points — sometimes just "
    "3-4 short phrases. Expand them into one complete, professional campaign brief.\n\n"
    "Respond with ONLY a valid JSON object — no markdown fences, no commentary, "
    "no text outside the JSON — with EXACTLY these two keys:\n"
    '  "title": string — a punchy campaign title, under 12 words.\n'
    '  "description": string — a detailed, well-organized campaign description, '
    "3-6 short paragraphs or bullet sections, written in plain text (you may use "
    "\"- \" for bullet lines). It MUST naturally cover, where relevant to the "
    "given points: what the campaign is about and its objective, the kind of "
    "influencers being sought (niche, audience, approximate follower range), "
    "the expected content deliverables (e.g. number of reels/posts/stories), "
    "3-6 suggested campaign hashtags starting with #, and posting guidelines "
    "(tone, mandatory #ad/paid-partnership disclosure, posting window). "
    "Do not invent specifics the brand didn't imply (like exact follower counts) "
    "unless it's a reasonable, clearly-labeled suggestion. "
    "IMPORTANT: Keep the entire description under 220 words total so the JSON "
    "response stays complete and well-formed — do not let it run on."
)


def _build_user_prompt(key_points, brand_name, category, platform, budget):
    lines = [f"Brand's rough campaign points:\n{key_points.strip()}"]
    if brand_name:
        lines.append(f"Brand name: {brand_name}")
    if category:
        lines.append(f"Category: {category}")
    if platform:
        lines.append(f"Primary platform: {platform}")
    if budget:
        lines.append(f"Budget: {budget}")
    return "\n".join(lines)


def generate_campaign_content(key_points, brand_name="", category="", platform="", budget=""):
    """
    Returns: {"title": str, "description": str}
    Raises CampaignAIGenerationError on any failure (missing key, network error,
    bad status code, unparsable response) so the view can return a clean HTTP
    error instead of a 500 stack trace.
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
            {"role": "user", "content": _build_user_prompt(key_points, brand_name, category, platform, budget)},
        ],
        "temperature": 0.7,
        "max_tokens": 1600,
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

    return {
        "title": str(parsed.get("title", "")).strip(),
        "description": str(parsed.get("description", "")).strip(),
    }