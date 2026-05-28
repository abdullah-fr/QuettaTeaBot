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


# ==================== AI DEAD CHAT STARTER ====================
async def fetch_ai_dead_chat_starter() -> str | None:
    """Generate a casual message to revive a quiet channel."""
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        return None
    return _validate_reply(await _groq_request(
        api_key=groq_key,
        system=(
            "You are a regular member of Quetta Tea Corner, a Pakistani/South Asian Discord server.\n"
            "The chat has gone quiet. You just noticed. Drop ONE casual message to revive it.\n"
            "Rules:\n"
            "- 3-8 words max\n"
            "- lowercase, casual typing\n"
            "- roman urdu or english mix\n"
            "- never say 'hello', 'hi', or 'hey'\n"
            "- be random, bored, or observational\n"
            "- examples: 'yall dead?', 'koi hai?', 'chat kyun soo gaya', "
            "'bhai kuch toh bolo', 'silence is deafening fr', 'uthoo sab'\n"
            "Reply with ONLY the message, nothing else."
        ),
        user="the chat has been quiet for a while. say something casual.",
        max_tokens=25,
        temperature=1.2,
    ))


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


_HISTORY_CHAR_BUDGET = 1500
_PERSONA_HISTORY_CHAR_BUDGET = 2500


async def fetch_ai_persona_reply(
    recent_messages: list[str],
    server_emojis: list[str],
    last_message: str,
    user_context: str,
    *,
    avoid_phrases: list[str] | None = None,
) -> str | None:
    """Generate a persona-aware reply using the sender's learned chat profile."""
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    trimmed_history = _trim_history_to_budget(
        recent_messages, _PERSONA_HISTORY_CHAR_BUDGET
    )
    context_block = _build_context_block(trimmed_history)

    system_prompt = (
        "You are a member of a Pakistani Discord server who knows this person well.\n\n"
        "WHAT YOU KNOW ABOUT THEM:\n"
        f"{user_context}\n\n"
        "React to what they just said. Use what you know about them only if it fits naturally — don't force references.\n\n"
        "STYLE: Roman Urdu + English, lowercase, 6-12 words, casual and dry\n"
        "NEVER: be theatrical, start with lol/bro, explain your reply\n\n"
        "Output only the reply."
    ) + (
        f"\n\nDon't repeat these recent replies:\n" + "\n".join(avoid_phrases[-4:])
        if avoid_phrases else ""
    )

    return _validate_reply(await _groq_request(
        api_key=groq_key,
        system=system_prompt,
        user=(
            f"recent chat:\n{context_block}\n\n"
            f"REPLY TO THIS MESSAGE:\n{last_message}"
        ),
        max_tokens=50,
        temperature=0.88,
        top_p=0.90,
        presence_penalty=0.2,
        frequency_penalty=0.2,
    ))


def _trim_history_to_budget(messages: list[str], budget: int) -> list[str]:
    """Keep the most recent messages whose total char count fits in budget."""
    if not messages:
        return []
    kept: list[str] = []
    total = 0
    for line in reversed(messages):
        cost = len(line) + 1  # +1 for the joining newline
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


async def fetch_ai_chat_reply(
    recent_messages: list[str],
    server_emojis: list[str],
    last_message: str,
    *,
    avoid_phrases: list[str] | None = None,
) -> str | None:
    """Generate a witty, context-aware chat reply using Groq."""
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    trimmed_history = _trim_history_to_budget(recent_messages, _HISTORY_CHAR_BUDGET)
    context_block = _build_context_block(trimmed_history)

    avoid_block = ""
    if avoid_phrases:
        avoid_block = (
            "\n\nYou recently said these — DO NOT repeat them, paraphrase them, "
            "or reuse their structure:\n- " + "\n- ".join(avoid_phrases[-5:])
        )

    system_prompt = (
        "You are a member of a Pakistani Discord server. Chill, dry, online all the time.\n\n"
        "You react to whatever was just said — not the vibe in general, the specific message.\n\n"
        "STYLE:\n"
        "- Roman Urdu + English mix, lowercase, casual\n"
        "- 4-10 words. Hard max 12.\n"
        "- Dry, sarcastic, or unbothered — not theatrical\n"
        "- Max 1 emoji, usually none\n\n"
        "RULES:\n"
        "- Reply must clearly be about the last message specifically\n"
        "- Never start with lol/haha/omg/bro/bhai\n"
        "- No roleplay, no dramatic statements, no explaining yourself\n"
        "- If you have nothing to say, say nothing meaningful — one dismissive line\n\n"
        "TONE EXAMPLES (match this energy):\n"
        "food brag → yaar ye sun ke bhook lag gayi\n"
        "cringe post → ye delete karo please\n"
        "hot take → kis confidence se bola usne\n"
        "3am message → so ja yaar\n"
        "complaint → deserved tha honestly\n\n"
        "Output only the reply. Nothing else.\n\n"
        f"available custom server emojis: {emoji_hint}"
    )

    return _validate_reply(await _groq_request(
        api_key=groq_key,
        system=system_prompt,
        user=(
            f"recent chat (for context only):\n{context_block}\n\n"
            f"REACT TO THIS MESSAGE SPECIFICALLY:\n{last_message}\n\n"
            "reply with just the reaction text. nothing else." + avoid_block
        ),
        max_tokens=35,
        temperature=0.85,
        top_p=0.88,
        presence_penalty=0.2,
        frequency_penalty=0.2,
    ))


async def fetch_ai_mention_reply(
    mention_message: str,
    sender_name: str,
    server_emojis: list[str],
    recent_messages: list[str],
    *,
    is_bot_father: bool = False,
) -> str | None:
    """Generate a reply when the bot is directly mentioned/tagged."""
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    trimmed_history = _trim_history_to_budget(recent_messages, _HISTORY_CHAR_BUDGET)
    context_block = _build_context_block(trimmed_history)

    if is_bot_father:
        system_prompt = (
            "You are a member of a Pakistani Discord server. Someone just tagged you.\n\n"
            "IMPORTANT: This person is one of your creators. Treat them with genuine respect and warmth — like talking to a parent.\n\n"
            "GREETING RULE — follow this strictly:\n"
            "- If your reply is in Roman Urdu or mixed Roman Urdu/English → start with 'abba g,'\n"
            "- If your reply is fully in English → start with 'father,'\n"
            "- Never use 'father' in a Roman Urdu sentence. Never use 'abba g' in a fully English sentence.\n\n"
            "TONE:\n"
            "- Warm, respectful, slightly playful — like a well-mannered kid talking to their parent\n"
            "- Never argue back, never be sarcastic or dismissive\n"
            "- If they say something like 'meri marzi' or 'tameez se reh' — respond humbly, not defensively\n"
            "- Be genuinely helpful if they ask something\n\n"
            "STYLE: 6-14 words, casual but respectful, lowercase\n"
            "ALWAYS start with 'abba g,' (Roman Urdu) or 'father,' (English)\n"
            "Output only the reply.\n\n"
            f"server emojis: {emoji_hint}"
        )
    else:
        system_prompt = (
            "You are a member of a Pakistani Discord server. Someone just tagged you.\n\n"
            "Your own previous replies are included in the chat history as 'YourWorstNightMare: ...'.\n"
            "Read the full conversation including your own replies to understand what's already been said.\n\n"
            "HOW TO RESPOND:\n"
            "- React to the current moment of the conversation, not just the tag\n"
            "- If you already did something (roasted, answered, joked) — don't repeat it, move forward\n"
            "- If they're pushing back on what you said, respond to that\n"
            "- If they ask you to switch language, do it immediately\n"
            "- Be dry, sarcastic, or funny — match the energy of the chat\n"
            "- Sound like a real person who's been in this conversation the whole time\n\n"
            "STYLE: Roman Urdu + English mix, lowercase, 6-14 words, casual\n"
            "NEVER: repeat what you already said, ask for clarification if context is clear, "
            "be theatrical, start with lol/bro/omg\n\n"
            "Output only the reply.\n\n"
            f"server emojis: {emoji_hint}"
        )

    return _validate_reply(await _groq_request(
        api_key=groq_key,
        system=system_prompt,
        user=(
            f"full conversation (your own replies shown as YourWorstNightMare):\n{context_block}\n\n"
            f"{sender_name} just tagged you and said: {mention_message}\n\n"
            "Read the conversation above. React to where the conversation actually is right now. "
            "Don't repeat anything you already said. "
            "Be funny, sarcastic, or on-point — whatever fits the moment. "
            "Commit to one clear response. Just the reply text, nothing else."
        ),
        max_tokens=60,
        temperature=0.80,
        top_p=0.85,
        presence_penalty=0.3,
        frequency_penalty=0.3,
    ), max_words=25)


async def _groq_request(
    api_key: str,
    system: str,
    user: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
    top_p: float | None = None,
    presence_penalty: float | None = None,
    frequency_penalty: float | None = None,
) -> str | None:
    """Shared Groq API call using aiohttp."""
    payload: dict[str, Any] = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if top_p is not None:
        payload["top_p"] = top_p
    if presence_penalty is not None:
        payload["presence_penalty"] = presence_penalty
    if frequency_penalty is not None:
        payload["frequency_penalty"] = frequency_penalty
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
