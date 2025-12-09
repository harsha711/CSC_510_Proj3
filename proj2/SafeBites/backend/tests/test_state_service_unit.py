"""
Unit tests for state_service.py

Tests session management and chat state persistence including:
- Session creation and retrieval
- Session clearing
- Chat state saving and retrieval
- Context rebuilding from chat history
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
from bson import ObjectId
from app.services.state_service import (
    get_or_create_session,
    clear_and_create_new_session,
    save_chat_state,
    get_all_chat_states,
    rebuild_context
)


class TestGetOrCreateSession:
    """Test session retrieval and creation"""

    @patch('app.services.state_service.sessions')
    def test_returns_existing_active_session(self, mock_sessions):
        """Test that existing active session is returned"""
        mock_sessions.find_one.return_value = {
            "session_id": "sess_abc123",
            "user_id": "user1",
            "restaurant_id": "rest1",
            "active": True
        }

        result = get_or_create_session("user1", "rest1")

        assert result == "sess_abc123"
        mock_sessions.find_one.assert_called_once_with({
            "user_id": "user1",
            "restaurant_id": "rest1",
            "active": True
        })

    @patch('app.services.state_service.sessions')
    @patch('app.services.state_service.uuid')
    def test_creates_new_session_when_none_exists(self, mock_uuid, mock_sessions):
        """Test that new session is created when no active session exists"""
        mock_sessions.find_one.return_value = None
        mock_uuid.uuid4.return_value = Mock(hex="abcd1234567890")

        result = get_or_create_session("user1", "rest1")

        assert result.startswith("sess_")
        assert len(result) == 15  # "sess_" + 10 chars
        mock_sessions.insert_one.assert_called_once()
        insert_data = mock_sessions.insert_one.call_args[0][0]
        assert insert_data["user_id"] == "user1"
        assert insert_data["restaurant_id"] == "rest1"
        assert insert_data["active"] is True

    @patch('app.services.state_service.sessions')
    def test_handles_multiple_users(self, mock_sessions):
        """Test that different users get different sessions"""
        mock_sessions.find_one.side_effect = [
            {"session_id": "sess_user1", "user_id": "user1", "restaurant_id": "rest1", "active": True},
            {"session_id": "sess_user2", "user_id": "user2", "restaurant_id": "rest1", "active": True}
        ]

        result1 = get_or_create_session("user1", "rest1")
        result2 = get_or_create_session("user2", "rest1")

        assert result1 == "sess_user1"
        assert result2 == "sess_user2"


class TestClearAndCreateNewSession:
    """Test session clearing"""

    @patch('app.services.state_service.sessions')
    @patch('app.services.state_service.uuid')
    def test_marks_existing_session_inactive(self, mock_uuid, mock_sessions):
        """Test that existing sessions are marked inactive"""
        mock_uuid.uuid4.return_value = Mock(hex="newid567890abc")

        result = clear_and_create_new_session("user1", "rest1")

        # Check that update_many was called to mark sessions inactive
        mock_sessions.update_many.assert_called_once()
        update_filter = mock_sessions.update_many.call_args[0][0]
        update_data = mock_sessions.update_many.call_args[0][1]
        assert update_filter == {"user_id": "user1", "restaurant_id": "rest1", "active": True}
        assert update_data["$set"]["active"] is False
        assert "ended_at" in update_data["$set"]

    @patch('app.services.state_service.sessions')
    @patch('app.services.state_service.uuid')
    def test_creates_new_session_after_clearing(self, mock_uuid, mock_sessions):
        """Test that new session is created after clearing"""
        mock_uuid.uuid4.return_value = Mock(hex="newid567890abc")

        result = clear_and_create_new_session("user1", "rest1")

        assert result.startswith("sess_")
        mock_sessions.insert_one.assert_called_once()
        insert_data = mock_sessions.insert_one.call_args[0][0]
        assert insert_data["session_id"] == result
        assert insert_data["active"] is True

    @patch('app.services.state_service.sessions')
    @patch('app.services.state_service.uuid')
    def test_returns_new_session_id(self, mock_uuid, mock_sessions):
        """Test that new session ID is returned"""
        mock_uuid.uuid4.return_value = Mock(hex="xyz9876543210")

        result = clear_and_create_new_session("user1", "rest1")

        assert result == "sess_xyz9876543"


class TestSaveChatState:
    """Test chat state persistence"""

    @patch('app.services.state_service.chat_states')
    @patch('app.services.state_service.jsonable_encoder')
    def test_saves_chat_state_to_database(self, mock_encoder, mock_chat_states):
        """Test that chat state is saved to database"""
        mock_state = Mock()
        mock_encoder.return_value = {"query": "test", "session_id": "sess_123"}

        save_chat_state(mock_state)

        mock_encoder.assert_called_once_with(mock_state)
        mock_chat_states.insert_one.assert_called_once_with({"query": "test", "session_id": "sess_123"})

    @patch('app.services.state_service.chat_states')
    @patch('app.services.state_service.jsonable_encoder')
    def test_encodes_pydantic_models(self, mock_encoder, mock_chat_states):
        """Test that Pydantic models are properly encoded"""
        mock_state = Mock()
        mock_encoder.return_value = {
            "query": "pizza",
            "user_id": "user1",
            "intents": [{"type": "menu_search", "query": "pizza"}]
        }

        save_chat_state(mock_state)

        assert mock_encoder.called
        saved_data = mock_chat_states.insert_one.call_args[0][0]
        assert "query" in saved_data
        assert "intents" in saved_data


class TestGetAllChatStates:
    """Test chat state retrieval"""

    @patch('app.services.state_service.chat_states')
    def test_retrieves_chat_states_for_session(self, mock_chat_states):
        """Test that chat states are retrieved for a session"""
        mock_cursor = Mock()
        mock_cursor.sort.return_value = [
            {"query": "pizza", "timestamp": 1},
            {"query": "pasta", "timestamp": 2}
        ]
        mock_chat_states.find.return_value = mock_cursor

        result = get_all_chat_states("sess_123")

        mock_chat_states.find.assert_called_once_with({"session_id": "sess_123"})
        mock_cursor.sort.assert_called_once_with("timestamp", 1)
        assert len(result) == 2
        assert result[0]["query"] == "pizza"

    @patch('app.services.state_service.chat_states')
    def test_returns_empty_list_for_new_session(self, mock_chat_states):
        """Test that empty list is returned for new session"""
        mock_cursor = Mock()
        mock_cursor.sort.return_value = []
        mock_chat_states.find.return_value = mock_cursor

        result = get_all_chat_states("sess_new")

        assert result == []

    @patch('app.services.state_service.chat_states')
    def test_sorts_by_timestamp(self, mock_chat_states):
        """Test that results are sorted by timestamp"""
        mock_cursor = Mock()
        mock_cursor.sort.return_value = [
            {"query": "first", "timestamp": 1},
            {"query": "second", "timestamp": 2},
            {"query": "third", "timestamp": 3}
        ]
        mock_chat_states.find.return_value = mock_cursor

        result = get_all_chat_states("sess_123")

        # Verify sort was called with ascending order (1)
        mock_cursor.sort.assert_called_once_with("timestamp", 1)
        assert result[0]["query"] == "first"
        assert result[2]["query"] == "third"


class TestRebuildContext:
    """Test context rebuilding"""

    @patch('app.services.state_service.get_all_chat_states')
    @patch('app.services.state_service.db')
    def test_rebuilds_context_without_user(self, mock_db, mock_get_states):
        """Test context rebuilding without user profile"""
        mock_get_states.return_value = [
            {"query": "pizza", "intents": [], "menu_results": {}, "info_results": {}},
            {"query": "pasta", "intents": [], "menu_results": {}, "info_results": {}}
        ]

        result = rebuild_context("sess_123", user_id=None, last_n=5)

        assert len(result) == 2
        assert result[0]["query"] == "pizza"
        assert result[1]["query"] == "pasta"

    @patch('app.services.state_service.get_all_chat_states')
    @patch('app.services.state_service.db')
    def test_rebuilds_context_with_user_allergens(self, mock_db, mock_get_states):
        """Test context rebuilding with user allergen preferences"""
        mock_users = Mock()
        mock_db.__getitem__.return_value = mock_users
        mock_users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "allergen_preferences": ["peanuts", "dairy"],
            "health_goals": [],
            "cuisine_preferences": [],
            "taste_preferences": [],
            "dietary_pattern": "omnivore"
        }
        mock_get_states.return_value = [
            {"query": "pizza", "intents": [], "menu_results": {}, "info_results": {}}
        ]

        result = rebuild_context("sess_123", user_id="507f1f77bcf86cd799439011", last_n=5)

        # First item should be user allergens
        assert len(result) >= 2
        assert "user_allergens" in result[0]
        assert "peanuts" in result[0]["user_allergens"]
        assert "dairy" in result[0]["user_allergens"]

    @patch('app.services.state_service.get_all_chat_states')
    @patch('app.services.state_service.db')
    def test_limits_to_last_n_states(self, mock_db, mock_get_states):
        """Test that only last N chat states are included"""
        mock_get_states.return_value = [
            {"query": f"query{i}", "intents": [], "menu_results": {}, "info_results": {}}
            for i in range(10)
        ]

        result = rebuild_context("sess_123", user_id=None, last_n=3)

        # Should only have last 3 queries
        assert len(result) == 3
        assert result[0]["query"] == "query7"
        assert result[1]["query"] == "query8"
        assert result[2]["query"] == "query9"

    @patch('app.services.state_service.get_all_chat_states')
    @patch('app.services.state_service.db')
    def test_includes_user_profile_for_compatibility(self, mock_db, mock_get_states):
        """Test that full user profile is included for compatibility scoring"""
        mock_users = Mock()
        mock_db.__getitem__.return_value = mock_users
        mock_users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "allergen_preferences": ["peanuts"],
            "health_goals": ["high_protein", "low_carb"],
            "cuisine_preferences": ["Italian"],
            "taste_preferences": ["spicy"],
            "dietary_pattern": "vegetarian"
        }
        mock_get_states.return_value = [
            {"query": "pizza", "intents": [], "menu_results": {}, "info_results": {}}
        ]

        result = rebuild_context("sess_123", user_id="507f1f77bcf86cd799439011", last_n=5)

        # Should have allergen context + user profile + chat state
        assert len(result) >= 3
        # Check for user profile
        has_profile = any("user_profile" in item for item in result)
        assert has_profile

        # Find the profile and verify contents
        profile_item = next(item for item in result if "user_profile" in item)
        assert profile_item["user_profile"]["dietary_pattern"] == "vegetarian"
        assert "high_protein" in profile_item["user_profile"]["health_goals"]

    @patch('app.services.state_service.get_all_chat_states')
    @patch('app.services.state_service.db')
    def test_handles_missing_user_profile(self, mock_db, mock_get_states):
        """Test that missing user profile is handled gracefully"""
        mock_users = Mock()
        mock_db.__getitem__.return_value = mock_users
        mock_users.find_one.return_value = None
        mock_get_states.return_value = [
            {"query": "pizza", "intents": [], "menu_results": {}, "info_results": {}}
        ]

        result = rebuild_context("sess_123", user_id="507f1f77bcf86cd799439011", last_n=5)

        # Should still work, just without user profile
        assert len(result) >= 1
        assert result[-1]["query"] == "pizza"

    @patch('app.services.state_service.get_all_chat_states')
    @patch('app.services.state_service.db')
    def test_handles_database_error(self, mock_db, mock_get_states):
        """Test that database errors are handled gracefully"""
        mock_users = Mock()
        mock_db.__getitem__.return_value = mock_users
        mock_users.find_one.side_effect = Exception("Database error")
        mock_get_states.return_value = [
            {"query": "pizza", "intents": [], "menu_results": {}, "info_results": {}}
        ]

        # Should not raise exception
        result = rebuild_context("sess_123", user_id="507f1f77bcf86cd799439011", last_n=5)

        # Should still have chat states
        assert len(result) >= 1
        assert result[-1]["query"] == "pizza"


class TestSessionIdFormat:
    """Test session ID formatting"""

    @patch('app.services.state_service.sessions')
    @patch('app.services.state_service.uuid')
    def test_session_id_has_correct_prefix(self, mock_uuid, mock_sessions):
        """Test that session IDs have 'sess_' prefix"""
        mock_sessions.find_one.return_value = None
        mock_uuid.uuid4.return_value = Mock(hex="a" * 32)

        result = get_or_create_session("user1", "rest1")

        assert result.startswith("sess_")

    @patch('app.services.state_service.sessions')
    @patch('app.services.state_service.uuid')
    def test_session_id_length(self, mock_uuid, mock_sessions):
        """Test that session IDs are correct length"""
        mock_sessions.find_one.return_value = None
        mock_uuid.uuid4.return_value = Mock(hex="b" * 32)

        result = get_or_create_session("user1", "rest1")

        # "sess_" (5 chars) + 10 chars from UUID = 15 total
        assert len(result) == 15
