"""
Unit tests for dish_service.py

Tests CRUD operations for dishes including:
- Creating dishes
- Listing dishes with allergen safety
- Getting single dishes
- Updating dishes
- Deleting dishes
- Allergen safety checks
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId
from app.services.dish_service import (
    create_dish,
    list_dishes,
    get_dish,
    update_dish,
    delete_dish,
    _to_out
)
from app.models.exception_model import (
    NotFoundException,
    BadRequestException,
    DatabaseException,
    ConflictException
)


class TestToOut:
    """Test _to_out helper function"""

    def test_converts_object_id_to_string(self):
        """Test that ObjectId is converted to string"""
        doc = {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Pizza"}
        result = _to_out(doc)

        assert isinstance(result["_id"], str)
        assert result["_id"] == "507f1f77bcf86cd799439011"
        assert result["name"] == "Pizza"

    def test_handles_none_doc(self):
        """Test that None doc returns None"""
        result = _to_out(None)
        assert result is None

    def test_preserves_other_fields(self):
        """Test that other fields are preserved"""
        doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "Burger",
            "price": 12.99,
            "ingredients": ["beef", "bun"]
        }
        result = _to_out(doc)

        assert result["name"] == "Burger"
        assert result["price"] == 12.99
        assert result["ingredients"] == ["beef", "bun"]


@patch('app.services.dish_service.db')
class TestCreateDish:
    """Test dish creation"""

    def test_create_dish_success(self, mock_db):
        """Test successful dish creation"""
        dish_create = Mock()
        dish_create.name = "Pizza"
        dish_create.restaurant_id = "rest123"
        dish_create.model_dump.return_value = {
            "name": "Pizza",
            "restaurant_id": "rest123",
            "price": 12.99
        }

        # Use side_effect for multiple calls to find_one
        mock_db.dishes.find_one.side_effect = [
            None,  # First call: check for existing dish
            {  # Second call: get created dish
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "Pizza",
                "restaurant_id": "rest123",
                "price": 12.99,
                "availability": True
            }
        ]
        mock_db.dishes.insert_one.return_value = Mock(inserted_id=ObjectId("507f1f77bcf86cd799439011"))

        result = create_dish("rest123", dish_create)

        assert result["name"] == "Pizza"
        assert result["safe_for_user"] is True
        assert "availability" in result

    def test_create_dish_missing_name(self, mock_db):
        """Test creating dish without name raises error"""
        dish_create = Mock()
        dish_create.name = None
        dish_create.restaurant_id = "rest123"

        with pytest.raises(BadRequestException) as exc_info:
            create_dish("rest123", dish_create)

        assert "Missing required dish fields" in str(exc_info.value.message)

    def test_create_dish_duplicate_name(self, mock_db):
        """Test creating dish with duplicate name raises error"""
        dish_create = Mock()
        dish_create.name = "Pizza"
        dish_create.restaurant_id = "rest123"

        # Existing dish found
        mock_db.dishes.find_one.return_value = {"_id": ObjectId(), "name": "Pizza"}

        with pytest.raises(ConflictException):
            create_dish("rest123", dish_create)

    def test_create_dish_database_error(self, mock_db):
        """Test database error during creation"""
        dish_create = Mock()
        dish_create.name = "Pizza"
        dish_create.restaurant_id = "rest123"
        dish_create.model_dump.return_value = {"name": "Pizza", "restaurant_id": "rest123"}

        mock_db.dishes.find_one.return_value = None
        mock_db.dishes.insert_one.side_effect = Exception("DB Error")

        with pytest.raises(DatabaseException):
            create_dish("rest123", dish_create)

    def test_create_dish_sets_availability_default(self, mock_db):
        """Test that availability defaults to True"""
        dish_create = Mock()
        dish_create.name = "Salad"
        dish_create.restaurant_id = "rest123"
        dish_create.model_dump.return_value = {"name": "Salad", "restaurant_id": "rest123"}

        mock_db.dishes.find_one.side_effect = [
            None,  # Check for existing
            {  # Get created dish
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "Salad",
                "availability": True
            }
        ]
        mock_db.dishes.insert_one.return_value = Mock(inserted_id=ObjectId("507f1f77bcf86cd799439011"))

        result = create_dish("rest123", dish_create)

        assert result["availability"] is True


@patch('app.services.dish_service.db')
class TestListDishes:
    """Test dish listing with allergen safety"""

    def test_list_dishes_no_user(self, mock_db):
        """Test listing dishes without user context"""
        mock_db.dishes.find.return_value.limit.return_value = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Pizza", "explicit_allergens": []},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "Burger", "explicit_allergens": []}
        ]

        result = list_dishes({}, user_id=None)

        assert len(result) == 2
        assert all(d["safe_for_user"] is True for d in result)

    def test_list_dishes_with_safe_user(self, mock_db):
        """Test listing dishes with user having no allergen conflicts"""
        mock_db.dishes.find.return_value.limit.return_value = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "Pizza",
                "explicit_allergens": [{"allergen": "dairy"}]
            }
        ]
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439020"),
            "allergen_preferences": ["peanuts"]  # No dairy
        }

        result = list_dishes({}, user_id="507f1f77bcf86cd799439020")

        assert len(result) == 1
        assert result[0]["safe_for_user"] is True

    def test_list_dishes_with_unsafe_user(self, mock_db):
        """Test listing dishes with user having allergen conflicts"""
        mock_db.dishes.find.return_value.limit.return_value = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "Pizza",
                "explicit_allergens": [{"allergen": "dairy"}]
            }
        ]
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439020"),
            "allergen_preferences": ["dairy"]
        }

        result = list_dishes({}, user_id="507f1f77bcf86cd799439020")

        assert len(result) == 1
        assert result[0]["safe_for_user"] is False

    def test_list_dishes_case_insensitive_allergen_matching(self, mock_db):
        """Test allergen matching is case-insensitive"""
        mock_db.dishes.find.return_value.limit.return_value = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "Dish",
                "explicit_allergens": [{"allergen": "DAIRY"}]
            }
        ]
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439020"),
            "allergen_preferences": ["dairy"]  # lowercase
        }

        result = list_dishes({}, user_id="507f1f77bcf86cd799439020")

        assert result[0]["safe_for_user"] is False

    def test_list_dishes_user_not_found(self, mock_db):
        """Test listing with invalid user ID"""
        mock_db.dishes.find.return_value.limit.return_value = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Pizza", "explicit_allergens": []}
        ]
        mock_db.users.find_one.return_value = None

        result = list_dishes({}, user_id="invalid_user")

        assert len(result) == 1
        assert result[0]["safe_for_user"] is True  # Default to safe

    def test_list_dishes_database_error(self, mock_db):
        """Test database error during listing"""
        mock_db.dishes.find.side_effect = Exception("DB Error")

        with pytest.raises(DatabaseException):
            list_dishes({})

    def test_list_dishes_applies_filter(self, mock_db):
        """Test that filter query is applied"""
        filter_query = {"restaurant_id": "rest123"}
        mock_db.dishes.find.return_value.limit.return_value = []

        list_dishes(filter_query)

        mock_db.dishes.find.assert_called_once_with(filter_query)

    def test_list_dishes_limits_to_100(self, mock_db):
        """Test that results are limited to 100"""
        mock_db.dishes.find.return_value.limit.return_value = []

        list_dishes({})

        mock_db.dishes.find.return_value.limit.assert_called_once_with(100)


@patch('app.services.dish_service.db')
class TestGetDish:
    """Test getting single dish"""

    def test_get_dish_success(self, mock_db):
        """Test successfully getting a dish"""
        mock_db.dishes.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "Pizza",
            "explicit_allergens": []
        }

        result = get_dish("507f1f77bcf86cd799439011")

        assert result["name"] == "Pizza"
        assert result["safe_for_user"] is True

    def test_get_dish_invalid_id(self, mock_db):
        """Test getting dish with invalid ID format"""
        with pytest.raises(NotFoundException):
            get_dish("invalid_id")

    def test_get_dish_not_found(self, mock_db):
        """Test getting non-existent dish"""
        mock_db.dishes.find_one.return_value = None

        with pytest.raises(NotFoundException):
            get_dish("507f1f77bcf86cd799439011")

    def test_get_dish_with_user_safe(self, mock_db):
        """Test getting dish with user (safe)"""
        mock_db.dishes.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "Pizza",
            "explicit_allergens": [{"allergen": "dairy"}]
        }
        mock_db.users.find_one.return_value = {
            "allergen_preferences": ["peanuts"]
        }

        result = get_dish("507f1f77bcf86cd799439011", user_id="507f1f77bcf86cd799439020")

        assert result["safe_for_user"] is True

    def test_get_dish_with_user_unsafe(self, mock_db):
        """Test getting dish with user (unsafe)"""
        mock_db.dishes.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "Pizza",
            "explicit_allergens": [{"allergen": "dairy"}]
        }
        mock_db.users.find_one.return_value = {
            "allergen_preferences": ["dairy"]
        }

        result = get_dish("507f1f77bcf86cd799439011", user_id="507f1f77bcf86cd799439020")

        assert result["safe_for_user"] is False


@patch('app.services.dish_service.db')
class TestUpdateDish:
    """Test dish update"""

    def test_update_dish_success(self, mock_db):
        """Test successful dish update"""
        update_data = {"price": 14.99}

        mock_db.dishes.update_one.return_value = Mock(matched_count=1)
        mock_db.dishes.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "Pizza",
            "price": 14.99
        }

        result = update_dish("507f1f77bcf86cd799439011", update_data)

        assert result["price"] == 14.99
        assert result["safe_for_user"] is True

    def test_update_dish_no_data(self, mock_db):
        """Test update with no data raises error"""
        with pytest.raises(BadRequestException):
            update_dish("507f1f77bcf86cd799439011", {})

    def test_update_dish_invalid_id(self, mock_db):
        """Test update with invalid ID"""
        with pytest.raises(NotFoundException):
            update_dish("invalid_id", {"price": 10})

    def test_update_dish_not_found(self, mock_db):
        """Test updating non-existent dish"""
        mock_db.dishes.update_one.return_value = Mock(matched_count=0)

        with pytest.raises(NotFoundException):
            update_dish("507f1f77bcf86cd799439011", {"price": 10})

    def test_update_dish_name_conflict(self, mock_db):
        """Test updating to duplicate name raises error"""
        update_data = {"name": "Burger"}

        mock_db.dishes.find_one.side_effect = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Pizza", "restaurant": "rest1"},  # Current dish
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "Burger", "restaurant": "rest1"}  # Duplicate
        ]

        with pytest.raises(ConflictException):
            update_dish("507f1f77bcf86cd799439011", update_data)

    def test_update_dish_name_no_conflict_same_dish(self, mock_db):
        """Test updating dish name to its own name is allowed"""
        update_data = {"name": "Pizza"}

        mock_db.dishes.find_one.side_effect = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Pizza", "restaurant": "rest1"},  # Current dish
            None,  # No other dish with same name
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Pizza"}  # Updated dish
        ]
        mock_db.dishes.update_one.return_value = Mock(matched_count=1)

        result = update_dish("507f1f77bcf86cd799439011", update_data)

        assert result["name"] == "Pizza"


@patch('app.services.dish_service.db')
class TestDeleteDish:
    """Test dish deletion"""

    def test_delete_dish_success(self, mock_db):
        """Test successful dish deletion"""
        mock_db.dishes.delete_one.return_value = Mock(deleted_count=1)

        result = delete_dish("507f1f77bcf86cd799439011")

        assert result == {"detail": "deleted"}

    def test_delete_dish_invalid_id(self, mock_db):
        """Test delete with invalid ID"""
        with pytest.raises(NotFoundException):
            delete_dish("invalid_id")

    def test_delete_dish_not_found(self, mock_db):
        """Test deleting non-existent dish"""
        mock_db.dishes.delete_one.return_value = Mock(deleted_count=0)

        with pytest.raises(NotFoundException):
            delete_dish("507f1f77bcf86cd799439011")


class TestAllergenSafetyEdgeCases:
    """Test edge cases in allergen safety logic"""

    @patch('app.services.dish_service.db')
    def test_no_explicit_allergens_key(self, mock_db):
        """Test dish without explicit_allergens key"""
        mock_db.dishes.find.return_value.limit.return_value = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Pizza"}
        ]

        # Should not crash
        result = list_dishes({})

        assert len(result) == 1

    @patch('app.services.dish_service.db')
    def test_empty_allergen_preferences(self, mock_db):
        """Test user with empty allergen preferences"""
        mock_db.dishes.find.return_value.limit.return_value = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Pizza", "explicit_allergens": [{"allergen": "dairy"}]}
        ]
        mock_db.users.find_one.return_value = {"allergen_preferences": []}

        result = list_dishes({}, user_id="507f1f77bcf86cd799439020")

        assert result[0]["safe_for_user"] is True

    @patch('app.services.dish_service.db')
    def test_multiple_allergens_one_match(self, mock_db):
        """Test dish with multiple allergens, user has one"""
        mock_db.dishes.find.return_value.limit.return_value = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "Complex Dish",
                "explicit_allergens": [
                    {"allergen": "dairy"},
                    {"allergen": "nuts"},
                    {"allergen": "soy"}
                ]
            }
        ]
        mock_db.users.find_one.return_value = {"allergen_preferences": ["nuts"]}

        result = list_dishes({}, user_id="507f1f77bcf86cd799439020")

        assert result[0]["safe_for_user"] is False
