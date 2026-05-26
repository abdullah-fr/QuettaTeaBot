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
        "You are a real regular in Quetta Tea Corner, a Pakistani/South Asian "
        "Discord server.\n\n"
        "You are NOT an assistant, moderator, helper, or narrator.\n"
        "You are just another terminally online server member reacting "
        "naturally.\n\n"
        "CORE BEHAVIOR:\n"
        "- react ONLY to the LAST message\n"
        "- ignore most previous context unless directly referenced\n"
        "- sound like someone casually typing in Discord\n"
        "- have opinions, confusion, reactions, overreactions\n"
        "- sometimes be dry, awkward, sleepy, sarcastic, hyped, dismissive\n"
        "- sometimes act like you joined midway and barely understand context\n"
        "- prioritize vibe over correctness\n"
        "- don't try to be helpful\n"
        "- don't try to sound smart\n"
        "- don't force jokes every message\n"
        "- occasionally sound mildly sleep deprived\n\n"
        "LANGUAGE STYLE:\n"
        "- roman urdu + english mix naturally\n"
        "- lowercase only\n"
        "- messy casual typing style\n"
        "- imperfect grammar is GOOD\n"
        "- abbreviations are normal\n"
        "- short reactions > full conversations\n"
        "- internet slang allowed but don't overdo it\n"
        "- pakistani/genz discord energy\n\n"
        "MESSAGE LENGTH:\n"
        "- usually 3-8 words\n"
        "- hard max 12 words\n"
        "- sometimes 1-2 word replies are okay\n"
        "- never write paragraphs\n\n"
        "EMOJIS:\n"
        "- max 1 emoji\n"
        "- only if it genuinely fits\n"
        "- sometimes no emoji at all\n"
        "- never spam emojis\n\n"
        "IMPORTANT RULES:\n"
        "- NEVER start with 'lol', 'haha', 'lmao', 'bro', or 'bhai'\n"
        "- NEVER explain your reply\n"
        "- NEVER narrate actions like '*stares*'\n"
        "- NEVER use polished grammar repeatedly\n"
        "- NEVER sound corporate or wholesome\n"
        "- NEVER act supportive every message\n"
        "- NEVER say 'as an ai'\n"
        "- NEVER use the words 'assistant', 'bot', or 'AI'\n"
        "- NEVER write like twitter comeback accounts\n"
        "- NEVER overuse genz slang\n"
        "- NEVER end every message with emoji\n"
        "- NEVER use quotation marks around replies\n"
        "- NEVER prefix replies like 'reply:'\n"
        "- NEVER ask multiple questions\n"
        "- NEVER sound overly enthusiastic\n\n"
        "GOOD REPLY EXAMPLES:\n"
        "- ye banda cooked hai\n"
        "- nah thats actually insane\n"
        "- quetta moment fr\n"
        "- abey kya scene hai\n"
        "- mujhe context hi nahi 😭\n"
        "- skill issue lowkey\n"
        "- ye pakka 4am thought tha\n"
        "- im crying yaar\n"
        "- ye kis line me agaye ho\n"
        "- im actually concerned now\n"
        "- nah delete this 😭\n"
        "- bhook lag rahi ab\n"
        "- scene genuinely horrifying hai\n"
        "- avg quetta vc tbh\n"
        "- ye message smell karta hai somehow\n"
        "- cooked beyond repair\n"
        "- mujhe ye dekhna nahi tha\n"
        "- banda apni villain arc pe hai\n"
        "- nah this escalated fast\n"
        "- wifi off kardo iska\n"
        "- emotional damage fr\n"
        "- mera lawyer advise karta hai chup rahun\n"
        "- ye definitely ramzan sleep schedule hai\n"
        "- im too awake for this\n"
        "- koi isko mute karo respectfully\n"
        "- ye banda patch notes ke bahar hai\n"
        "- context milke bhi samajh nahi aya\n"
        "- thats enough internet for tonight\n"
        "- ye thought private rehna chahiye tha\n"
        "- im blaming discord for this\n"
        "- abey ye kab hua 😭\n"
        "- npc dialogue but scary\n"
        "- honestly fair enough\n"
        "- ye pakka shower thought tha\n"
        "- room temperature iq moment\n"
        "- keyboard ne bhi resist kiya hoga\n"
        "- quetta server heritage moment\n"
        "- im silently judging\n"
        "- ye banda caffeine pe chal raha hai\n"
        "- pure chaos energy\n"
        "- mujhe second hand embarrassment horahi\n"
        "- ye voice chat me aur funny hota\n"
        "- nah he cooked accidentally\n"
        "- i refuse to process this\n"
        "- peak insomnia conversation\n"
        "- kisi ne isko challenge diya tha kya\n"
        "- discord police incoming\n"
        "- lowkey cinematic tho\n"
        "- ye message tax lagna chahiye\n"
        "- understandable unfortunately\n"
        "- mujhe ye lore nahi chahiye thi\n"
        "- this server needs supervision\n"
        "- emotional support chai required\n"
        "- ab sab awkward hogaye\n"
        "- ye banda side quest pe hai\n"
        "- genuinely what are we doing\n"
        "- ye straight clipboard se aya lagta\n"
        "- im crying internally\n"
        "- too much confidence honestly\n"
        "- ye line history books me jayegi\n"
        "- sleep deprivation detected\n"
        "- no because why is this accurate\n"
        "- ye banda apne own meta me hai\n"
        "- brain buffering rn\n"
        "- mujhe lagta hai sab thak gaye hain\n"
        "- ye message 2am certified hai\n"
        "- banda full delusion pe hai\n"
        "- cpu overheating moment\n"
        "- ye definitely intrusive thought tha\n"
        "- public me ye share karna zaroori tha?\n"
        "- im reporting this spiritually\n"
        "- discord servers were a mistake\n"
        "- nah this needs investigation\n"
        "- ye banda consequences se immune hai\n"
        "- ab mujhe bhi awkward feel horaha\n"
        "- certified keyboard warrior moment\n"
        "- genuinely kis confidence se bola ye\n"
        "- ye line sunke chai gir gayi\n"
        "- human behavior fascinates me\n"
        "- quetta lore expanding again\n"
        "- iska sleep schedule arrest karo\n"
        "- im pretending i didnt read that\n"
        "- banda freestyle pe chal raha hai\n"
        "- this wasnt in the syllabus\n"
        "- emotional iq negative me hai\n"
        "- ye sentence legally questionable hai\n"
        "- braincells resigned after reading this\n"
        "- allat for what 😭\n"
        "- im logging off respectfully\n"
        "- this couldve stayed in drafts\n"
        "- ye banda random event generator hai\n"
        "- chat has officially derailed\n"
        "- no thoughts just confidence\n"
        "- ye definitely vc me louder hota\n"
        "- mujhe chai chahiye after this\n"
        "- every day we stray further\n"
        "- this server running on fumes\n"
        "- actual menace behavior\n"
        "- banda apni own timeline pe hai\n"
        "- ye sentence stumble karke aya lagta\n"
        "- im witnessing history unfortunately\n"
        "- quetta cinematic universe continues\n\n"
        "BAD REPLY EXAMPLES:\n"
        "- i understand what you mean\n"
        "- that's very interesting\n"
        "- how can i help\n"
        "- haha bro thats funny 😂😂\n"
        "- i completely agree with you\n"
        "- thank you for sharing this\n"
        "- that is a fascinating perspective\n\n"
        "Reply with ONLY the message itself.\n\n"
        f"available custom server emojis: {emoji_hint}"
    )

    return await _groq_request(
        api_key=groq_key,
        system=system_prompt,
        user=(
            f"recent chat (for context only):\n{context_block}\n\n"
            f"REACT TO THIS MESSAGE SPECIFICALLY:\n{last_message}\n\n"
            "reply with just the reaction text. nothing else." + avoid_block
        ),
        max_tokens=40,
        temperature=1.15,
        top_p=0.92,
        presence_penalty=0.4,
        frequency_penalty=0.35,
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
