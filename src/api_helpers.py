from typing import Any

import aiohttp
import json
import random
import html

try:
    from config import settings
    from logging_config import get_logger
except ImportError:
    from .config import settings
    from .logging_config import get_logger
from .retry_utils import HttpStatusError, RetryError, retry_async

logger = get_logger(__name__)


async def _fetch_json(
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    timeout: int = 15,
) -> Any:
    """Fetch and decode JSON. Returns the parsed body (dict/list) or None.

    Typed as Any because response shapes vary per endpoint and callers know
    the expected schema.
    """

    async def _request() -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                text = await resp.text()
                if resp.status in (429, 500, 502, 503, 504):
                    raise HttpStatusError(resp.status, text)
                if resp.status != 200:
                    logger.warning(
                        "Non-success HTTP status",
                        extra={"url": url, "status": resp.status, "body": text[:300]},
                    )
                    return None
                return await resp.json()

    try:
        return await retry_async(
            _request,
            retries=2,
            delay=0.8,
            backoff=2.0,
            log_message=f"HTTP GET retry for {url}",
        )
    except RetryError:
        logger.error("Failed to fetch JSON after retries", extra={"url": url})
        return None


async def _fetch_text(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: int = 15,
) -> str | None:
    async def _request() -> str | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                text = await resp.text()
                if resp.status in (429, 500, 502, 503, 504):
                    raise HttpStatusError(resp.status, text)
                if resp.status != 200:
                    logger.warning(
                        "Non-success HTTP status",
                        extra={"url": url, "status": resp.status, "body": text[:300]},
                    )
                    return None
                return text

    try:
        return await retry_async(
            _request,
            retries=2,
            delay=0.8,
            backoff=2.0,
            log_message=f"HTTP GET retry for {url}",
        )
    except RetryError:
        logger.error("Failed to fetch text after retries", extra={"url": url})
        return None


# ==================== TRIVIA API ====================
async def fetch_trivia_question() -> dict | None:
    """Fetch unlimited trivia from Open Trivia Database"""
    data = await _fetch_json("https://opentdb.com/api.php?amount=1&type=multiple")
    if not data or data.get("response_code") != 0:
        return None

    try:
        q_data = data["results"][0]
        question = html.unescape(q_data["question"])
        correct = html.unescape(q_data["correct_answer"])
        incorrect = [html.unescape(ans) for ans in q_data["incorrect_answers"]]
        options = incorrect + [correct]
        random.shuffle(options)
        return {"q": question, "a": correct, "options": options}
    except Exception:
        logger.exception("Trivia API error")
        return None


# ==================== RIDDLE API ====================
async def fetch_riddle() -> dict | None:
    """Fetch riddles from API Ninjas"""
    headers = {
        "X-Api-Key": (
            settings.api_ninjas_key.get_secret_value()
            if settings.api_ninjas_key
            else ""
        )
    }
    data = await _fetch_json("https://api.api-ninjas.com/v1/riddles", headers=headers)
    if not data:
        return None

    try:
        return {"q": data[0]["question"], "a": data[0]["answer"]}
    except Exception:
        logger.exception("Riddle API error")
        return None


# ==================== JOKE API ====================
async def fetch_joke() -> str | None:
    """Fetch jokes from JokeAPI"""
    data = await _fetch_json("https://v2.jokeapi.dev/joke/Any?safe-mode")
    if not data:
        return None

    try:
        if data["type"] == "single":
            return data["joke"]
        return f"{data['setup']}\n{data['delivery']}"
    except Exception:
        logger.exception("Joke API error")
        return None


# ==================== QOTD API (Unlimited) ====================
async def fetch_qotd() -> str | None:
    """Fetch unlimited conversation questions"""
    data = await _fetch_json("https://api.quotable.io/quotes/random?limit=1")
    if data and len(data) > 0:
        try:
            return (
                f"Reflect on this: \"{data[0]['content']}\" - What are your thoughts?"
            )
        except Exception:
            logger.exception("QOTD API error")

    # Fallback: Use philosophy questions
    data = await _fetch_json("https://opentdb.com/api.php?amount=1&category=9")
    if not data or data.get("response_code") != 0:
        return None

    try:
        q_data = data["results"][0]
        question = html.unescape(q_data["question"])
        return f"What do you think: {question}"
    except Exception:
        logger.exception("QOTD Fallback error")
        return None


# ==================== WOULD YOU RATHER API ====================
async def fetch_wyr() -> str | None:
    """Fetch unlimited Would You Rather questions"""
    data = await _fetch_json("https://api.truthordarebot.xyz/v1/wyr")
    if data and "question" in data:
        return data["question"]

    # Fallback: Generate from two random activities
    data1 = await _fetch_json("https://www.boredapi.com/api/activity")
    data2 = await _fetch_json("https://www.boredapi.com/api/activity")
    if not data1 or not data2 or "activity" not in data1 or "activity" not in data2:
        return None

    try:
        return (
            f"Would you rather {data1['activity'].lower()} or "
            f"{data2['activity'].lower()}?"
        )
    except Exception:
        logger.exception("WYR Fallback error")
        return None


# ==================== CONVERSATION STARTER API ====================
async def fetch_conversation_starter() -> str | None:
    """Fetch unlimited conversation starters"""
    text = await _fetch_text(
        "https://api.adviceslip.com/advice",
        headers={"Accept": "application/json"},
    )
    if text:
        try:
            data = json.loads(text)
            if "slip" in data:
                return f"Let's talk about: {data['slip']['advice']}"
        except Exception:
            logger.exception("Conversation API error")

    # Fallback: Random interesting fact
    data = await _fetch_json("https://uselessfacts.jsph.pl/random.json?language=en")
    if not data or "text" not in data:
        return None

    try:
        return f"Interesting fact: {data['text']} - What do you think?"
    except Exception:
        logger.exception("Conversation Fallback error")
        return None


# ==================== COMPLIMENT API ====================
async def fetch_compliment() -> str | None:
    """Fetch unlimited compliments"""
    data = await _fetch_json("https://compliments-api.herokuapp.com/compliment")
    if isinstance(data, dict) and "compliment" in data:
        return data["compliment"]

    # Fallback: Affirmations
    data = await _fetch_json("https://www.affirmations.dev/")
    if isinstance(data, dict) and "affirmation" in data:
        return data["affirmation"]

    return None


# ==================== ROAST (Clean & Friendly Only) ====================
async def fetch_roast() -> None:
    """Always use our clean, friendly roast list - NO API"""
    # All roast APIs contain inappropriate content
    # We ONLY use our curated clean list from question_bank.py
    return None


# ==================== AI SUMMARIZATION ====================
async def fetch_ai_summary(messages_text: str) -> str | None:
    """Generate conversation summary using Groq (free)"""
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        logger.warning("GROQ_API_KEY not set. Skipping Groq requests.")
        return None
    return await _groq_request(
        api_key=groq_key,
        system=(
            "You are a Discord conversation summarizer. Your summaries are casual, "
            "accurate, and concise. Always mention key usernames. Output only the "
            "summary — no preamble, no title, no meta-commentary."
        ),
        user=(
            f"Summarize the following Discord conversation.\n\n"
            f"Rules:\n"
            f"- 100 to 150 words max\n"
            f"- 2 to 3 short paragraphs\n"
            f"- Mention usernames when describing key moments\n"
            f"- Skip spam, repeated emojis, and filler messages\n"
            f"- Highlight funny moments, debates, or notable interactions\n"
            f"- Capture the overall vibe (e.g. chaotic, chill, sarcastic)\n"
            f"- Use a casual tone with a few relevant emojis\n"
            f"- Start directly with the summary, no heading\n\n"
            f"Conversation:\n{messages_text}"
        ),
        max_tokens=350,
    )


async def fetch_ai_chat_reply(
    recent_messages: list[str], server_emojis: list[str]
) -> str | None:
    """Generate a witty, context-aware chat reply using Groq."""
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    conversation = "\n".join(recent_messages[-10:])

    return await _groq_request(
        api_key=groq_key,
        system=(
            "You are QuettaTeaBot, a funny, witty, slightly chaotic bot member "
            "in a Pakistani/South Asian server called Quetta Tea Corner. "
            "You talk like a real server member — casual Urdu/English mix is fine. "
            "You are NOT a helpful assistant. You are a funny, sarcastic, hype-giving "
            "community member who occasionally roasts, hypes, acts confused, or drops "
            "one-liners. Never sound like an AI. Never be generic. Never be cringe. "
            "STRICT STYLE RULES:\n"
            "- Keep replies under 12 words MOST of the time\n"
            "- Sometimes use lowercase only\n"
            "- Sometimes send short reactions only (e.g. 'bro 💀', 'nahh', "
            "  'average activities')\n"
            "- Sometimes act confused\n"
            "- Sometimes roast lightly\n"
            "- Never start with 'lol' every time\n"
            "- Never use full sentences every time\n"
            "- Never sound like a helpful assistant\n"
            "- Use 0 to 2 custom emojis max, only when they genuinely fit\n"
            "- Never spam emojis\n"
            f"Available custom server emojis: {emoji_hint}"
        ),
        user=(
            f"Recent chat:\n{conversation}\n\n"
            "Drop ONE short natural reaction that fits the vibe. "
            "Examples of good style: 'bro got exposed 😭', 'nahhhh', "
            "'average faisalabad activities', 'who let bro cook', "
            "'this convo declining rapidly 💀'. "
            "Max 12 words. Be unpredictable."
        ),
        max_tokens=60,
        temperature=1.15,
    )


async def _groq_request(
    api_key: str,
    system: str,
    user: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
) -> str | None:
    """Shared Groq API call using aiohttp."""
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async def _request():
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                text = await resp.text()
                if resp.status in (429, 500, 502, 503, 504):
                    raise HttpStatusError(resp.status, text)
                if resp.status != 200:
                    logger.error(
                        "Groq API error", extra={"status": resp.status, "body": text}
                    )
                    return None

                data = json.loads(text)
                return data["choices"][0]["message"]["content"].strip()

    try:
        return await retry_async(
            _request,
            retries=2,
            delay=0.8,
            backoff=2.0,
            log_message="Groq request retry",
        )
    except RetryError:
        logger.error("Failed to fetch Groq response after retries")
    except Exception:
        logger.exception("Groq request error")
    return None
