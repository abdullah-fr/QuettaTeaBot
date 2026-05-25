from src import api_helpers


async def test_fetch_trivia_question_returns_parsed_question(monkeypatch):
    async def fake_fetch_json(url, headers=None, params=None):
        return {
            "response_code": 0,
            "results": [
                {
                    "question": "What is 2+2?",
                    "correct_answer": "4",
                    "incorrect_answers": ["3", "22", "5"],
                }
            ],
        }

    monkeypatch.setattr(api_helpers, "_fetch_json", fake_fetch_json)

    result = await api_helpers.fetch_trivia_question()

    assert isinstance(result, dict)
    assert result["a"] == "4"
    assert result["q"] == "What is 2+2?"
    assert set(result["options"]) == {"3", "4", "5", "22"}


async def test_fetch_joke_returns_single_and_twopart(monkeypatch):
    async def fake_fetch_json_single(url, headers=None, params=None):
        return {"type": "single", "joke": "Hello world"}

    monkeypatch.setattr(api_helpers, "_fetch_json", fake_fetch_json_single)
    assert await api_helpers.fetch_joke() == "Hello world"

    async def fake_fetch_json_two_part(url, headers=None, params=None):
        return {"type": "twopart", "setup": "Why?", "delivery": "Because."}

    monkeypatch.setattr(api_helpers, "_fetch_json", fake_fetch_json_two_part)
    assert await api_helpers.fetch_joke() == "Why?\nBecause."


async def test_fetch_conversation_starter_falls_back_to_fact(monkeypatch):
    async def fake_fetch_text(url, headers=None, timeout=15):
        return None

    async def fake_fetch_json(url, headers=None, params=None):
        if "uselessfacts.jsph.pl" in url:
            return {"text": "This is a fact."}
        return None

    monkeypatch.setattr(api_helpers, "_fetch_text", fake_fetch_text)
    monkeypatch.setattr(api_helpers, "_fetch_json", fake_fetch_json)

    result = await api_helpers.fetch_conversation_starter()
    assert result == "Interesting fact: This is a fact. - What do you think?"


async def test_fetch_compliment_falls_back_to_affirmation(monkeypatch):
    async def fake_fetch_json(url, headers=None, params=None):
        if "compliments-api.herokuapp.com" in url:
            return None
        return {"affirmation": "You are capable."}

    monkeypatch.setattr(api_helpers, "_fetch_json", fake_fetch_json)

    assert await api_helpers.fetch_compliment() == "You are capable."


async def test_fetch_qotd_falls_back_to_opentdb(monkeypatch):
    async def fake_fetch_json(url, headers=None, params=None):
        if "quotes/random" in url:
            return None
        return {
            "response_code": 0,
            "results": [{"question": "What makes you smile?"}],
        }

    monkeypatch.setattr(api_helpers, "_fetch_json", fake_fetch_json)

    result = await api_helpers.fetch_qotd()
    assert result == "What do you think: What makes you smile?"
