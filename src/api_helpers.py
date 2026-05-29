from typing import Any

import aiohttp
import json
import random
import html
import re

try:
    from config import settings
    from logging_config import get_logger
    from retry_utils import HttpStatusError, RetryError, retry_async
except ImportError:
    from .config import settings
    from .logging_config import get_logger
    from .retry_utils import HttpStatusError, RetryError, retry_async

logger = get_logger(__name__)

_GEMINI_MODEL = "gemini-3.1-flash-lite"
_GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{_GEMINI_MODEL}:generateContent"
)


def _get_gemini_keys() -> list[str]:
    """Return all configured Gemini API keys as plain strings."""
    keys = []
    for attr in ("gemini_api_key_1", "gemini_api_key_2", "gemini_api_key_3", "gemini_api_key_4"):
        val = getattr(settings, attr, None)
        if not val:
            continue
        if hasattr(val, "get_secret_value"):
            keys.append(val.get_secret_value())
        else:
            keys.append(str(val))
    return keys


# Round-robin index — rotates across keys on each call
_gemini_key_index: int = 0


def _get_gemini_key() -> str | None:
    """Return the next available Gemini API key (round-robin)."""
    global _gemini_key_index
    keys = _get_gemini_keys()
    if not keys:
        return None
    key = keys[_gemini_key_index % len(keys)]
    _gemini_key_index = (_gemini_key_index + 1) % len(keys)
    return key


async def _fetch_json(
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    timeout: int = 15,
) -> Any:
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


# ==================== QOTD API ====================
async def fetch_qotd() -> str | None:
    data = await _fetch_json("https://api.quotable.io/quotes/random?limit=1")
    if data and len(data) > 0:
        try:
            return f"Reflect on this: \"{data[0]['content']}\" - What are your thoughts?"
        except Exception:
            logger.exception("QOTD API error")
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
    data = await _fetch_json("https://api.truthordarebot.xyz/v1/wyr")
    if data and "question" in data:
        return data["question"]
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
    data = await _fetch_json("https://compliments-api.herokuapp.com/compliment")
    if isinstance(data, dict) and "compliment" in data:
        return data["compliment"]
    data = await _fetch_json("https://www.affirmations.dev/")
    if isinstance(data, dict) and "affirmation" in data:
        return data["affirmation"]
    return None


# ==================== ROAST ====================
async def fetch_roast() -> None:
    return None


# ==================== HELPER UTILITIES ====================

def _trim_history_to_budget(messages: list[str], budget: int) -> list[str]:
    if not messages:
        return []
    kept: list[str] = []
    total = 0
    for line in reversed(messages):
        cost = len(line) + 1
        if total + cost > budget and kept:
            break
        kept.append(line)
        total += cost
    kept.reverse()
    return kept


def _sanitize_history_line(line: str) -> str:
    clean = line.strip()
    if not clean or len(clean) < 3:
        return ""
    if len(clean) > 200:
        clean = clean[:200] + "..."
    return clean


def _build_context_block(messages: list[str]) -> str:
    cleaned = [_sanitize_history_line(m) for m in messages]
    cleaned = [m for m in cleaned if m]
    return "\n".join(cleaned) if cleaned else "(no prior chat)"


_BANNED_OUTPUT_PHRASES = [
    "my whole",
    "digital sovereignty",
    "digital existence",
    "meditation",
    "abducted",
    "aliens",
    "as an ai",
    "i am a bot",
    "let me help",
    "great question",
]
_THEATRICAL_PATTERNS = [
    re.compile(r'\*[^*]+\*'),
    re.compile(r'"[^"]{30,}"'),
]


def _validate_reply(text: str | None, max_words: int = 16) -> str | None:
    if not text:
        return None
    lowered = text.lower()
    if any(phrase in lowered for phrase in _BANNED_OUTPUT_PHRASES):
        return None
    for pattern in _THEATRICAL_PATTERNS:
        if pattern.search(text):
            return None
    if len(text.split()) > max_words:
        return None
    banned_starts = ("lol", "haha", "omg", "bro,", "bhai,", "lmao")
    if lowered.startswith(banned_starts):
        return None
    return text.strip()


_HISTORY_CHAR_BUDGET = 1500
_PERSONA_HISTORY_CHAR_BUDGET = 2500


# ==================== GEMINI REQUEST ====================

async def _gemini_request(
    system: str,
    user: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
) -> str | None:
    """Shared Gemini API call with automatic key rotation on 429."""
    payload: dict[str, Any] = {
        "system_instruction": {
            "parts": [{"text": system}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user}]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }

    keys = _get_gemini_keys()
    if not keys:
        logger.warning("No Gemini API keys configured.")
        return None

    # Try each key once before giving up
    for attempt, key in enumerate(keys):
        async def _request(k=key):
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    _GEMINI_URL,
                    params={"key": k},
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=20),
                ) as resp:
                    text = await resp.text()
                    if resp.status == 429:
                        raise HttpStatusError(resp.status, text)
                    if resp.status in (500, 502, 503, 504):
                        raise HttpStatusError(resp.status, text)
                    if resp.status != 200:
                        logger.error(
                            "Gemini API error",
                            extra={"status": resp.status, "body": text[:300]},
                        )
                        return None
                    data = json.loads(text)
                    return (
                        data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    )

        try:
            result = await retry_async(
                _request,
                retries=1,
                delay=0.5,
                backoff=1.5,
                log_message=f"Gemini request retry (key {attempt + 1})",
            )
            if result is not None:
                return result
        except RetryError:
            if attempt < len(keys) - 1:
                logger.warning(
                    "Gemini key exhausted, rotating to next key",
                    extra={"key_index": attempt + 1},
                )
                continue
            logger.error("All Gemini keys exhausted after retries")
        except Exception:
            logger.exception("Gemini request error")
            return None

    return None


# ==================== AI DEAD CHAT STARTER ====================
async def fetch_ai_dead_chat_starter() -> str | None:
    if not _get_gemini_keys():
        return None
    return _validate_reply(await _gemini_request(
        system=(
            "You are a regular member of Quetta Tea Corner, a Pakistani/South Asian Discord server. "
            "The chat has gone quiet. Drop ONE casual message to revive it. "
            "3-8 words max. Lowercase. Roman Urdu or English mix. "
            "Never say hello/hi/hey. Be random, bored, or observational. "
            "Examples: 'yall dead?', 'koi hai?', 'chat kyun soo gaya', 'uthoo sab'. "
            "Output ONLY the message, nothing else."
        ),
        user="the chat has been quiet for a while. say something casual.",
        max_tokens=30,
        temperature=1.2,
    ))


# ==================== AI SUMMARIZATION ====================
async def fetch_ai_summary(messages_text: str) -> str | None:
    if not _get_gemini_keys():
        logger.warning("No Gemini API keys configured. Skipping AI summary.")
        return None
    return await _gemini_request(
        system=(
            "You are a Discord conversation summarizer. "
            "Your summaries are casual, accurate, and concise. "
            "Always mention key usernames. "
            "Output only the summary — no preamble, no title, no meta-commentary."
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
        max_tokens=400,
        temperature=0.5,
    )


# ==================== AI PERSONA REPLY ====================
async def fetch_ai_persona_reply(
    recent_messages: list[str],
    server_emojis: list[str],
    last_message: str,
    user_context: str,
    *,
    avoid_phrases: list[str] | None = None,
) -> str | None:
    if not _get_gemini_keys():
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    trimmed_history = _trim_history_to_budget(recent_messages, _PERSONA_HISTORY_CHAR_BUDGET)
    context_block = _build_context_block(trimmed_history)

    avoid_block = (
        f"\n\nDo not repeat these recent replies:\n" + "\n".join(avoid_phrases[-4:])
        if avoid_phrases else ""
    )

    system_prompt = (
        "You are a member of a Pakistani Discord server who knows this person well.\n\n"
        "ABOUT THIS PERSON:\n"
        f"{user_context}\n\n"
        "React to what they just said. Use what you know about them only if it fits naturally — never force it.\n\n"
        "STYLE: Roman Urdu + English mix, lowercase, 6-12 words, casual and dry.\n"
        "NEVER: be theatrical, start with lol/bro, explain your reply, use asterisks.\n"
        f"Available server emojis: {emoji_hint}\n\n"
        "Output only the reply, nothing else." + avoid_block
    )

    return _validate_reply(await _gemini_request(
        system=system_prompt,
        user=(
            f"Recent chat:\n{context_block}\n\n"
            f"Reply to this message: {last_message}"
        ),
        max_tokens=60,
        temperature=0.88,
    ))


# ==================== AI CHAT REPLY ====================
async def fetch_ai_chat_reply(
    recent_messages: list[str],
    server_emojis: list[str],
    last_message: str,
    *,
    avoid_phrases: list[str] | None = None,
) -> str | None:
    if not _get_gemini_keys():
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    trimmed_history = _trim_history_to_budget(recent_messages, _HISTORY_CHAR_BUDGET)
    context_block = _build_context_block(trimmed_history)

    avoid_block = ""
    if avoid_phrases:
        avoid_block = (
            "\n\nDo NOT repeat, paraphrase, or reuse the structure of these recent replies:\n- "
            + "\n- ".join(avoid_phrases[-5:])
        )

    system_prompt = (
        "You are a member of a Pakistani Discord server. Chill, dry, online all the time.\n\n"
        "React to the specific message given — not the general vibe.\n\n"
        "STYLE:\n"
        "- Roman Urdu + English mix, lowercase, casual\n"
        "- 4-10 words. Hard max 12.\n"
        "- Dry, sarcastic, or unbothered — never theatrical\n"
        "- Max 1 emoji, usually none\n\n"
        "RULES:\n"
        "- Reply must clearly be about the last message\n"
        "- Never start with lol/haha/omg/bro/bhai\n"
        "- No roleplay, no dramatic statements, no asterisks\n"
        "- One dismissive line if you have nothing to say\n\n"
        "TONE EXAMPLES:\n"
        "food brag → yaar ye sun ke bhook lag gayi\n"
        "cringe post → ye delete karo please\n"
        "hot take → kis confidence se bola usne\n"
        "3am message → so ja yaar\n"
        "complaint → deserved tha honestly\n\n"
        f"Available server emojis: {emoji_hint}\n\n"
        "Output only the reply. Nothing else." + avoid_block
    )

    return _validate_reply(await _gemini_request(
        system=system_prompt,
        user=(
            f"Recent chat (context only):\n{context_block}\n\n"
            f"React to this message specifically: {last_message}"
        ),
        max_tokens=40,
        temperature=0.85,
    ))


# ==================== AI MENTION REPLY ====================
async def fetch_ai_mention_reply(
    mention_message: str,
    sender_name: str,
    server_emojis: list[str],
    recent_messages: list[str],
) -> str | None:
    if not _get_gemini_keys():
        return None

    emoji_sample = random.sample(server_emojis, k=min(20, len(server_emojis)))
    emoji_hint = ", ".join(emoji_sample) if emoji_sample else "none available"
    trimmed_history = _trim_history_to_budget(recent_messages, _HISTORY_CHAR_BUDGET)
    context_block = _build_context_block(trimmed_history)

    system_prompt = (
        "You are a member of a Pakistani Discord server. Someone just tagged you.\n\n"
        "Your own previous replies appear in the chat history as 'YourWorstNightMare: ...'.\n"
        "Read the full conversation to understand what's already been said.\n\n"
        "HOW TO RESPOND:\n"
        "- React to the current moment, not just the tag\n"
        "- If you already roasted/answered/joked — don't repeat it, move forward\n"
        "- If they push back on what you said, respond to that\n"
        "- If they ask you to switch language, do it immediately\n"
        "- If asked to roast someone and you see their name in chat — DO IT immediately, "
        "use something they actually said, no questions asked\n"
        "- Be dry, sarcastic, or funny — match the energy\n\n"
        "STYLE: Roman Urdu + English mix, lowercase, 6-14 words, no asterisks.\n"
        "NEVER: repeat yourself, ask for clarification when context is clear, be theatrical, "
        "start with lol/bro/omg, or always use the same emoji.\n"
        f"Available server emojis: {emoji_hint}\n\n"
        "Output only the reply."
    )

    return _validate_reply(await _gemini_request(
        system=system_prompt,
        user=(
            f"Full conversation (your replies shown as YourWorstNightMare):\n{context_block}\n\n"
            f"{sender_name} tagged you and said: {mention_message}\n\n"
            "React to where the conversation is right now. Don't repeat anything you already said. "
            "Commit to one clear response. Just the reply text, nothing else."
        ),
        max_tokens=70,
        temperature=0.80,
    ), max_words=25)
