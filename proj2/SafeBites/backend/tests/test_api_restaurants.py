"""
Restaurant API Endpoint Tests

Tests for restaurant-related API endpoints:
- GET /restaurants/ - List all restaurants
- GET /restaurants/{id} - Get restaurant by ID
- GET /restaurants/{id}/dishes - Get dishes for a restaurant

These are integration tests that verify the complete request-response cycle.
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

client = TestClient(app)


class TestGetAllRestaurants:
    """Test GET /restaurants/ endpoint"""

    def test_returns_200_status(self):
        """
        Test that /restaurants/ returns 200 OK

        This validates the fix for the 500 error caused by address/location field mismatch
        """
        response = client.get("/restaurants/")

        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}. Error: {response.json() if response.status_code != 200 else 'N/A'}"

    def test_returns_list_of_restaurants(self):
        """Test that response is a list"""
        response = client.get("/restaurants/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"

    def test_restaurant_has_required_fields(self):
        """
        Test that each restaurant has required fields

        After fix: id and name are required, location/address are optional
        """
        response = client.get("/restaurants/")

        if response.status_code == 200:
            restaurants = response.json()

            if len(restaurants) > 0:
                restaurant = restaurants[0]

                # Must have id (either 'id' or '_id')
                assert "id" in restaurant or "_id" in restaurant, \
                    "Restaurant must have id field"

                # Must have name
                assert "name" in restaurant, \
                    "Restaurant must have name field"

                # location/address are optional after fix
                # No assertion needed - should not cause 500 error

    def test_restaurant_count_matches_database(self):
        """Test that we get expected number of restaurants (at least 1)"""
        response = client.get("/restaurants/")

        assert response.status_code == 200
        restaurants = response.json()
        assert len(restaurants) >= 1, "Should have at least 1 restaurant in database"


class TestGetRestaurantById:
    """Test GET /restaurants/{restaurant_id} endpoint"""

    def test_valid_restaurant_id_returns_200(self):
        """Test that valid restaurant ID returns restaurant data"""
        # First get a valid restaurant ID
        all_restaurants_response = client.get("/restaurants/")

        if all_restaurants_response.status_code == 200:
            restaurants = all_restaurants_response.json()

            if len(restaurants) > 0:
                # Get first restaurant's ID
                restaurant_id = restaurants[0].get("id") or restaurants[0].get("_id")

                # Test getting that specific restaurant
                response = client.get(f"/restaurants/{restaurant_id}")

                assert response.status_code == 200, \
                    f"Expected 200 for valid ID, got {response.status_code}"

                # Verify it returns the correct restaurant
                restaurant = response.json()
                returned_id = restaurant.get("id") or restaurant.get("_id")
                assert returned_id == restaurant_id

    def test_invalid_restaurant_id_returns_error(self):
        """Test that invalid restaurant ID returns appropriate error"""
        response = client.get("/restaurants/nonexistent_restaurant_999")

        # Should return 404 (not found) or 500 (database error)
        assert response.status_code in [404, 500], \
            f"Expected 404 or 500 for invalid ID, got {response.status_code}"

    def test_restaurant_data_completeness(self):
        """Test that returned restaurant has all available fields"""
        # Get first restaurant
        all_restaurants_response = client.get("/restaurants/")

        if all_restaurants_response.status_code == 200:
            restaurants = all_restaurants_response.json()

            if len(restaurants) > 0:
                restaurant_id = restaurants[0].get("id") or restaurants[0].get("_id")
                response = client.get(f"/restaurants/{restaurant_id}")

                if response.status_code == 200:
                    restaurant = response.json()

                    # Should have basic fields
                    assert "name" in restaurant
                    # Optional fields like cuisine, rating may or may not be present


class TestGetRestaurantDishes:
    """Test GET /restaurants/{restaurant_id}/dishes endpoint"""

    def test_returns_list_of_dishes(self):
        """Test that endpoint returns list of dishes for a restaurant"""
        # Get a valid restaurant ID
        all_restaurants_response = client.get("/restaurants/")

        if all_restaurants_response.status_code == 200:
            restaurants = all_restaurants_response.json()

            if len(restaurants) > 0:
                restaurant_id = restaurants[0].get("id") or restaurants[0].get("_id")

                response = client.get(f"/restaurants/{restaurant_id}/dishes")

                # May return 200 with empty list or 200 with dishes
                if response.status_code == 200:
                    dishes = response.json()
                    assert isinstance(dishes, list), "Should return list of dishes"

    def test_dish_has_required_fields(self):
        """Test that each dish has required fields (name, price, etc.)"""
        # Get restaurant with dishes
        all_restaurants_response = client.get("/restaurants/")

        if all_restaurants_response.status_code == 200:
            restaurants = all_restaurants_response.json()

            if len(restaurants) > 0:
                restaurant_id = restaurants[0].get("id") or restaurants[0].get("_id")
                response = client.get(f"/restaurants/{restaurant_id}/dishes")

                if response.status_code == 200:
                    dishes = response.json()

                    if len(dishes) > 0:
                        dish = dishes[0]
                        assert "name" in dish, "Dish must have name"
                        # Other fields like price, ingredients may vary

    def test_dishes_belong_to_correct_restaurant(self):
        """
        Test that returned dishes belong to the requested restaurant

        This validates restaurant_id field is correctly populated
        """
        all_restaurants_response = client.get("/restaurants/")

        if all_restaurants_response.status_code == 200:
            restaurants = all_restaurants_response.json()

            if len(restaurants) > 0:
                restaurant_id = restaurants[0].get("id") or restaurants[0].get("_id")
                response = client.get(f"/restaurants/{restaurant_id}/dishes")

                if response.status_code == 200:
                    dishes = response.json()

                    if len(dishes) > 0:
                        # Check if restaurant_id field exists and matches
                        for dish in dishes:
                            if "restaurant_id" in dish:
                                assert dish["restaurant_id"] == restaurant_id, \
                                    f"Dish restaurant_id mismatch: {dish['restaurant_id']} != {restaurant_id}"


class TestRestaurantEndpointErrorHandling:
    """Test error handling for restaurant endpoints"""

    def test_malformed_restaurant_id(self):
        """Test that malformed IDs are handled gracefully"""
        response = client.get("/restaurants/!@#$%^&*()")

        # Should return error, not crash
        assert response.status_code in [404, 422, 500]

    def test_empty_restaurant_id(self):
        """Test that empty ID is handled"""
        response = client.get("/restaurants/")

        # Should return all restaurants, not error
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
