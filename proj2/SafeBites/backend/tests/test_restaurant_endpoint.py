"""
Test Suite for Restaurant Endpoint

Tests the fix for:
1. Restaurant endpoint 500 error
2. Field name mapping (address vs location)
3. RestaurantInDB Pydantic model
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.restaurant_model import RestaurantInDB, RestaurantBase
from pydantic import ValidationError


class TestRestaurantModelFix:
    """Test that RestaurantInDB model handles address/location correctly"""

    def test_restaurant_with_address_field(self):
        """
        Test that RestaurantInDB accepts 'address' field from database

        Before fix: RestaurantInDB inherited from RestaurantBase which required 'location'
        Database has: 'address'
        Result: 500 error - "Field required [type=missing, input_value={'_id': 'rest_1'...}]"

        After fix: RestaurantInDB uses Optional[str] with alias="address"
        """
        # Mock database document
        db_document = {
            "_id": "rest_1",
            "name": "Test Restaurant",
            "address": "123 Main St",
            "cuisine": ["Italian"],
            "rating": 4.5
        }

        # Should create model without error
        restaurant = RestaurantInDB(**db_document)

        assert restaurant.id == "rest_1"
        assert restaurant.name == "Test Restaurant"
        assert restaurant.address == "123 Main St"
        # location is aliased from address
        assert restaurant.location == "123 Main St"

    def test_restaurant_with_location_field(self):
        """Test that RestaurantInDB also accepts 'location' field"""
        db_document = {
            "_id": "rest_2",
            "name": "Test Restaurant 2",
            "location": "456 Oak Ave",
            "cuisine": ["Mexican"],
            "rating": 4.0
        }

        # Should create model without error (populate_by_name allows both)
        restaurant = RestaurantInDB(**db_document)

        assert restaurant.id == "rest_2"
        assert restaurant.name == "Test Restaurant 2"
        assert restaurant.location == "456 Oak Ave"

    def test_restaurant_without_location_or_address(self):
        """Test that location/address are optional"""
        db_document = {
            "_id": "rest_3",
            "name": "Test Restaurant 3",
            "cuisine": ["Japanese"]
        }

        # Should create model without error (fields are optional)
        restaurant = RestaurantInDB(**db_document)

        assert restaurant.id == "rest_3"
        assert restaurant.name == "Test Restaurant 3"
        assert restaurant.location is None
        assert restaurant.address is None

    def test_restaurant_model_not_inheriting_from_base(self):
        """
        Test that RestaurantInDB is independent from RestaurantBase

        The fix: Changed from inheritance to standalone model to avoid
        required field conflicts
        """
        # RestaurantInDB should have its own fields, not inherit required ones
        db_document = {
            "_id": "rest_4",
            "name": "Test Restaurant 4"
            # Missing location - should still work
        }

        try:
            restaurant = RestaurantInDB(**db_document)
            assert True, "Should create model without location"
        except ValidationError as e:
            pytest.fail(f"Should not require location field: {e}")


class TestRestaurantFieldMapping:
    """Test field mapping between database and model"""

    def test_id_aliased_from_underscore_id(self):
        """Test that 'id' field is aliased from '_id' in database"""
        db_document = {
            "_id": "rest_5",
            "name": "Test Restaurant 5",
            "address": "789 Pine Rd"
        }

        restaurant = RestaurantInDB(**db_document)

        # Should map _id -> id
        assert restaurant.id == "rest_5"
        assert hasattr(restaurant, 'id')

    def test_location_aliased_from_address(self):
        """Test that 'location' is aliased from 'address' in database"""
        db_document = {
            "_id": "rest_6",
            "name": "Test Restaurant 6",
            "address": "999 Elm St"
        }

        restaurant = RestaurantInDB(**db_document)

        # Should map address -> location
        assert restaurant.location == "999 Elm St"
        assert restaurant.address == "999 Elm St"

    def test_optional_fields_have_defaults(self):
        """Test that optional fields have appropriate defaults"""
        db_document = {
            "_id": "rest_7",
            "name": "Test Restaurant 7"
        }

        restaurant = RestaurantInDB(**db_document)

        # Optional fields should have defaults
        assert restaurant.location is None
        assert restaurant.address is None
        assert restaurant.cuisine is None
        assert restaurant.rating == 0.0  # Default rating


class TestRestaurantEndpointCompatibility:
    """Test backward compatibility"""

    def test_model_accepts_both_field_names(self):
        """
        Test that model accepts both 'address' and 'location'

        This ensures backward compatibility with different data sources
        """
        # With address
        doc1 = {
            "_id": "rest_8",
            "name": "Restaurant 8",
            "address": "Address St"
        }
        r1 = RestaurantInDB(**doc1)
        assert r1.location == "Address St"

        # With location
        doc2 = {
            "_id": "rest_9",
            "name": "Restaurant 9",
            "location": "Location Ave"
        }
        r2 = RestaurantInDB(**doc2)
        assert r2.location == "Location Ave"

    def test_populate_by_name_config(self):
        """
        Test that populate_by_name config is set

        This allows both field name and alias to work
        """
        # Check Config class exists and has populate_by_name
        assert hasattr(RestaurantInDB, 'Config')
        assert hasattr(RestaurantInDB.Config, 'populate_by_name')
        assert RestaurantInDB.Config.populate_by_name is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
