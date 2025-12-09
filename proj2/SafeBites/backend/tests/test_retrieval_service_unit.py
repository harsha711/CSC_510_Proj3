"""
Unit tests for retrieval_service.py

Tests menu retrieval and filtering including:
- Menu item retrieval
- FAISS semantic search integration
- Filter application
- Error handling
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.retrieval_service import get_menu_items
from app.models.dish_info_model import DishData
from app.models.restaurant_model import MenuResultResponse


class TestGetMenuItems:
    """Test menu item retrieval"""

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    @patch('app.services.retrieval_service.apply_filters')
    def test_get_menu_items_success(self, mock_apply_filters, mock_semantic_search):
        """Test successful menu item retrieval"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {"menu_search": ["pizza"]}

        # Mock FAISS search results
        mock_hit = Mock()
        mock_hit.dish = {
            "_id": "dish123",
            "name": "Margherita Pizza",
            "description": "Classic pizza",
            "price": 12.99,
            "ingredients": ["dough", "cheese", "tomato"],
            "restaurant_id": "rest123",
            "serving_size": "12 inch",
            "availability": True,
            "explicit_allergens": [{"allergen": "dairy"}],
            "nutrition_facts": {"calories": 300}
        }
        mock_semantic_search.return_value = [mock_hit]

        # Mock filter (returns same dishes)
        mock_apply_filters.return_value = [
            DishData(
                dish_id="dish123",
                dish_name="Margherita Pizza",
                restaurant_id="rest123",
                description="Classic pizza",
                price=12.99,
                ingredients=["dough", "cheese", "tomato"],
                serving_size="12 inch",
                availability=True,
                allergens=["dairy"],
                nutrition_facts={"calories": 300}
            )
        ]

        result = get_menu_items(state)

        assert "menu_results" in result
        assert isinstance(result["menu_results"], MenuResultResponse)
        assert len(result["menu_results"].menu_results) == 1
        assert "pizza" in result["menu_results"].menu_results

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    def test_no_menu_search_query_parts(self, mock_semantic_search):
        """Test when no menu_search query parts exist"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {}

        result = get_menu_items(state)

        assert result["menu_results"].menu_results == {}
        mock_semantic_search.assert_not_called()

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    def test_empty_query_parts_list(self, mock_semantic_search):
        """Test when menu_search list is empty"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {"menu_search": []}

        result = get_menu_items(state)

        assert result["menu_results"].menu_results == {}
        mock_semantic_search.assert_not_called()

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    @patch('app.services.retrieval_service.apply_filters')
    def test_no_dishes_found(self, mock_apply_filters, mock_semantic_search):
        """Test when no dishes are found"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {"menu_search": ["nonexistent dish"]}

        mock_semantic_search.return_value = []

        result = get_menu_items(state)

        assert "nonexistent dish" in result["menu_results"].menu_results
        assert result["menu_results"].menu_results["nonexistent dish"] == []

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    @patch('app.services.retrieval_service.apply_filters')
    def test_multiple_queries(self, mock_apply_filters, mock_semantic_search):
        """Test processing multiple menu search queries"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {"menu_search": ["pizza", "pasta", "salad"]}

        # Mock FAISS search results
        mock_hit = Mock()
        mock_hit.dish = {
            "_id": "dish123",
            "name": "Test Dish",
            "description": "Test",
            "price": 10.0,
            "ingredients": ["test"],
            "restaurant_id": "rest123",
            "explicit_allergens": [],
            "nutrition_facts": {}
        }
        mock_semantic_search.return_value = [mock_hit]

        mock_apply_filters.return_value = [
            DishData(
                dish_id="dish123",
                dish_name="Test Dish",
                restaurant_id="rest123",
                description="Test",
                price=10.0,
                ingredients=["test"],
                allergens=[],
                nutrition_facts={}
            )
        ]

        result = get_menu_items(state)

        assert len(result["menu_results"].menu_results) == 3
        assert "pizza" in result["menu_results"].menu_results
        assert "pasta" in result["menu_results"].menu_results
        assert "salad" in result["menu_results"].menu_results
        assert mock_semantic_search.call_count == 3

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    @patch('app.services.retrieval_service.apply_filters')
    def test_filter_reduces_results(self, mock_apply_filters, mock_semantic_search):
        """Test that filtering reduces dish count"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {"menu_search": ["pizza under $10"]}

        # Mock FAISS returns 5 dishes
        mock_hits = []
        for i in range(5):
            mock_hit = Mock()
            mock_hit.dish = {
                "_id": f"dish{i}",
                "name": f"Pizza {i}",
                "description": "Pizza",
                "price": 10.0 + i,
                "ingredients": ["dough"],
                "restaurant_id": "rest123",
                "explicit_allergens": [],
                "nutrition_facts": {}
            }
            mock_hits.append(mock_hit)
        mock_semantic_search.return_value = mock_hits

        # Mock filter returns only 2 dishes (under $10)
        mock_apply_filters.return_value = [
            DishData(
                dish_id="dish0",
                dish_name="Pizza 0",
                restaurant_id="rest123",
                description="Pizza",
                price=10.0,
                ingredients=["dough"],
                allergens=[],
                nutrition_facts={}
            ),
            DishData(
                dish_id="dish1",
                dish_name="Pizza 1",
                restaurant_id="rest123",
                description="Pizza",
                price=11.0,
                ingredients=["dough"],
                allergens=[],
                nutrition_facts={}
            )
        ]

        result = get_menu_items(state)

        dishes = result["menu_results"].menu_results["pizza under $10"]
        assert len(dishes) == 2

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    def test_exception_in_retrieval(self, mock_semantic_search):
        """Test exception handling during retrieval"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {"menu_search": ["pizza"]}

        mock_semantic_search.side_effect = Exception("FAISS error")

        result = get_menu_items(state)

        # Should return empty results for failed query
        assert "pizza" in result["menu_results"].menu_results
        assert result["menu_results"].menu_results["pizza"] == []

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    @patch('app.services.retrieval_service.apply_filters')
    def test_none_restaurant_id(self, mock_apply_filters, mock_semantic_search):
        """Test retrieval with None restaurant_id (cross-restaurant search)"""
        state = Mock()
        state.restaurant_id = None
        state.query_parts = {"menu_search": ["pizza"]}

        mock_hit = Mock()
        mock_hit.dish = {
            "_id": "dish123",
            "name": "Pizza",
            "description": "Test",
            "price": 10.0,
            "ingredients": ["dough"],
            "restaurant_id": "rest456",
            "explicit_allergens": [],
            "nutrition_facts": {}
        }
        mock_semantic_search.return_value = [mock_hit]

        mock_apply_filters.return_value = [
            DishData(
                dish_id="dish123",
                dish_name="Pizza",
                restaurant_id="rest456",
                description="Test",
                price=10.0,
                ingredients=["dough"],
                allergens=[],
                nutrition_facts={}
            )
        ]

        result = get_menu_items(state)

        # Should call semantic search with None restaurant_id
        mock_semantic_search.assert_called_once_with("pizza", None)
        assert len(result["menu_results"].menu_results["pizza"]) == 1

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    @patch('app.services.retrieval_service.apply_filters')
    def test_dish_data_construction(self, mock_apply_filters, mock_semantic_search):
        """Test proper DishData object construction from search results"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {"menu_search": ["test"]}

        mock_hit = Mock()
        mock_hit.dish = {
            "_id": "dish123",
            "name": "Test Dish",
            "description": "A test dish",
            "price": 15.99,
            "ingredients": ["ingredient1", "ingredient2"],
            "restaurant_id": "rest123",
            "serving_size": "large",
            "availability": False,
            "explicit_allergens": [{"allergen": "nuts"}, {"allergen": "dairy"}],
            "nutrition_facts": {"calories": 500, "protein": 20}
        }
        mock_semantic_search.return_value = [mock_hit]

        dish_data = DishData(
            dish_id="dish123",
            dish_name="Test Dish",
            restaurant_id="rest123",
            description="A test dish",
            price=15.99,
            ingredients=["ingredient1", "ingredient2"],
            serving_size="large",
            availability=False,
            allergens=["nuts", "dairy"],
            nutrition_facts={"calories": 500, "protein": 20}
        )
        mock_apply_filters.return_value = [dish_data]

        result = get_menu_items(state)

        dishes = result["menu_results"].menu_results["test"]
        assert len(dishes) == 1
        assert dishes[0].dish_id == "dish123"
        assert dishes[0].serving_size == "large"
        assert dishes[0].availability == False
        assert "nuts" in dishes[0].allergens
        assert "dairy" in dishes[0].allergens

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    @patch('app.services.retrieval_service.apply_filters')
    def test_missing_optional_fields(self, mock_apply_filters, mock_semantic_search):
        """Test handling of missing optional fields in dish data"""
        state = Mock()
        state.restaurant_id = "rest123"
        state.query_parts = {"menu_search": ["test"]}

        # Mock hit without optional fields
        mock_hit = Mock()
        mock_hit.dish = {
            "_id": "dish123",
            "name": "Test Dish",
            "description": "Test",
            "price": 10.0,
            "ingredients": ["test"],
            "restaurant_id": "rest123"
            # Missing: serving_size, availability, explicit_allergens, nutrition_facts
        }
        mock_semantic_search.return_value = [mock_hit]

        mock_apply_filters.return_value = [
            DishData(
                dish_id="dish123",
                dish_name="Test Dish",
                restaurant_id="rest123",
                description="Test",
                price=10.0,
                ingredients=["test"],
                serving_size=None,
                availability=True,  # Default
                allergens=[],
                nutrition_facts={}
            )
        ]

        result = get_menu_items(state)

        dishes = result["menu_results"].menu_results["test"]
        assert len(dishes) == 1
        assert dishes[0].availability == True  # Default value
        assert dishes[0].allergens == []
        assert dishes[0].nutrition_facts == {}


class TestStateAttributes:
    """Test state attribute handling"""

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    def test_missing_restaurant_id_attribute(self, mock_semantic_search):
        """Test when state doesn't have restaurant_id attribute"""
        state = Mock(spec=[])  # Empty spec, no attributes
        state.query_parts = {"menu_search": ["pizza"]}

        # Mock getattr to return None for missing restaurant_id
        def mock_getattr(obj, name, default=None):
            if name == "restaurant_id":
                return None
            if name == "query_parts":
                return {"menu_search": ["pizza"]}
            return default

        with patch('builtins.getattr', side_effect=mock_getattr):
            result = get_menu_items(state)

        # Should still work, just pass None to semantic search
        assert "menu_results" in result

    @patch('app.services.retrieval_service.semantic_retrieve_with_negation')
    def test_missing_query_parts_attribute(self, mock_semantic_search):
        """Test when state doesn't have query_parts attribute"""
        state = Mock()
        state.restaurant_id = "rest123"
        # Don't set query_parts

        result = get_menu_items(state)

        # Should return empty results
        assert result["menu_results"].menu_results == {}
