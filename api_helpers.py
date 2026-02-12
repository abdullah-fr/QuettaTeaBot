import aiohttp
import random
import html

# ==================== TRIVIA API ====================
async def fetch_trivia_question():
    """Fetch unlimited trivia from Open Trivia Database"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://opentdb.com/api.php?amount=1&type=multiple') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['response_code'] == 0:
                        q_data = data['results'][0]
                        question = html.unescape(q_data['question'])
                        correct = html.unescape(q_data['correct_answer'])
                        incorrect = [html.unescape(ans) for ans in q_data['incorrect_answers']]
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
            headers = {'X-Api-Key': 'YOUR_API_KEY'}
            async with session.get('https://api.api-ninjas.com/v1/riddles', headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        return {"q": data[0]['question'], "a": data[0]['answer']}
    except Exception as e:
        print(f"Riddle API error: {e}")
    return None

# ==================== JOKE API ====================
async def fetch_joke():
    """Fetch jokes from JokeAPI"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://v2.jokeapi.dev/joke/Any?safe-mode') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['type'] == 'single':
                        return data['joke']
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
            async with session.get('https://api.quotable.io/quotes/random?limit=1') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and len(data) > 0:
                        return f"Reflect on this: \"{data[0]['content']}\" - What are your thoughts?"
    except Exception as e:
        print(f"QOTD API error: {e}")

    # Fallback: Use philosophy questions
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://opentdb.com/api.php?amount=1&category=9') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['response_code'] == 0:
                        q_data = data['results'][0]
                        question = html.unescape(q_data['question'])
                        return f"What do you think: {question}"
    except Exception as e:
        print(f"QOTD Fallback error: {e}")

    return None

# ==================== WOULD YOU RATHER API ====================
async def fetch_wyr():
    """Fetch unlimited Would You Rather questions"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.truthordarebot.xyz/v1/wyr') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'question' in data:
                        return data['question']
    except Exception as e:
        print(f"WYR API error: {e}")

    # Fallback: Generate from two random activities
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.boredapi.com/api/activity') as resp1:
                async with session.get('https://www.boredapi.com/api/activity') as resp2:
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
            async with session.get('https://api.adviceslip.com/advice', headers={'Accept': 'application/json'}) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    import json
                    data = json.loads(text)
                    if 'slip' in data:
                        return f"Let's talk about: {data['slip']['advice']}"
    except Exception as e:
        print(f"Conversation API error: {e}")

    # Fallback: Random interesting fact
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://uselessfacts.jsph.pl/random.json?language=en') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'text' in data:
                        return f"Interesting fact: {data['text']} - What do you think?"
    except Exception as e:
        print(f"Conversation Fallback error: {e}")

    return None

# ==================== COMPLIMENT API ====================
async def fetch_compliment():
    """Fetch unlimited compliments"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://compliments-api.herokuapp.com/compliment') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'compliment' in data:
                        return data['compliment']
    except Exception as e:
        print(f"Compliment API error: {e}")

    # Fallback: Affirmations
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.affirmations.dev/') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'affirmation' in data:
                        return data['affirmation']
    except Exception as e:
        print(f"Compliment Fallback error: {e}")

    return None

# ==================== ROAST API (Friendly & SFW with Safety Filter) ====================
async def fetch_roast():
    """Fetch unlimited friendly roasts with safety filter"""
    # Safety filter for unexpected NSFW content
    nsfw_words = [
        'dick', 'cock', 'penis', 'vagina', 'pussy', 'ass', 'asshole', 'shit', 'fuck',
        'bitch', 'bastard', 'damn', 'hell', 'sex', 'sexual', 'porn', 'nude', 'naked',
        'whore', 'slut', 'cunt', 'piss', 'crap', 'tit', 'boob', 'breast', 'butt',
        'stupid', 'idiot', 'moron', 'dumb', 'retard', 'loser', 'ugly', 'fat',
        'kill', 'die', 'death', 'suicide', 'rape', 'molest'
    ]

    try:
        async with aiohttp.ClientSession() as session:
            # Try pirate insults API - known for funny, friendly roasts
            async with session.get('https://pirate.monkeyness.com/api/insult') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'insult' in data:
                        roast = data['insult']
                        # Safety check
                        roast_lower = roast.lower()
                        is_clean = not any(word in roast_lower for word in nsfw_words)
                        if is_clean and len(roast) > 10:
                            return roast
    except Exception as e:
        print(f"Pirate Roast API error: {e}")

    # Fallback: Try compliment API but make it a playful roast
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://complimentr.com/api') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'compliment' in data:
                        # Turn compliment into playful roast
                        compliment = data['compliment']
                        return f"You're so {compliment.lower()}, it's almost suspicious! 🤔"
    except Exception as e:
        print(f"Compliment fallback error: {e}")

    return None
