import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.flow.state import ChatState
from app.services.state_service import get_or_create_session, get_all_chat_states, rebuild_context, save_chat_state

@pytest.fixture
def mock_db():
    with patch("app.services.state_service.sessions") as mock_sessions, \
        patch("app.services.state_service.chat_states") as mock_chat_states:
        yield mock_sessions, mock_chat_states

def test_get_or_create_session_existing_session(mock_db):
    mock_sessions, _ = mock_db
    mock_sessions.find_one.return_value = {"session_id":"sess_123"}

    session_id = get_or_create_session("user1","rest1")
    mock_sessions.find_one.assert_called_once_with(
        {"user_id":"user1","restaurant_id":"rest1","active":True}
    )

    assert session_id == "sess_123"

def test_get_or_create_session_new_session(mock_db):
    mock_sessions, _ = mock_db
    mock_sessions.find_one.return_value = None

    session_id = get_or_create_session("user2","rest2")
    mock_sessions.insert_one.assert_called_once()
    assert session_id.startswith("sess_")

def test_save_chat_state(mock_db):
    _, mock_chat_states = mock_db
    mock_chat_states.insert_one.return_value = None

    state = ChatState(
        user_id="u1",
        session_id="sess_1",
        restaurant_id="r1",
        query="What's on the menu?"
    )

    save_chat_state(state)
    mock_chat_states.insert_one.assert_called_once()
    args, _ = mock_chat_states.insert_one.call_args
    assert isinstance(args[0],dict)
    assert args[0]["query"] == "What's on the menu?"

def test_get_all_chat_states(mock_db):
    _, mock_chat_states = mock_db
    mock_chat_states.find.return_value.sort.return_value = [
        {"session_id": "sess_1", "timestamp": "2025-11-06T00:00:00Z", "query": "hi"},
        {"session_id": "sess_1", "timestamp": "2025-11-06T01:00:00Z", "query": "hello"},
    ]

    results = get_all_chat_states("sess_1")
    mock_chat_states.find.assert_called_once_with({"session_id":"sess_1"})
    assert len(results) == 2
    assert results[0]["query"] == "hi"

def test_rebuild_context_returns(monkeypatch):
    sample_docs = [
        {"query": "hi", "intents": [{"intent": "greet"}], "menu_results": {"m": 1}, "info_results": {"i": 1}},
        {"query": "what's for dinner", "intents": [{"intent": "menu"}], "menu_results": {"m": 2}, "info_results": {"i": 2}},
        {"query": "order pizza", "intents": [{"intent": "order"}], "menu_results": {"m": 3}, "info_results": {"i": 3}},
    ]
    monkeypatch.setattr("app.services.state_service.get_all_chat_states",lambda _:sample_docs)
    context = rebuild_context("sess_1",last_n=2)
    assert len(context) == 2
    assert context[0]["query"] == "what's for dinner"
    assert context[1]["query"] == "order pizza"
    assert "intents" in context[0]
    assert "menu_results" in context[1]