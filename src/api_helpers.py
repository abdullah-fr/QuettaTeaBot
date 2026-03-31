import aiohttp
import json
import random
import html
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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
    """Generate conversation summary using Google Gemini (free)"""

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("⚠️ GEMINI_API_KEY not set. Get free key from https://aistudio.google.com/app/apikey")
        return None

    return await try_gemini_summary(messages_text, gemini_key)


async def try_gemini_summary(messages_text, api_key):
    """Try Google Gemini (free tier, 1500 req/day)"""
    try:
        async with aiohttp.ClientSession() as session:
            print(f"✅ Using Gemini: {api_key[:10]}...")

            prompt = f"""You are a Discord conversation summarizer. Your summaries are casual, accurate, and concise. Always mention key usernames. Output only the summary — no preamble, no title, no meta-commentary.

Summarize the following Discord conversation.

Rules:
- 100 to 150 words max
- 2 to 3 short paragraphs
- Mention usernames when describing key moments
- Skip spam, repeated emojis, and filler messages
- Highlight funny moments, debates, or notable interactions
- Capture the overall vibe (e.g. chaotic, chill, sarcastic)
- Use a casual tone with a few relevant emojis
- Start directly with the summary, no heading

Conversation:
{messages_text}"""

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.6,
                    "maxOutputTokens": 350
                }
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

            print(f"📤 Sending request to Gemini...")

            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                print(f"📥 Gemini response: {resp.status}")

                if resp.status == 200:
                    data = await resp.json()
                    summary = data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"✅ Gemini summary generated!")
                    return summary
                else:
                    error_text = await resp.text()
                    print(f"❌ Gemini error {resp.status}: {error_text}")
                    return None

    except Exception as e:
        print(f"❌ Gemini error: {e}")
    return None
