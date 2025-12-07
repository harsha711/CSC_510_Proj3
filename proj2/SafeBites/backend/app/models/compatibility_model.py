"""
Defines Pydantic models for AI-Powered Meal Compatibility Scoring.

This module provides structured schemas for multi-factor compatibility analysis
between dishes and user dietary profiles, including allergen safety, nutrition matching,
taste preferences, and dietary pattern alignment.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class SafetyLevel(str, Enum):
    """Safety assessment levels for allergen analysis"""
    SAFE = "SAFE"
    WARNING = "WARNING"
    UNSAFE = "UNSAFE"

class MatchLevel(str, Enum):
    """Match quality levels for compatibility factors"""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MODERATE = "MODERATE"
    POOR = "POOR"

class AllergenSafetyScore(BaseModel):
    """
    Allergen safety analysis for a dish.

    Attributes:
        score (int): Safety score 0-100 (100 = completely safe).
        level (SafetyLevel): Safety assessment (SAFE/WARNING/UNSAFE).
        detected_allergens (List[str]): Allergens found that match user allergies.
        reasoning (str): Explanation of safety assessment.
    """
    score: int = Field(..., ge=0, le=100)
    level: SafetyLevel
    detected_allergens: List[str] = Field(default_factory=list)
    reasoning: str

class NutritionMatchScore(BaseModel):
    """
    Nutrition matching analysis based on user health goals.

    Attributes:
        score (int): Nutrition match score 0-100.
        level (MatchLevel): Match quality assessment.
        matched_goals (List[str]): Health goals that align with dish nutrition.
        conflicts (List[str]): Health goals that conflict with dish nutrition.
        reasoning (str): Detailed explanation of nutrition analysis.
    """
    score: int = Field(..., ge=0, le=100)
    level: MatchLevel
    matched_goals: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    reasoning: str

class TastePreferenceScore(BaseModel):
    """
    Taste and cuisine preference matching analysis.

    Attributes:
        score (int): Taste match score 0-100.
        level (MatchLevel): Match quality assessment.
        matched_cuisines (List[str]): User's preferred cuisines found in dish.
        matched_tastes (List[str]): User's taste preferences found in dish.
        reasoning (str): Explanation of taste matching.
    """
    score: int = Field(..., ge=0, le=100)
    level: MatchLevel
    matched_cuisines: List[str] = Field(default_factory=list)
    matched_tastes: List[str] = Field(default_factory=list)
    reasoning: str

class DietaryPatternScore(BaseModel):
    """
    Dietary pattern alignment analysis (vegetarian, vegan, etc.).

    Attributes:
        score (int): Dietary pattern match score 0-100.
        level (MatchLevel): Match quality assessment.
        user_pattern (str): User's dietary pattern (e.g., "vegetarian").
        dish_category (str): Detected dish category (e.g., "contains meat").
        reasoning (str): Explanation of dietary pattern analysis.
    """
    score: int = Field(..., ge=0, le=100)
    level: MatchLevel
    user_pattern: str
    dish_category: str
    reasoning: str

class AlternativeSuggestion(BaseModel):
    """
    Alternative dish suggestion with higher compatibility.

    Attributes:
        dish_id (str): ID of suggested alternative dish.
        dish_name (str): Name of suggested dish.
        compatibility_score (int): Overall compatibility score of alternative.
        reason (str): Why this alternative is better.
    """
    dish_id: str
    dish_name: str
    compatibility_score: int
    reason: str

class CompatibilityScore(BaseModel):
    """
    Complete compatibility analysis for a dish.

    Attributes:
        dish_id (str): Unique identifier of the dish.
        dish_name (str): Name of the dish.
        overall_score (int): Overall compatibility score 0-100.
        allergen_safety (AllergenSafetyScore): Allergen safety analysis.
        nutrition_match (NutritionMatchScore): Nutrition matching analysis.
        taste_preference (TastePreferenceScore): Taste preference analysis.
        dietary_pattern (DietaryPatternScore): Dietary pattern analysis.
        recommendation (str): AI-generated recommendation text.
        alternative_suggestions (List[AlternativeSuggestion]): Better alternatives if score is low.
    """
    dish_id: str
    dish_name: str
    overall_score: int = Field(..., ge=0, le=100)
    allergen_safety: AllergenSafetyScore
    nutrition_match: NutritionMatchScore
    taste_preference: TastePreferenceScore
    dietary_pattern: DietaryPatternScore
    recommendation: str
    alternative_suggestions: List[AlternativeSuggestion] = Field(default_factory=list)

class CompatibilityResult(BaseModel):
    """
    Container for compatibility scores of multiple dishes.

    Attributes:
        scores (Dict[str, CompatibilityScore]): Map of dish_id to compatibility score.
    """
    scores: Dict[str, CompatibilityScore] = Field(default_factory=dict)
