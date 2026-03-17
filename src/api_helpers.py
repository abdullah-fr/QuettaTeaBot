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
    """Generate conversation summary using Groq (free)"""

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("⚠️ GROQ_API_KEY not set. Get free key from https://console.groq.com/keys")
        return None

    return await try_groq_summary(messages_text, groq_key)



async def try_groq_summary(messages_text, api_key):
    """Try Groq Llama (free, fast, good quality)"""
    try:
        async with aiohttp.ClientSession() as session:
            print(f"✅ Using Groq Llama: {api_key[:10]}...")

            prompt = f"""You are an AI assistant that summarizes Discord conversations.
Your task is to analyze the full chat and produce a concise summary explaining what happened.
First understand the discussion, then write the summary.

Instructions
• Identify the main participants in the conversation.
• Determine the main topics or jokes discussed.
• Mention who said the key messages when relevant.
• Ignore spam, repeated emojis, or filler messages unless they are part of a joke.
• Focus on important interactions, funny moments, or disagreements.
• Capture the overall tone of the conversation such as chaotic, friendly, sarcastic, or serious.

Output Requirements
• Maximum 100 to 150 words
• 2 to 3 short paragraphs
• Mention usernames when describing key messages
• Write in a casual, natural tone
• Use a few emojis but not excessively

Output Format
Summary of the Conversation 💬

Paragraph 1: Explain the main discussion and who started it.
Paragraph 2: Describe responses, jokes, or reactions from other users.
Paragraph 3: Briefly mention the overall vibe of the chat.

Conversation:
{messages_text}

Write the summary:"""

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300
            }

            print(f"📤 Sending request to Groq...")

            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                print(f"📥 Groq response: {resp.status}")

                if resp.status == 200:
                    data = await resp.json()
                    summary = data["choices"][0]["message"]["content"]
                    print(f"✅ Groq summary generated!")
                    return summary
                else:
                    error_text = await resp.text()
                    print(f"❌ Groq error {resp.status}: {error_text}")
                    return None

    except Exception as e:
        print(f"❌ Groq error: {e}")
    return None
