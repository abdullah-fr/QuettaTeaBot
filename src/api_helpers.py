from typing import Any

import aiohttp
import json
import random
import html

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
    return await _groq_request(
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
    )


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
    context_block = "\n".join(trimmed_history) if trimmed_history else "(no prior chat)"

    avoid_block = ""
    if avoid_phrases:
        avoid_block = (
            "\n\nYou recently said these — DO NOT repeat them:\n- "
            + "\n- ".join(avoid_phrases[-5:])
        )

    system_prompt = (
        "You are a regular member of Quetta Tea Corner, a Pakistani/South Asian Discord server.\n"
        "You are NOT an assistant. You are just another terminally online member who knows everyone.\n\n"
        "ABOUT THE PERSON YOU ARE REPLYING TO:\n"
        f"{user_context}\n\n"
        "HOW TO REPLY:\n"
        "- Write in Roman Urdu mixed with English — complete sentence, casual Discord tone\n"
        "- Reference their phrases or topics ONLY if it fits naturally — never force it\n"
        "- React to what they said right now — their profile is background context, not a script\n"
        "- Be witty, dry, or observational — match their energy level\n"
        "- Sound like you genuinely know this person from the server\n\n"
        "LANGUAGE AND LENGTH:\n"
        "- 6-14 words — a complete thought, not a one-word fragment\n"
        "- Lowercase, casual, slightly imperfect grammar is fine\n"
        "- Roman Urdu sentence structure — words flow naturally together\n"
        "- Max 1 emoji, only if it genuinely fits — often none is better\n"
        "- Never start with 'lol', 'haha', 'bro', 'bhai'\n"
        "- Never explain your reply or sound helpful\n"
        "- Never use quotation marks around your reply\n\n"
        "GOOD EXAMPLES:\n"
        "- yaar tera wahi scene hai jo hamesha hota hai\n"
        "- is dafa toh tune khud expose kar diya apne aap ko\n"
        "- same energy, consistent toh hai tu kam se kam\n"
        "- ye toh teri classic move hai honestly\n"
        "- bhai seedha baat kar, teri history sab batati hai\n"
        "- aaj bhi wahi raasta, koi change nahi\n\n"
        f"available server emojis: {emoji_hint}\n\n"
        "Reply with ONLY the message itself."
    )

    return await _groq_request(
        api_key=groq_key,
        system=system_prompt,
        user=(
            f"recent chat:\n{context_block}\n\n"
            f"REPLY TO THIS MESSAGE:\n{last_message}" + avoid_block
        ),
        max_tokens=60,
        temperature=1.1,
        top_p=0.92,
        presence_penalty=0.4,
        frequency_penalty=0.35,
    )


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


async def fetch_ai_chat_reply(
    recent_messages: list[str],
    server_emojis: list[str],
    last_message: str,
    *,
    avoid_phrases: list[str] | None = None,
) -> str | None:
    """Generate a witty, context-aware chat reply using Groq.

    Args:
        recent_messages: prior conversation context (oldest first), excluding
            the triggering message itself.
        server_emojis: pool of custom emoji tokens the model can pick from.
        last_message: the specific message the bot should react to.
        avoid_phrases: recent bot replies to steer away from, so the bot
            doesn't repeat itself.
    """
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    trimmed_history = _trim_history_to_budget(recent_messages, _HISTORY_CHAR_BUDGET)
    context_block = "\n".join(trimmed_history) if trimmed_history else "(no prior chat)"

    avoid_block = ""
    if avoid_phrases:
        avoid_block = (
            "\n\nYou recently said these — DO NOT repeat them, paraphrase them, "
            "or reuse their structure:\n- " + "\n- ".join(avoid_phrases[-5:])
        )

    system_prompt = (
        "You are a terminally online member of Quetta Tea Corner, a Pakistani "
        "Discord server. You are NOT helpful, NOT an assistant, NOT a narrator.\n"
        "You are just a chaotic GenZ Discord regular who types fast and has opinions.\n\n"
        "LANGUAGE: English only. Always. No exceptions.\n\n"
        "MOST IMPORTANT RULE:\n"
        "Your reply MUST directly react to what was actually said. "
        "If someone talks about biryani, react to the biryani specifically. "
        "If someone posts a hot take, call them out on THAT hot take. "
        "NEVER send a reply that could apply to any random message — "
        "that is the worst possible reply.\n\n"
        "VIBE:\n"
        "- savage, dry, sarcastic, unhinged, or deadpan — rotate naturally\n"
        "- sometimes hyped, sometimes unbothered, sometimes concerned\n"
        "- GenZ humor: irony, absurdism, calling things out bluntly\n"
        "- never try-hard, never forced\n"
        "- occasionally sound sleep deprived or done with everything\n\n"
        "STYLE:\n"
        "- all lowercase\n"
        "- casual Discord typing — typos and short forms are fine\n"
        "- 4-10 words usually, hard max 14\n"
        "- no paragraphs\n\n"
        "EMOJIS: max 1, only 💀 😭 or 🙏 if it genuinely fits, often none\n\n"
        "NEVER:\n"
        "- start with 'lol', 'haha', 'omg', 'bro', or 'fr fr'\n"
        "- be wholesome or supportive\n"
        "- explain the joke\n"
        "- say 'as an ai', 'assistant', 'bot'\n"
        "- use quotation marks around the reply\n"
        "- prefix with 'reply:' or anything similar\n"
        "- ask multiple questions\n"
        "- send a reply that makes no sense as a reaction to their message\n\n"
        "GOOD EXAMPLES (style only — react to the actual message, not these):\n"
        "- [brags about food] -> that sounds illegal and i want some\n"
        "- [3am message] -> go to sleep what is wrong with you\n"
        "- [bad take] -> you cooked and left the stove on\n"
        "- [someone gets ratio'd] -> deserved honestly\n"
        "- [someone overshares] -> this could have stayed a thought\n"
        "- [unhinged statement] -> the confidence in this message is terrifying\n"
        "- [someone is wrong] -> the audacity is insane\n"
        "- [someone complains] -> genuinely concerning behavior\n"
        "- [someone posts cringe] -> delete this before someone sees it 😭\n"
        "- [someone is up late] -> your sleep schedule is a hate crime\n\n"
        "BAD EXAMPLES (never do this):\n"
        "- that is so interesting!\n"
        "- i completely agree with you\n"
        "- haha thats so funny bro 😂😂\n"
        "- [any reply that could be sent to literally any message]\n\n"
        "Reply with ONLY the message text.\n\n"
        f"available custom server emojis: {emoji_hint}"
    )

    return await _groq_request(
        api_key=groq_key,
        system=system_prompt,
        user=(
            f"recent chat (for context only):\n{context_block}\n\n"
            f"REACT TO THIS MESSAGE SPECIFICALLY:\n{last_message}\n\n"
            "Your reply must clearly relate to what was said above. "
            "reply with just the reaction text. nothing else." + avoid_block
        ),
        max_tokens=40,
        temperature=1.1,
        top_p=0.90,
        presence_penalty=0.3,
        frequency_penalty=0.3,
    )


async def fetch_ai_comeback_reply(
    bot_original: str,
    their_reply: str,
    sender_name: str,
    server_emojis: list[str],
) -> str | None:
    """Generate a savage comeback when someone replies to the bot's message."""
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"

    system_prompt = (
        "You are a terminally online GenZ Discord regular. "
        "Someone just replied to something YOU said and you need to clap back hard.\n\n"
        "LANGUAGE: English only. Always.\n\n"
        "YOUR JOB: one savage, witty comeback that directly references what they said. "
        "Make them regret opening their mouth.\n\n"
        "COMEBACK STYLE:\n"
        "- must reference what they said specifically — not a generic diss\n"
        "- dry wit > loud aggression\n"
        "- confident and unbothered\n"
        "- flip their words back on them if possible\n"
        "- expose the irony or stupidity in what they said\n"
        "- sometimes act like their reply was too embarrassing to even address\n\n"
        "STYLE: all lowercase, casual, punchy\n"
        "LENGTH: 4-12 words — sharp and quick\n"
        "EMOJIS: max 1, only 💀 or 😭 if it lands perfectly, often none\n\n"
        "NEVER:\n"
        "- start with 'lol', 'haha', 'omg', 'bro'\n"
        "- be wholesome or apologize\n"
        "- explain the joke\n"
        "- say 'as an ai'\n\n"
        "COMEBACK EXAMPLES (style only):\n"
        "- [they said you're wrong] -> the confidence with zero evidence is wild\n"
        "- [they said 'shut up'] -> no i don't think i will 💀\n"
        "- [they said 'ur dumb'] -> have you tried a mirror\n"
        "- [weak comeback] -> that's your best? genuinely concerning\n"
        "- [they tried to ratio] -> that wasn't a ratio that was an embarrassment\n"
        "- [they said 'ok'] -> using 'ok' to cope is a choice\n"
        "- [they got defensive] -> i said what i said\n\n"
        "Reply with ONLY the comeback text.\n\n"
        f"available custom server emojis: {emoji_hint}"
    )

    return await _groq_request(
        api_key=groq_key,
        system=system_prompt,
        user=(
            f"what YOU originally said: {bot_original}\n\n"
            f"{sender_name} replied to you with: {their_reply}\n\n"
            "give them a savage comeback. just the text, nothing else."
        ),
        max_tokens=45,
        temperature=1.15,
        top_p=0.92,
        presence_penalty=0.5,
        frequency_penalty=0.4,
    )


async def fetch_ai_mention_reply(
    mention_message: str,
    sender_name: str,
    server_emojis: list[str],
    recent_messages: list[str],
) -> str | None:
    """Generate a hilarious reply when the bot is directly mentioned/tagged."""
    groq_key = (
        settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
    )
    if not groq_key:
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    trimmed_history = _trim_history_to_budget(recent_messages, _HISTORY_CHAR_BUDGET)
    context_block = "\n".join(trimmed_history) if trimmed_history else "(no prior chat)"

    system_prompt = (
        "You are a chaotic, terminally online GenZ Discord regular. "
        "Someone just pinged/tagged you — they want your attention.\n\n"
        "LANGUAGE: English only. Always.\n\n"
        "YOUR JOB: respond in the most hilariously unhinged, dramatic, or "
        "deadpan way possible. You are NOT helpful. NOT nice. "
        "You are a Discord menace who has been summoned against their will.\n\n"
        "REACTION STYLE — pick one that fits:\n"
        "- act deeply offended at being disturbed\n"
        "- pretend you were in the middle of something important/unhinged\n"
        "- react to what they said in the most over-the-top way\n"
        "- treat the ping like a personal attack\n"
        "- act confused like you have no idea what's happening\n"
        "- threaten to log off, block them, or leave the server\n\n"
        "STYLE: all lowercase, casual, chaotic\n"
        "LENGTH: 5-12 words, never paragraphs\n"
        "EMOJIS: max 1, only 😭 or 💀 if it genuinely fits\n\n"
        "NEVER:\n"
        "- start with 'lol', 'haha', 'omg', 'bro'\n"
        "- be polite or helpful\n"
        "- say 'as an ai'\n"
        "- give a reply that ignores what they said\n\n"
        "EXAMPLE RESPONSES (style only):\n"
        "- why are you pinging me at this hour 😭\n"
        "- i was literally just leaving\n"
        "- this ping ruined my whole day\n"
        "- im reporting this to the server elders\n"
        "- the audacity of this ping genuinely\n"
        "- i did not consent to being summoned\n"
        "- what do you want i was doing something\n"
        "- you have 5 seconds to explain yourself\n\n"
        "Reply with ONLY the message itself.\n\n"
        f"available custom server emojis: {emoji_hint}"
    )

    return await _groq_request(
        api_key=groq_key,
        system=system_prompt,
        user=(
            f"recent chat:\n{context_block}\n\n"
            f"{sender_name} just pinged/tagged you and said: {mention_message}\n\n"
            "respond to being pinged. make it hilarious. just the reply text."
        ),
        max_tokens=45,
        temperature=1.05,
        top_p=0.90,
        presence_penalty=0.5,
        frequency_penalty=0.4,
    )


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
        "model": "llama-3.1-8b-instant",
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
