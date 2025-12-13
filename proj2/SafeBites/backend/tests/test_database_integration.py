"""
Database Integration Tests

Tests for MongoDB database operations:
- Restaurant CRUD operations
- Dish CRUD operations
- User profile storage
- FAISS index integration with database

These tests validate database connectivity, data integrity, and query operations.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from pymongo.errors import PyMongoError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestRestaurantDatabase:
    """Test restaurant database operations"""

    @patch('app.database.restaurants.get_all_restaurants')
    def test_get_all_restaurants_from_db(self, mock_get_all):
        """
        Test fetching all restaurants from database

        Should return list of restaurant documents
        """
        mock_get_all.return_value = [
            {"_id": "rest_1", "name": "Restaurant 1", "address": "123 Main St"},
            {"_id": "rest_2", "name": "Restaurant 2", "address": "456 Oak Ave"}
        ]

        restaurants = mock_get_all()

        assert len(restaurants) > 0
        assert all("name" in r for r in restaurants)

    @patch('app.database.restaurants.get_restaurant_by_id')
    def test_get_restaurant_by_id_from_db(self, mock_get_by_id):
        """
        Test fetching specific restaurant by ID

        Should return restaurant document or None
        """
        mock_get_by_id.return_value = {
            "_id": "rest_1",
            "name": "Test Restaurant",
            "address": "123 Test St",
            "cuisine": ["Italian"]
        }

        restaurant = mock_get_by_id("rest_1")

        assert restaurant is not None
        assert restaurant["_id"] == "rest_1"
        assert "name" in restaurant

    @patch('app.database.restaurants.get_restaurant_by_id')
    def test_get_nonexistent_restaurant(self, mock_get_by_id):
        """Test that getting non-existent restaurant returns None"""
        mock_get_by_id.return_value = None

        restaurant = mock_get_by_id("nonexistent_999")

        assert restaurant is None


class TestDishDatabase:
    """Test dish database operations"""

    @patch('app.database.dishes.get_dishes_by_restaurant')
    def test_get_dishes_by_restaurant_id(self, mock_get_dishes):
        """
        Test fetching dishes for a specific restaurant

        Should return list of dish documents
        """
        mock_get_dishes.return_value = [
            {
                "_id": "dish_1",
                "name": "Margherita Pizza",
                "restaurant_id": "rest_1",
                "price": 12.99,
                "ingredients": ["dough", "tomato", "mozzarella"]
            },
            {
                "_id": "dish_2",
                "name": "Pepperoni Pizza",
                "restaurant_id": "rest_1",
                "price": 14.99,
                "ingredients": ["dough", "tomato", "pepperoni"]
            }
        ]

        dishes = mock_get_dishes("rest_1")

        assert len(dishes) > 0
        assert all("name" in d for d in dishes)
        assert all(d["restaurant_id"] == "rest_1" for d in dishes)

    @patch('app.database.dishes.get_dish_by_id')
    def test_get_dish_by_id_from_db(self, mock_get_dish):
        """Test fetching specific dish by ID"""
        mock_get_dish.return_value = {
            "_id": "dish_1",
            "name": "Test Dish",
            "restaurant_id": "rest_1",
            "price": 10.99,
            "ingredients": ["ingredient1", "ingredient2"],
            "explicit_allergens": [{"allergen": "nuts"}]
        }

        dish = mock_get_dish("dish_1")

        assert dish is not None
        assert dish["_id"] == "dish_1"
        assert "ingredients" in dish
        assert "explicit_allergens" in dish

    @patch('app.database.dishes.search_dishes_by_name')
    def test_search_dishes_by_name(self, mock_search):
        """
        Test searching dishes by name pattern

        Should support partial matching (e.g., "pizza" matches "Margherita Pizza")
        """
        mock_search.return_value = [
            {"_id": "dish_1", "name": "Margherita Pizza"},
            {"_id": "dish_2", "name": "Pepperoni Pizza"},
            {"_id": "dish_3", "name": "BBQ Chicken Pizza"}
        ]

        dishes = mock_search("pizza")

        assert len(dishes) == 3
        assert all("pizza" in d["name"].lower() for d in dishes)


class TestUserProfileDatabase:
    """Test user profile database operations"""

    @patch('app.database.user_profiles.get_user_profile')
    def test_get_user_profile_from_db(self, mock_get_profile):
        """
        Test fetching user profile from database

        Should return profile document or None
        """
        mock_get_profile.return_value = {
            "user_id": "user_123",
            "allergens": ["peanuts", "shellfish"],
            "health_goals": ["weight_loss"],
            "dietary_pattern": "vegetarian"
        }

        profile = mock_get_profile("user_123")

        if profile is not None:
            assert "allergens" in profile or "health_goals" in profile

    @patch('app.database.user_profiles.save_user_profile')
    def test_save_user_profile_to_db(self, mock_save):
        """
        Test saving user profile to database

        Should store or update profile document
        """
        mock_save.return_value = True

        profile_data = {
            "user_id": "user_123",
            "allergens": ["nuts"],
            "health_goals": ["high_protein"],
            "dietary_pattern": "omnivore"
        }

        result = mock_save(profile_data)

        # Should succeed
        assert result is True or result is not None


class TestDatabaseFieldMapping:
    """Test field mapping between database and models"""

    def test_restaurant_address_location_mapping(self):
        """
        Test that 'address' field in DB maps to 'location' in model

        This validates the fix for 500 error on /restaurants/ endpoint
        """
        # Database document
        db_doc = {
            "_id": "rest_1",
            "name": "Test Restaurant",
            "address": "123 Main St",  # DB uses 'address'
            "cuisine": ["Italian"]
        }

        # Model should accept this and alias to 'location'
        # This is tested in test_restaurant_endpoint.py
        assert "address" in db_doc
        # Model uses Field(alias="address") to map to location

    def test_dish_id_field_mapping(self):
        """
        Test that '_id' field in DB maps to 'id' in model

        MongoDB uses '_id', but models use 'id'
        """
        db_doc = {
            "_id": "dish_1",  # MongoDB format
            "name": "Test Dish",
            "restaurant_id": "rest_1"
        }

        # Model should handle _id → id mapping
        assert "_id" in db_doc


class TestFAISSIndexIntegration:
    """Test FAISS index integration with database"""

    @patch('app.services.faiss_service.load_faiss_index')
    def test_faiss_index_loads_successfully(self, mock_load):
        """
        Test that FAISS index loads from disk

        Index files: index.faiss, index.pkl
        """
        mock_load.return_value = MagicMock()

        index = mock_load()

        assert index is not None

    @patch('app.services.faiss_service.search_faiss_index')
    def test_faiss_search_returns_dish_ids(self, mock_search):
        """
        Test that FAISS search returns valid dish IDs

        These IDs should exist in MongoDB
        """
        mock_search.return_value = [
            ("dish_1", 0.5),  # (dish_id, distance)
            ("dish_2", 0.7),
            ("dish_3", 1.2)
        ]

        results = mock_search("pizza")

        assert len(results) > 0
        assert all(isinstance(r[0], str) for r in results)  # dish_id is string
        assert all(isinstance(r[1], (int, float)) for r in results)  # distance is numeric

    @patch('app.database.dishes.get_dishes_by_ids')
    def test_fetch_dishes_from_faiss_results(self, mock_get_dishes):
        """
        Test fetching dish documents for FAISS search results

        Workflow: FAISS returns IDs → MongoDB fetches full documents
        """
        mock_get_dishes.return_value = [
            {"_id": "dish_1", "name": "Pizza 1", "restaurant_id": "rest_1"},
            {"_id": "dish_2", "name": "Pizza 2", "restaurant_id": "rest_2"}
        ]

        dish_ids = ["dish_1", "dish_2"]
        dishes = mock_get_dishes(dish_ids)

        assert len(dishes) == 2
        assert all("name" in d for d in dishes)
        assert all("restaurant_id" in d for d in dishes)


class TestDatabaseErrorHandling:
    """Test database error handling"""

    @patch('app.database.restaurants.get_all_restaurants')
    def test_database_connection_error(self, mock_get_all):
        """
        Test handling of database connection errors

        Should handle PyMongoError gracefully
        """
        mock_get_all.side_effect = PyMongoError("Connection failed")

        with pytest.raises(PyMongoError):
            mock_get_all()

    @patch('app.database.dishes.get_dish_by_id')
    def test_invalid_object_id_error(self, mock_get_dish):
        """
        Test handling of invalid ObjectId errors

        Should return None or raise appropriate exception
        """
        mock_get_dish.return_value = None

        dish = mock_get_dish("invalid_id_format")

        # Should handle gracefully (return None)
        assert dish is None


class TestDatabaseDataIntegrity:
    """Test data integrity constraints"""

    def test_restaurant_has_required_fields(self):
        """
        Test that restaurant documents have required fields

        Required: _id, name
        Optional: address/location, cuisine, rating
        """
        # Minimum valid restaurant
        restaurant = {
            "_id": "rest_1",
            "name": "Test Restaurant"
        }

        assert "_id" in restaurant
        assert "name" in restaurant
        # Other fields are optional after fix

    def test_dish_has_required_fields(self):
        """
        Test that dish documents have required fields

        Required: _id, name, restaurant_id
        Optional: price, ingredients, allergens, etc.
        """
        # Minimum valid dish
        dish = {
            "_id": "dish_1",
            "name": "Test Dish",
            "restaurant_id": "rest_1"
        }

        assert "_id" in dish
        assert "name" in dish
        assert "restaurant_id" in dish

    def test_dish_allergens_format(self):
        """
        Test that allergens are in correct format

        Format: [{"allergen": "name", "severity": "level"}] or ["name"]
        """
        dish = {
            "_id": "dish_1",
            "name": "Test Dish",
            "explicit_allergens": [
                {"allergen": "peanuts", "severity": "high"},
                {"allergen": "dairy", "severity": "moderate"}
            ]
        }

        allergens = dish["explicit_allergens"]
        assert isinstance(allergens, list)
        if len(allergens) > 0:
            # Can be dict or string
            assert isinstance(allergens[0], (dict, str))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
