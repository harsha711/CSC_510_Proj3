"""
Unit tests for response_synthesizer_tool.py

Tests the response formatting and aggregation including:
- Menu result formatting with compatibility scores
- Dish info result formatting
- User preference result formatting
- Irrelevant query handling
- Filtering to only show dishes with compatibility scores (max 7)
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.response_synthesizer_tool import format_final_response


class TestFormatFinalResponse:
    """Test response formatting with menu results"""

    def test_format_menu_results_without_compatibility_scores(self):
        """Test that dishes without compatibility scores are filtered out"""
        state = Mock()
        state.restaurant_id = "rest123"

        # Create mock dishes
        dishes = []
        for i in range(3):
            dish = Mock()
            dish.dish_id = f"dish{i}"
            dish.dish_name = f"Dish {i}"
            dish.description = "Test"
            dish.price = 10.0
            dish.ingredients = ["test"]
            dish.allergens = []
            dish.nutrition_facts = {}
            dish.availability = True
            dish.serving_size = None
            dishes.append(dish)

        # Create menu results
        menu_results = Mock()
        menu_results.menu_results = {"test": dishes}
        state.menu_results = menu_results

        # No compatibility results
        state.compatibility_results = None
        state.info_results = None
        state.preference_results = None
        state.query_parts = None

        result = format_final_response(state)

        # All dishes should be filtered out (no compatibility scores)
        assert result["status"] == "success"
        assert len(result["responses"]) == 1
        assert len(result["responses"][0]["result"]) == 0

    def test_format_filters_to_max_7_dishes(self):
        """Test that only dishes with compatibility scores are included (max 7)"""
        state = Mock()
        state.restaurant_id = "rest123"

        # Create 10 mock dishes
        dishes = []
        for i in range(10):
            dish = Mock()
            dish.dish_id = f"dish{i}"
            dish.dish_name = f"Dish {i}"
            dish.description = "Test"
            dish.price = 10.0
            dish.ingredients = []
            dish.allergens = []
            dish.nutrition_facts = {}
            dish.availability = True
            dish.serving_size = None
            dishes.append(dish)

        menu_results = Mock()
        menu_results.menu_results = {"test": dishes}
        state.menu_results = menu_results

        # Create compatibility scores for only first 7 dishes
        compatibility_results = Mock()
        scores = {}
        for i in range(7):
            comp_score = Mock()
            comp_score.overall_score = 80 - i
            comp_score.recommendation = "Good"
            comp_score.alternative_suggestions = []

            for attr in ["allergen_safety", "nutrition_match", "taste_preference", "dietary_pattern"]:
                mock_attr = Mock()
                mock_attr.model_dump.return_value = {"score": 80}
                setattr(comp_score, attr, mock_attr)

            scores[f"dish{i}"] = comp_score

        compatibility_results.scores = scores
        state.compatibility_results = compatibility_results

        state.info_results = None
        state.preference_results = None
        state.query_parts = None

        result = format_final_response(state)

        # Should only have 7 dishes (those with scores)
        assert len(result["responses"][0]["result"]) == 7

    def test_format_sorts_by_compatibility_score(self):
        """Test that dishes are sorted by compatibility score (highest first)"""
        state = Mock()
        state.restaurant_id = "rest123"

        # Create dishes with different scores
        dishes = []
        scores = {}
        for i, score_val in enumerate([60, 90, 75]):
            dish = Mock()
            dish.dish_id = f"dish{i}"
            dish.dish_name = f"Dish {i}"
            dish.description = "Test"
            dish.price = 10.0
            dish.ingredients = []
            dish.allergens = []
            dish.nutrition_facts = {}
            dish.availability = True
            dish.serving_size = None
            dishes.append(dish)

            comp_score = Mock()
            comp_score.overall_score = score_val
            comp_score.recommendation = "Good"
            comp_score.alternative_suggestions = []

            for attr in ["allergen_safety", "nutrition_match", "taste_preference", "dietary_pattern"]:
                mock_attr = Mock()
                mock_attr.model_dump.return_value = {"score": score_val}
                setattr(comp_score, attr, mock_attr)

            scores[f"dish{i}"] = comp_score

        menu_results = Mock()
        menu_results.menu_results = {"test": dishes}
        state.menu_results = menu_results

        compatibility_results = Mock()
        compatibility_results.scores = scores
        state.compatibility_results = compatibility_results

        state.info_results = None
        state.preference_results = None
        state.query_parts = None

        result = format_final_response(state)

        # Should be sorted: 90, 75, 60
        result_dishes = result["responses"][0]["result"]
        assert result_dishes[0]["name"] == "Dish 1"  # Score 90
        assert result_dishes[1]["name"] == "Dish 2"  # Score 75
        assert result_dishes[2]["name"] == "Dish 0"  # Score 60


class TestFormatInfoResults:
    """Test formatting dish info results"""

    def test_format_info_results(self):
        """Test formatting dish info results"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.menu_results = None
        state.compatibility_results = None
        state.preference_results = None
        state.query_parts = None

        # Create info result
        info_result = Mock()
        info_result.model_dump.return_value = {
            "answer": "300 calories",
            "context": "Pizza has 300 calories"
        }

        info_results = Mock()
        info_results.info_results = {"calories": info_result}
        state.info_results = info_results

        result = format_final_response(state)

        assert result["status"] == "success"
        assert len(result["responses"]) == 1
        assert result["responses"][0]["type"] == "dish_info"
        assert result["responses"][0]["query"] == "calories"

    def test_format_multiple_info_results(self):
        """Test formatting multiple info results"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.menu_results = None
        state.compatibility_results = None
        state.preference_results = None
        state.query_parts = None

        # Create multiple info results
        info_results = Mock()
        info_dict = {}
        for query in ["calories", "price", "ingredients"]:
            info_result = Mock()
            info_result.model_dump.return_value = {"answer": f"Answer for {query}"}
            info_dict[query] = info_result

        info_results.info_results = info_dict
        state.info_results = info_results

        result = format_final_response(state)

        assert len(result["responses"]) == 3


class TestFormatIrrelevantQueries:
    """Test formatting irrelevant queries"""

    def test_format_irrelevant_query(self):
        """Test formatting irrelevant query"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.menu_results = None
        state.compatibility_results = None
        state.info_results = None
        state.preference_results = None

        state.query_parts = {"irrelevant": ["tell me a joke"]}

        result = format_final_response(state)

        assert result["status"] == "success"
        assert len(result["responses"]) == 1
        assert result["responses"][0]["type"] == "irrelevant"
        assert result["responses"][0]["query"] == "tell me a joke"
        assert "couldn't understand" in result["responses"][0]["result"]["message"]

    def test_format_multiple_irrelevant_queries(self):
        """Test formatting multiple irrelevant queries"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.menu_results = None
        state.compatibility_results = None
        state.info_results = None
        state.preference_results = None

        state.query_parts = {"irrelevant": ["joke", "weather", "news"]}

        result = format_final_response(state)

        assert len(result["responses"]) == 3
        assert all(r["type"] == "irrelevant" for r in result["responses"])


class TestEmptyResults:
    """Test formatting with empty results"""

    def test_format_no_results(self):
        """Test formatting when no results exist"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.menu_results = None
        state.compatibility_results = None
        state.info_results = None
        state.preference_results = None
        state.query_parts = None

        result = format_final_response(state)

        assert result["status"] == "failed"
        assert len(result["responses"]) == 0

    def test_format_empty_menu_results(self):
        """Test formatting with empty menu results"""
        state = Mock()
        state.restaurant_id = "rest123"

        menu_results = Mock()
        menu_results.menu_results = {}
        state.menu_results = menu_results

        state.compatibility_results = None
        state.info_results = None
        state.preference_results = None
        state.query_parts = None

        result = format_final_response(state)

        assert result["status"] == "failed"
