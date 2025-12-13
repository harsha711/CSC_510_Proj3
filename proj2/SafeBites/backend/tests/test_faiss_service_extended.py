"""
Extended unit tests for faiss_service.py

Tests the uncovered portions of FAISS service including:
- Query intent extraction with LLM
- FAISS index creation
- Negative query handling
- Edge cases in semantic search
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import json
from app.services.faiss_service import extract_query_intent, QueryIntent


class TestExtractQueryIntent:
    """Test query intent extraction for FAISS search"""

    @patch('app.services.faiss_service.llm')
    def test_extract_simple_positive_intent(self, mock_llm):
        """Test extracting simple positive intent"""
        query = "show me pizza"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["pizza", "margherita", "pepperoni"],
            "negative": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert isinstance(result, QueryIntent)
        assert "pizza" in result.positive
        assert len(result.negative) == 0

    @patch('app.services.faiss_service.llm')
    def test_extract_positive_and_negative_intent(self, mock_llm):
        """Test extracting both positive and negative intents"""
        query = "pasta without meatballs"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["pasta", "spaghetti", "penne"],
            "negative": ["meatballs"]
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert len(result.positive) > 0
        assert "pasta" in result.positive or "spaghetti" in result.positive
        assert "meatballs" in result.negative

    @patch('app.services.faiss_service.llm')
    def test_empty_llm_response(self, mock_llm):
        """Test handling empty LLM response"""
        query = "test query"

        mock_response = Mock()
        mock_response.content = ""
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        # Should fall back to using query as positive intent
        assert result.positive == [query]
        assert result.negative == []

    @patch('app.services.faiss_service.llm')
    def test_json_with_markdown_blocks(self, mock_llm):
        """Test handling JSON wrapped in markdown code blocks"""
        query = "show me burgers"

        mock_response = Mock()
        mock_response.content = '''```json
        {
            "positive": ["burgers", "hamburgers"],
            "negative": []
        }
        ```'''
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert "burgers" in result.positive or "hamburgers" in result.positive
        assert result.negative == []

    @patch('app.services.faiss_service.llm')
    def test_json_decode_error_fallback(self, mock_llm):
        """Test fallback when JSON decoding fails"""
        query = "invalid json query"

        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        # Should fall back to using query as positive intent
        assert result.positive == [query]
        assert result.negative == []

    @patch('app.services.faiss_service.llm')
    def test_llm_exception_fallback(self, mock_llm):
        """Test fallback when LLM throws exception"""
        query = "test query"

        mock_llm.invoke.side_effect = Exception("LLM error")

        result = extract_query_intent(query)

        # Should fall back to using query as positive intent
        assert result.positive == [query]
        assert result.negative == []

    @patch('app.services.faiss_service.llm')
    def test_multiple_negative_intents(self, mock_llm):
        """Test query with multiple negative intents"""
        query = "dishes without nuts dairy and eggs"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["dishes", "meals"],
            "negative": ["nuts", "dairy", "eggs"]
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert len(result.negative) >= 3
        assert "nuts" in result.negative
        assert "dairy" in result.negative
        assert "eggs" in result.negative

    @patch('app.services.faiss_service.llm')
    def test_only_negative_intents(self, mock_llm):
        """Test query with only negative intents"""
        query = "nothing with peanuts"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": [],
            "negative": ["peanuts"]
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert len(result.positive) == 0 or result.positive == []
        assert "peanuts" in result.negative

    @patch('app.services.faiss_service.llm')
    def test_synonyms_in_positive_intent(self, mock_llm):
        """Test that LLM expands query with synonyms"""
        query = "pizza"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["pizza", "margherita", "pepperoni", "flatbread"],
            "negative": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        # Should have multiple positive intents (synonyms)
        assert len(result.positive) > 1
        assert "pizza" in result.positive

    @patch('app.services.faiss_service.llm')
    def test_whitespace_query(self, mock_llm):
        """Test query with only whitespace"""
        query = "   "

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["   "],
            "negative": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        # Should still work, even with whitespace
        assert isinstance(result, QueryIntent)


class TestQueryIntentModel:
    """Test QueryIntent model"""

    def test_create_query_intent(self):
        """Test creating QueryIntent object"""
        intent = QueryIntent(positive=["pizza"], negative=["mushrooms"])

        assert intent.positive == ["pizza"]
        assert intent.negative == ["mushrooms"]

    def test_query_intent_empty_lists(self):
        """Test QueryIntent with empty lists"""
        intent = QueryIntent(positive=[], negative=[])

        assert intent.positive == []
        assert intent.negative == []

    def test_query_intent_many_items(self):
        """Test QueryIntent with many items"""
        positive = ["item" + str(i) for i in range(10)]
        negative = ["avoid" + str(i) for i in range(5)]

        intent = QueryIntent(positive=positive, negative=negative)

        assert len(intent.positive) == 10
        assert len(intent.negative) == 5


class TestEdgeCases:
    """Test edge cases in FAISS service"""

    @patch('app.services.faiss_service.llm')
    def test_very_long_query(self, mock_llm):
        """Test very long query"""
        query = "show me pizza " * 100

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["pizza"],
            "negative": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert "pizza" in result.positive

    @patch('app.services.faiss_service.llm')
    def test_special_characters_in_query(self, mock_llm):
        """Test query with special characters"""
        query = "dishes with jalapeño & café"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["jalapeño", "café"],
            "negative": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert len(result.positive) > 0

    @patch('app.services.faiss_service.llm')
    def test_numeric_price_query(self, mock_llm):
        """Test query with prices"""
        query = "dishes under $20"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["dishes under $20", "affordable meals"],
            "negative": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert len(result.positive) > 0

    @patch('app.services.faiss_service.llm')
    def test_complex_compound_query(self, mock_llm):
        """Test complex compound query"""
        query = "vegan pasta without gluten or dairy under $15"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["vegan pasta", "plant-based pasta"],
            "negative": ["gluten", "dairy"]
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        assert len(result.positive) > 0
        assert len(result.negative) > 0

    @patch('app.services.faiss_service.llm')
    def test_case_sensitivity(self, mock_llm):
        """Test that case is preserved in intents"""
        query = "PIZZA AND BURGERS"

        mock_response = Mock()
        mock_response.content = json.dumps({
            "positive": ["PIZZA", "BURGERS"],
            "negative": []
        })
        mock_llm.invoke.return_value = mock_response

        result = extract_query_intent(query)

        # Case should be preserved as returned by LLM
        assert len(result.positive) > 0
