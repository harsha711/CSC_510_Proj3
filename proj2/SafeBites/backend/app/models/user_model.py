"""
Defines Pydantic schemas for user management in the SafeBites backend.

These schemas are used for creating, updating, and retrieving user data.
They include fields for user identification, authentication credentials,
allergen preferences, health goals, dietary preferences, and dietary patterns
for AI-powered meal compatibility scoring.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict

class UserCreate(BaseModel):
    """
    Represents the schema for creating a new user account.

    Attributes:
        name (str): The full name of the user.
        username (str): Unique username for authentication or identification.
        password (str): User's password (must be between 3 and 72 characters).
        allergen_preferences (List[str]): List of allergens the user wishes to avoid.
        health_goals (List[str]): User's health/dietary goals (e.g., "low-carb", "high-protein", "weight-loss").
        cuisine_preferences (List[str]): Preferred cuisines (e.g., "Italian", "Mexican", "Indian").
        taste_preferences (List[str]): Taste preferences (e.g., "spicy", "sweet", "savory").
        dietary_pattern (str): Primary dietary pattern (e.g., "vegetarian", "vegan", "pescatarian", "omnivore").
    """
    name: str
    username: str
    # Limit password to 3–72 characters
    password: str = Field(..., min_length=3, max_length=72)
    allergen_preferences: List[str] = Field(default_factory=list)
    health_goals: List[str] = Field(default_factory=list)
    cuisine_preferences: List[str] = Field(default_factory=list)
    taste_preferences: List[str] = Field(default_factory=list)
    dietary_pattern: str = Field(default="omnivore")

class UserUpdate(BaseModel):
    """
    Represents the schema for updating a user account.

    Attributes:
        name (str): The full name of the user.
        allergen_preferences (List[str]): List of allergens the user wishes to avoid.
        health_goals (List[str]): User's health/dietary goals.
        cuisine_preferences (List[str]): Preferred cuisines.
        taste_preferences (List[str]): Taste preferences.
        dietary_pattern (str): Primary dietary pattern.
    """
    name: Optional[str] = None
    allergen_preferences: Optional[List[str]] = None
    health_goals: Optional[List[str]] = None
    cuisine_preferences: Optional[List[str]] = None
    taste_preferences: Optional[List[str]] = None
    dietary_pattern: Optional[str] = None

class UserOut(BaseModel):
    """
    Represents the output schema returned when fetching user information.

    Attributes:
        id (str): Unique identifier of the user (aliased as `_id` in the database).
        name (str): The user's full name.
        username (str): The user's username.
        allergen_preferences (List[str]): List of allergens the user avoids.
        health_goals (List[str]): User's health/dietary goals.
        cuisine_preferences (List[str]): Preferred cuisines.
        taste_preferences (List[str]): Taste preferences.
        dietary_pattern (str): Primary dietary pattern.
    """
    id: str = Field(..., alias="_id")
    name: str
    username: str
    allergen_preferences: List[str] = []
    health_goals: List[str] = []
    cuisine_preferences: List[str] = []
    taste_preferences: List[str] = []
    dietary_pattern: str = "omnivore"
