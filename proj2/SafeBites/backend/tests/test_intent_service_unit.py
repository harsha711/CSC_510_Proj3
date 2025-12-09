"""
Unit tests for intent_service.py

Tests intent extraction and query parsing including:
- Menu search intent extraction
- Dish info intent extraction
- User preferences intent extraction
- Irrelevant query handling
- JSON parsing and error handling
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import json
from app.services.intent_service import extract_query_intent
from app.models.intent_model import IntentQuery, IntentExtractionResult


class TestExtractQueryIntent:
    """Test intent extraction from user queries"""

    @patch('app.services.intent_service.llm')
    def test_extract_menu_search_intent(self, mock_llm):
        """Test extracting menu search intent"""
        state = Mock()
        state.query = "Show me chocolate cakes"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": ["List chocolate cakes"],
            "dish_info": [],
            "user_preferences": [],
            "irrelevant": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert "intents" in result
        assert isinstance(result["intents"], IntentExtractionResult)
        assert len(result["intents"].intents) == 1
        assert result["intents"].intents[0].type == "menu_search"
        assert "chocolate cakes" in result["intents"].intents[0].query.lower()

    @patch('app.services.intent_service.llm')
    def test_extract_dish_info_intent(self, mock_llm):
        """Test extracting dish info intent"""
        state = Mock()
        state.query = "How many calories in the pizza?"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": [],
            "dish_info": ["How many calories in the pizza?"],
            "user_preferences": [],
            "irrelevant": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 1
        assert result["intents"].intents[0].type == "dish_info"

    @patch('app.services.intent_service.llm')
    def test_extract_user_preferences_intent(self, mock_llm):
        """Test extracting user preferences intent"""
        state = Mock()
        state.query = "What am I allergic to?"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": [],
            "dish_info": [],
            "user_preferences": ["What am I allergic to?"],
            "irrelevant": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 1
        assert result["intents"].intents[0].type == "user_preferences"

    @patch('app.services.intent_service.llm')
    def test_extract_irrelevant_intent(self, mock_llm):
        """Test extracting irrelevant intent"""
        state = Mock()
        state.query = "Tell me a joke"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": [],
            "dish_info": [],
            "user_preferences": [],
            "irrelevant": ["Tell me a joke"]
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 1
        assert result["intents"].intents[0].type == "irrelevant"

    @patch('app.services.intent_service.llm')
    def test_extract_multiple_intents(self, mock_llm):
        """Test extracting multiple intents from complex query"""
        state = Mock()
        state.query = "Show me chocolate dishes under $20. How many calories do they have?"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": ["List chocolate dishes under $20"],
            "dish_info": ["How many calories do chocolate dishes under $20 have?"],
            "user_preferences": [],
            "irrelevant": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 2
        types = [intent.type for intent in result["intents"].intents]
        assert "menu_search" in types
        assert "dish_info" in types

    @patch('app.services.intent_service.llm')
    def test_json_with_markdown_code_blocks(self, mock_llm):
        """Test handling JSON wrapped in markdown code blocks"""
        state = Mock()
        state.query = "Show me pizza"

        mock_response = Mock()
        mock_response.content = '''```json
        {
            "menu_search": ["List pizza"],
            "dish_info": [],
            "user_preferences": [],
            "irrelevant": []
        }
        ```'''
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 1
        assert result["intents"].intents[0].type == "menu_search"

    @patch('app.services.intent_service.llm')
    def test_empty_llm_response(self, mock_llm):
        """Test handling empty LLM response"""
        state = Mock()
        state.query = "test query"

        mock_response = Mock()
        mock_response.content = ""
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        # Should treat as irrelevant
        assert len(result["intents"].intents) == 1
        assert result["intents"].intents[0].type == "irrelevant"

    @patch('app.services.intent_service.llm')
    def test_json_decode_error(self, mock_llm):
        """Test handling JSON decode errors"""
        state = Mock()
        state.query = "test query"

        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        # Should fall back to irrelevant
        assert len(result["intents"].intents) == 1
        assert result["intents"].intents[0].type == "irrelevant"
        assert result["intents"].intents[0].query == "test query"

    def test_missing_query_in_state(self):
        """Test error when query is missing from state"""
        state = Mock()
        state.query = None

        with pytest.raises(Exception) as exc_info:
            extract_query_intent(state)

        assert "Missing query" in str(exc_info.value)

    @patch('app.services.intent_service.llm')
    def test_llm_exception(self, mock_llm):
        """Test handling LLM exceptions"""
        state = Mock()
        state.query = "test query"

        mock_llm.invoke.side_effect = Exception("LLM error")

        result = extract_query_intent(state)

        # Should fall back to irrelevant
        assert len(result["intents"].intents) == 1
        assert result["intents"].intents[0].type == "irrelevant"

    @patch('app.services.intent_service.llm')
    def test_price_interpretation(self, mock_llm):
        """Test price interpretation (e.g., '$20' → 'under $20')"""
        state = Mock()
        state.query = "Show me dishes 20 dollars"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": ["List all dishes under $20"],
            "dish_info": [],
            "user_preferences": [],
            "irrelevant": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 1
        assert "under" in result["intents"].intents[0].query.lower()

    @patch('app.services.intent_service.llm')
    def test_all_intent_types_mixed(self, mock_llm):
        """Test query with all intent types"""
        state = Mock()
        state.query = "Show me vegan dishes. What's my allergen list? How many calories in pizza? Tell me a joke."

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": ["List vegan dishes"],
            "dish_info": ["How many calories in pizza?"],
            "user_preferences": ["What's my allergen list?"],
            "irrelevant": ["Tell me a joke"]
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 4
        types = [intent.type for intent in result["intents"].intents]
        assert "menu_search" in types
        assert "dish_info" in types
        assert "user_preferences" in types
        assert "irrelevant" in types


class TestIntentQueryModel:
    """Test IntentQuery model behavior"""

    def test_create_intent_query(self):
        """Test creating IntentQuery objects"""
        intent = IntentQuery(type="menu_search", query="Show me pizza")

        assert intent.type == "menu_search"
        assert intent.query == "Show me pizza"

    def test_create_intent_extraction_result(self):
        """Test creating IntentExtractionResult"""
        intents = [
            IntentQuery(type="menu_search", query="pizza"),
            IntentQuery(type="dish_info", query="calories")
        ]

        result = IntentExtractionResult(intents=intents)

        assert len(result.intents) == 2
        assert result.intents[0].type == "menu_search"
        assert result.intents[1].type == "dish_info"


class TestEdgeCases:
    """Test edge cases in intent extraction"""

    @patch('app.services.intent_service.llm')
    def test_whitespace_only_query(self, mock_llm):
        """Test query with only whitespace"""
        state = Mock()
        state.query = "   "

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": [],
            "dish_info": [],
            "user_preferences": [],
            "irrelevant": ["   "]
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 1

    @patch('app.services.intent_service.llm')
    def test_very_long_query(self, mock_llm):
        """Test very long query"""
        state = Mock()
        state.query = "Show me pizza " * 100  # Very long query

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": ["List pizza"],
            "dish_info": [],
            "user_preferences": [],
            "irrelevant": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) >= 1

    @patch('app.services.intent_service.llm')
    def test_unicode_characters(self, mock_llm):
        """Test query with unicode characters"""
        state = Mock()
        state.query = "Show me café dishes with jalapeño"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "menu_search": ["List café dishes with jalapeño"],
            "dish_info": [],
            "user_preferences": [],
            "irrelevant": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(state)

        assert len(result["intents"].intents) == 1
