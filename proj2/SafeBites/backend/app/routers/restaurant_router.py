from fastapi import APIRouter,HTTPException, Depends
from bson import ObjectId
from app.models.restaurant_model import RestaurantCreate, RestaurantUpdate, RestaurantBase, RestaurantInDB
from app.services.restaurant_service import restarant_service

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/",response_model=RestaurantInDB)
def create_restaurant(restaurant: RestaurantCreate):
    """
        Create a new restaurant entry in the database. If allergen information is not provided, 
        it will be inferred using an external service.

        Args:
            restaurant(RestaurantCreate): The restaurant data provided by the client.
        
        Returns:
            RestaurantInDB: The created restaurant entry with its unique ID.
    """
    return restarant_service.create_restaurant(restaurant)

@router.get("/",response_model=list[RestaurantInDB])
def list_restaurants():
    """
        Retrieve a list of all restaurants in the database.
        Args:
            None
        
        Returns:
            list[RestaurantInDB]: A list of all restaurant entries in the database.
    """
    return restarant_service.list_restaurants()

@router.get("/{restaurant_id}",response_model=RestaurantInDB)
def get_restaurant(restaurant_id:str):
    """
        Retrieve a specific restaurant by its ID.

        Args:
            restaurant_id(str): The unique identifier of the restaurant.
        
        Returns:
            RestaurantInDB: The restaurant entry corresponding to the provided ID.
        
        Raises:
            HTTPException(404): If no restaurant with the given ID is found.
    """
    return restarant_service.get_restaurant(restaurant_id)

@router.patch("/{restaurant_id}",response_model=RestaurantInDB)
def update_restaurant(restaurant_id:str,updates:RestaurantUpdate):
    """
        Update an existing restaurant's information.

        Args:
            restaurant_id(str): The unique identifier of the restaurant to be updated.
            updates(RestaurantUpdate): The fields to be updated with their new values.

        Returns:
            RestaurantInDB: The updated restaurant entry.
        Raises:
            HTTPException(404): If no restaurant with the given ID is found.
    """
    return restarant_service.update_restaurant(restaurant_id,updates)

@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id:str):
    """
        Delete a restaurant from the database.

        Args:
            restaurant_id(str): The unique identifier of the restaurant to be deleted.

        Returns:
            None

        Raises:
            HTTPException(404): If no restaurant with the given ID is found.
    """
    return restarant_service.delete_restaurant(restaurant_id)