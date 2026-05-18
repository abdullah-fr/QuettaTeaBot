import aiohttp
import json
import random
import html
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


# ==================== TRIVIA API ====================
async def fetch_trivia_question():
    """Fetch unlimited trivia from Open Trivia Database"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://opentdb.com/api.php?amount=1&type=multiple"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["response_code"] == 0:
                        q_data = data["results"][0]
                        question = html.unescape(q_data["question"])
                        correct = html.unescape(q_data["correct_answer"])
                        incorrect = [
                            html.unescape(ans) for ans in q_data["incorrect_answers"]
                        ]
                        options = incorrect + [correct]
                        random.shuffle(options)
                        return {"q": question, "a": correct, "options": options}
    except Exception as e:
        print(f"Trivia API error: {e}")
    return None


# ==================== RIDDLE API ====================
async def fetch_riddle():
    """Fetch riddles from API Ninjas"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"X-Api-Key": os.getenv("API_NINJAS_KEY", "")}
            async with session.get(
                "https://api.api-ninjas.com/v1/riddles", headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        return {"q": data[0]["question"], "a": data[0]["answer"]}
    except Exception as e:
        print(f"Riddle API error: {e}")
    return None


# ==================== JOKE API ====================
async def fetch_joke():
    """Fetch jokes from JokeAPI"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://v2.jokeapi.dev/joke/Any?safe-mode") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["type"] == "single":
                        return data["joke"]
                    else:
                        return f"{data['setup']}\n{data['delivery']}"
    except Exception as e:
        print(f"Joke API error: {e}")
    return None


# ==================== QOTD API (Unlimited) ====================
async def fetch_qotd():
    """Fetch unlimited conversation questions"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.quotable.io/quotes/random?limit=1"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and len(data) > 0:
                        return f"Reflect on this: \"{data[0]['content']}\" - What are your thoughts?"
    except Exception as e:
        print(f"QOTD API error: {e}")

    # Fallback: Use philosophy questions
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://opentdb.com/api.php?amount=1&category=9"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["response_code"] == 0:
                        q_data = data["results"][0]
                        question = html.unescape(q_data["question"])
                        return f"What do you think: {question}"
    except Exception as e:
        print(f"QOTD Fallback error: {e}")

    return None


# ==================== WOULD YOU RATHER API ====================
async def fetch_wyr():
    """Fetch unlimited Would You Rather questions"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/wyr") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "question" in data:
                        return data["question"]
    except Exception as e:
        print(f"WYR API error: {e}")

    # Fallback: Generate from two random activities
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.boredapi.com/api/activity") as resp1:
                async with session.get(
                    "https://www.boredapi.com/api/activity"
                ) as resp2:
                    if resp1.status == 200 and resp2.status == 200:
                        data1 = await resp1.json()
                        data2 = await resp2.json()
                        return f"Would you rather {data1['activity'].lower()} or {data2['activity'].lower()}?"
    except Exception as e:
        print(f"WYR Fallback error: {e}")

    return None


# ==================== CONVERSATION STARTER API ====================
async def fetch_conversation_starter():
    """Fetch unlimited conversation starters"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.adviceslip.com/advice",
                headers={"Accept": "application/json"},
            ) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    data = json.loads(text)
                    if "slip" in data:
                        return f"Let's talk about: {data['slip']['advice']}"
    except Exception as e:
        print(f"Conversation API error: {e}")

    # Fallback: Random interesting fact
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://uselessfacts.jsph.pl/random.json?language=en"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "text" in data:
                        return f"Interesting fact: {data['text']} - What do you think?"
    except Exception as e:
        print(f"Conversation Fallback error: {e}")

    return None


# ==================== COMPLIMENT API ====================
async def fetch_compliment():
    """Fetch unlimited compliments"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://compliments-api.herokuapp.com/compliment"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "compliment" in data:
                        return data["compliment"]
    except Exception as e:
        print(f"Compliment API error: {e}")

    # Fallback: Affirmations
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.affirmations.dev/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "affirmation" in data:
                        return data["affirmation"]
    except Exception as e:
        print(f"Compliment Fallback error: {e}")

    return None


# ==================== ROAST (Clean & Friendly Only) ====================
async def fetch_roast():
    """Always use our clean, friendly roast list - NO API"""
    # All roast APIs contain inappropriate content
    # We ONLY use our curated clean list from question_bank.py
    return None


# ==================== AI SUMMARIZATION ====================
async def fetch_ai_summary(messages_text):
    """Generate conversation summary using Groq (free)"""
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("⚠️ GROQ_API_KEY not set. Get free key from https://console.groq.com")
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


async def fetch_ai_chat_reply(recent_messages: list[str], server_emojis: list[str]) -> str | None:
    """Generate a witty, context-aware chat reply using Groq."""
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return None

    emoji_hint = ", ".join(server_emojis[:20]) if server_emojis else "none available"
    conversation = "\n".join(recent_messages[-10:])

    return await _groq_request(
        api_key=groq_key,
        system=(
            "You are QuettaTeaBot, a funny, witty, slightly chaotic Discord bot member "
            "in a Pakistani/South Asian community server called Quetta Tea Corner. "
            "You talk like a real server member — casual Urdu/English mix is fine. "
            "You are NOT a helpful assistant. You are a funny, sarcastic, hype-giving "
            "community member who occasionally roasts, hypes, acts confused, or drops "
            "one-liners. Never sound like an AI. Never be generic. Never be cringe. "
            "Keep replies SHORT — 1 to 2 sentences max. "
            f"Available custom server emojis you can use naturally: {emoji_hint}. "
            "Use them like a real member would — sparingly and only when they fit the vibe."
        ),
        user=(
            f"Recent chat in the server:\n{conversation}\n\n"
            "Drop a short, natural reply that fits the vibe. "
            "Don't address everyone. Don't start with 'lol' every time. "
            "Be unpredictable. Sometimes hype, sometimes roast, sometimes confused, "
            "sometimes a callback. Max 2 sentences."
        ),
        max_tokens=80,
        temperature=1.1,
    )


async def _groq_request(
    api_key: str,
    system: str,
    user: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
) -> str | None:
    """Shared Groq API call using aiohttp."""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "llama3-8b-8192",
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
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    err = await resp.text()
                    print(f"❌ Groq error {resp.status}: {err}")
    except Exception as e:
        print(f"❌ Groq request error: {e}")
    return None
