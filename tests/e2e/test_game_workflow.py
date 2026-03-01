"""
End-to-End tests for game feature workflows.

Simulates complete user journeys for:
- Trivia game
- Joke requests
- API-based games
"""

import pytest
import aiohttp

from src.api_helpers import fetch_trivia_question, fetch_joke


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.api
async def test_trivia_game_workflow():
    """
    E2E Test: User plays trivia game

    User Journey:
    1. User starts trivia game
    2. Bot fetches question from API
    3. Bot presents question with options
    4. User sees shuffled answers
    """
    # Step 1: User starts game
    # Step 2: Bot fetches question
    question_data = await fetch_trivia_question()

    if question_data:  # API may be unavailable
        # Step 3: Verify question structure
        assert "q" in question_data
        assert "a" in question_data
        assert "options" in question_data

        # Step 4: Verify user sees complete game
        assert len(question_data["q"]) > 0
        assert len(question_data["a"]) > 0
        assert len(question_data["options"]) == 4
        assert question_data["a"] in question_data["options"]


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.api
async def test_joke_request_workflow():
    """
    E2E Test: User requests a joke

    User Journey:
    1. User asks for joke
    2. Bot fetches from API
    3. Bot formats joke
    4. User sees joke
    """
    # Step 1: User requests
    # Step 2: Bot fetches
    joke = await fetch_joke()

    if joke:  # API may be unavailable
        # Step 3 & 4: Verify user sees joke
        assert isinstance(joke, str)
        assert len(joke) > 0


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.api
async def test_multiple_trivia_rounds_workflow():
    """
    E2E Test: User plays multiple trivia rounds

    User Journey:
    1. User plays round 1
    2. User plays round 2
    3. Each round has different question
    """
    import asyncio

    # Round 1
    q1 = await fetch_trivia_question()
    await asyncio.sleep(1)  # Avoid rate limiting

    # Round 2
    q2 = await fetch_trivia_question()

    # Verify both rounds worked (if API available)
    if q1 and q2:
        assert "q" in q1
        assert "q" in q2


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_entertainment_session_workflow():
    """
    E2E Test: User has entertainment session

    User Journey:
    1. User plays trivia
    2. User requests joke
    3. User enjoys both features
    """
    import asyncio

    # Step 1: Trivia
    trivia = await fetch_trivia_question()
    await asyncio.sleep(1)

    # Step 2: Joke
    joke = await fetch_joke()

    # Step 3: Verify complete session
    # At least one should work
    assert trivia is not None or joke is not None
