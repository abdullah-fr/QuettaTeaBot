from pydantic import SecretStr

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


async def test_fetch_ai_summary_returns_none_when_no_groq_key(monkeypatch):
    monkeypatch.setattr(api_helpers.settings, "groq_api_key", None)
    assert await api_helpers.fetch_ai_summary("hello world") is None


async def test_fetch_ai_chat_reply_returns_none_when_no_groq_key(monkeypatch):
    monkeypatch.setattr(api_helpers.settings, "groq_api_key", None)
    assert await api_helpers.fetch_ai_chat_reply(["hi"], ["smile"], "bro what") is None


async def test_fetch_ai_chat_reply_returns_groq_response(monkeypatch):
    monkeypatch.setattr(
        api_helpers.settings, "groq_api_key", SecretStr("fake-groq-key")
    )

    captured = {}

    async def fake_groq_request(
        api_key, system, user, max_tokens=200, temperature=0.7, **kwargs
    ):
        captured["api_key"] = api_key
        captured["system"] = system
        captured["user"] = user
        return "bro got cooked 💀"

    monkeypatch.setattr(api_helpers, "_groq_request", fake_groq_request)

    reply = await api_helpers.fetch_ai_chat_reply(
        ["how's everyone", "kuch nahi yaar"],
        ["smile", "cry"],
        "skill issue",
    )
    assert reply == "bro got cooked 💀"
    assert captured["api_key"] == "fake-groq-key"
    assert "smile, cry" in captured["system"]
    assert "kuch nahi yaar" in captured["user"]
    # The trigger message must be highlighted to the model.
    assert "skill issue" in captured["user"]
    assert "REACT TO THIS MESSAGE" in captured["user"]


async def test_fetch_ai_chat_reply_sends_anti_repetition_sampling(monkeypatch):
    monkeypatch.setattr(
        api_helpers.settings, "groq_api_key", SecretStr("fake-groq-key")
    )

    captured = {}

    async def fake_groq_request(
        api_key, system, user, max_tokens=200, temperature=0.7, **kwargs
    ):
        captured["temperature"] = temperature
        captured["max_tokens"] = max_tokens
        captured["top_p"] = kwargs.get("top_p")
        captured["presence_penalty"] = kwargs.get("presence_penalty")
        captured["frequency_penalty"] = kwargs.get("frequency_penalty")
        return "fine"

    monkeypatch.setattr(api_helpers, "_groq_request", fake_groq_request)

    await api_helpers.fetch_ai_chat_reply([], [], "test")

    assert captured["temperature"] == 1.15
    assert captured["max_tokens"] == 40
    assert captured["top_p"] == 0.92
    assert captured["presence_penalty"] == 0.4
    assert captured["frequency_penalty"] == 0.35


async def test_fetch_ai_chat_reply_passes_avoid_phrases(monkeypatch):
    monkeypatch.setattr(
        api_helpers.settings, "groq_api_key", SecretStr("fake-groq-key")
    )

    captured = {}

    async def fake_groq_request(
        api_key, system, user, max_tokens=200, temperature=0.7, **kwargs
    ):
        captured["user"] = user
        return "fresh reply"

    monkeypatch.setattr(api_helpers, "_groq_request", fake_groq_request)

    await api_helpers.fetch_ai_chat_reply(
        ["context"],
        [],
        "bro that's wild",
        avoid_phrases=["nahh", "average faisalabad behaviour", "bro 💀"],
    )

    assert "DO NOT repeat" in captured["user"]
    assert "average faisalabad behaviour" in captured["user"]


def test_trim_history_to_budget_drops_oldest_when_overflowing():
    long_line = "x" * 600
    kept = api_helpers._trim_history_to_budget(
        [long_line, long_line, long_line, long_line], budget=1500
    )
    # 600+1 * 4 = 2404 -> only the last 2 fit (1202 chars)
    assert len(kept) == 2


def test_trim_history_to_budget_keeps_at_least_one_message():
    huge = "x" * 5000
    kept = api_helpers._trim_history_to_budget([huge], budget=100)
    assert kept == [huge]


def test_trim_history_to_budget_handles_empty():
    assert api_helpers._trim_history_to_budget([], budget=100) == []


async def test_fetch_ai_summary_passes_messages_to_groq(monkeypatch):
    monkeypatch.setattr(
        api_helpers.settings, "groq_api_key", SecretStr("fake-groq-key")
    )

    captured = {}

    async def fake_groq_request(
        api_key, system, user, max_tokens=200, temperature=0.7, **kwargs
    ):
        captured["user"] = user
        captured["max_tokens"] = max_tokens
        return "Summary text"

    monkeypatch.setattr(api_helpers, "_groq_request", fake_groq_request)

    result = await api_helpers.fetch_ai_summary("alice: hi\nbob: hello")
    assert result == "Summary text"
    assert "alice: hi" in captured["user"]
    assert captured["max_tokens"] == 350


def test_http_status_error_stores_status_and_body():
    err = api_helpers.HttpStatusError(503, "service unavailable")
    assert err.status == 503
    assert err.body == "service unavailable"
    assert "503" in str(err)
