"""
AI-Powered Meal Compatibility Scoring Service

This service provides multi-factor compatibility analysis between dishes and user profiles,
including allergen safety, nutrition matching, taste preferences, and dietary pattern alignment.
"""
import logging
import json
from typing import List, Dict, Optional
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from app.models.compatibility_model import (
    CompatibilityScore, CompatibilityResult,
    AllergenSafetyScore, NutritionMatchScore, TastePreferenceScore, DietaryPatternScore,
    AlternativeSuggestion, SafetyLevel, MatchLevel
)
from app.utils.llm_tracker import LLMUsageTracker

logger = logging.getLogger(__name__)
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,  # Lower temperature for more consistent scoring
    openai_api_key=os.getenv("OPENAI_KEY"),
    callbacks=[LLMUsageTracker()]
)

def calculate_compatibility_scores(state) -> dict:
    """
    Calculate compatibility scores for all dishes in the menu results.

    This is the main entry point for the compatibility scoring pipeline.
    It analyzes each dish against the user's profile and generates detailed
    compatibility scores with breakdowns.

    Args:
        state: LangGraph state containing menu_results and context with user profile.

    Returns:
        dict: {"compatibility_results": CompatibilityResult}
    """
    logger.info("Starting compatibility score calculation")

    # Extract menu results
    menu_results = state.menu_results
    if not menu_results or not menu_results.menu_results:
        logger.debug("No menu results to score")
        return {"compatibility_results": CompatibilityResult(scores={})}

    # Extract user profile from context
    user_profile = extract_user_profile(state.context)
    if not user_profile:
        logger.warning("No user profile found in context, skipping compatibility scoring")
        return {"compatibility_results": CompatibilityResult(scores={})}

    logger.info(f"Calculating compatibility for {len(menu_results.menu_results)} dishes")

    scores = {}
    all_dishes = []

    # Collect all dishes for alternative suggestions
    for query, dishes in menu_results.menu_results.items():
        all_dishes.extend(dishes)

    # Calculate score for each dish
    for query, dishes in menu_results.menu_results.items():
        for dish in dishes:
            try:
                compatibility = calculate_dish_compatibility(
                    dish=dish,
                    user_profile=user_profile,
                    all_dishes=all_dishes
                )
                scores[dish.dish_id] = compatibility
                logger.debug(f"Scored {dish.dish_name}: {compatibility.overall_score}/100")
            except Exception as e:
                logger.error(f"Error calculating compatibility for {dish.dish_name}: {e}")

    return {"compatibility_results": CompatibilityResult(scores=scores)}


def extract_user_profile(context: List[dict]) -> Optional[dict]:
    """
    Extract user profile information from context.

    Args:
        context: List of context items from state.

    Returns:
        dict: User profile with allergens, health_goals, cuisine_preferences, etc.
              None if no user profile found.
    """
    profile = {
        "allergens": [],
        "health_goals": [],
        "cuisine_preferences": [],
        "taste_preferences": [],
        "dietary_pattern": "omnivore"
    }

    if not context:
        return None

    for ctx_item in context:
        # Extract allergens
        if "user_allergens" in ctx_item:
            profile["allergens"] = ctx_item.get("user_allergens", [])

        # Extract other profile fields
        if "user_profile" in ctx_item:
            user_data = ctx_item["user_profile"]
            profile["health_goals"] = user_data.get("health_goals", [])
            profile["cuisine_preferences"] = user_data.get("cuisine_preferences", [])
            profile["taste_preferences"] = user_data.get("taste_preferences", [])
            profile["dietary_pattern"] = user_data.get("dietary_pattern", "omnivore")

    # Only return profile if we have at least one piece of user data
    if profile["allergens"] or profile["health_goals"] or profile["cuisine_preferences"]:
        return profile

    return None


def calculate_dish_compatibility(dish, user_profile: dict, all_dishes: List) -> CompatibilityScore:
    """
    Calculate complete compatibility score for a single dish.

    Uses LLM to analyze multiple factors:
    - Allergen safety
    - Nutrition matching with health goals
    - Taste and cuisine preferences
    - Dietary pattern alignment

    Args:
        dish: DishData object with dish information.
        user_profile: User profile dictionary.
        all_dishes: All available dishes for alternative suggestions.

    Returns:
        CompatibilityScore: Complete compatibility analysis.
    """
    prompt = ChatPromptTemplate.from_template("""
You are an AI nutritionist and food safety expert analyzing dish compatibility for a user.

**User Profile:**
- Allergens to avoid: {allergens}
- Health Goals: {health_goals}
- Cuisine Preferences: {cuisine_preferences}
- Taste Preferences: {taste_preferences}
- Dietary Pattern: {dietary_pattern}

**Dish to Analyze:**
- Name: {dish_name}
- Description: {description}
- Ingredients: {ingredients}
- Allergens: {dish_allergens}
- Nutrition Facts: {nutrition}
- Price: ${price}

**Your Task:**
Analyze this dish across 4 dimensions and provide scores (0-100) for each:

1. **Allergen Safety (0-100)**:
   - 100 = No allergens detected, completely safe
   - 50-99 = Trace amounts or unclear allergens
   - 0-49 = Contains user allergens, unsafe
   - Determine safety level: SAFE, WARNING, or UNSAFE
   - List any detected allergens that match user allergies

2. **Nutrition Match (0-100)**:
   - Analyze dish nutrition against user health goals
   - Higher score = better alignment with health goals
   - List matched goals and conflicts
   - Consider calories, protein, carbs, fat, etc.

3. **Taste Preference (0-100)**:
   - Match dish cuisine and taste profile with user preferences
   - Higher score = better match
   - List matched cuisines and tastes

4. **Dietary Pattern (0-100)**:
   - Analyze alignment with user's dietary pattern (vegetarian, vegan, etc.)
   - 100 = Perfect alignment
   - Lower score = Contains ingredients outside dietary pattern
   - Determine dish category (e.g., "contains meat", "fully vegan")

**Calculate Overall Score:**
- Weighted average: Allergen Safety (40%) + Nutrition (25%) + Taste (20%) + Dietary (15%)
- If allergen safety < 50, overall score must be < 50 (safety override)

**Provide AI Recommendation:**
- Short, friendly recommendation about the dish
- If score < 70, suggest why user might want to consider alternatives
- If score >= 70, highlight what makes this a good match

**Output Format (JSON only):**
{{
  "allergen_safety": {{
    "score": <0-100>,
    "level": "SAFE" | "WARNING" | "UNSAFE",
    "detected_allergens": [list of allergens from user's list found in dish],
    "reasoning": "explanation"
  }},
  "nutrition_match": {{
    "score": <0-100>,
    "level": "EXCELLENT" | "GOOD" | "MODERATE" | "POOR",
    "matched_goals": [health goals that align],
    "conflicts": [health goals that conflict],
    "reasoning": "explanation"
  }},
  "taste_preference": {{
    "score": <0-100>,
    "level": "EXCELLENT" | "GOOD" | "MODERATE" | "POOR",
    "matched_cuisines": [matched cuisines],
    "matched_tastes": [matched taste preferences],
    "reasoning": "explanation"
  }},
  "dietary_pattern": {{
    "score": <0-100>,
    "level": "EXCELLENT" | "GOOD" | "MODERATE" | "POOR",
    "user_pattern": "{dietary_pattern}",
    "dish_category": "category of dish",
    "reasoning": "explanation"
  }},
  "overall_score": <0-100>,
  "recommendation": "your friendly recommendation"
}}

Remember:
- Be strict with allergen safety - user safety is paramount
- Be objective with nutrition - base on actual nutritional data
- Be helpful with recommendations - guide user to safe, healthy choices
- If user has no health goals/preferences, give neutral scores (70-80) for those factors
""")

    try:
        response = llm.invoke(prompt.format_messages(
            allergens=", ".join(user_profile["allergens"]) if user_profile["allergens"] else "None",
            health_goals=", ".join(user_profile["health_goals"]) if user_profile["health_goals"] else "None specified",
            cuisine_preferences=", ".join(user_profile["cuisine_preferences"]) if user_profile["cuisine_preferences"] else "None specified",
            taste_preferences=", ".join(user_profile["taste_preferences"]) if user_profile["taste_preferences"] else "None specified",
            dietary_pattern=user_profile["dietary_pattern"],
            dish_name=dish.dish_name,
            description=dish.description,
            ingredients=", ".join(dish.ingredients),
            dish_allergens=", ".join(dish.allergens) if dish.allergens else "None listed",
            nutrition=json.dumps(dish.nutrition_facts) if dish.nutrition_facts else "Not available",
            price=dish.price
        ))

        # Parse LLM response
        content = response.content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        data = json.loads(content)

        # Build CompatibilityScore object
        compatibility = CompatibilityScore(
            dish_id=dish.dish_id,
            dish_name=dish.dish_name,
            overall_score=data["overall_score"],
            allergen_safety=AllergenSafetyScore(**data["allergen_safety"]),
            nutrition_match=NutritionMatchScore(**data["nutrition_match"]),
            taste_preference=TastePreferenceScore(**data["taste_preference"]),
            dietary_pattern=DietaryPatternScore(**data["dietary_pattern"]),
            recommendation=data["recommendation"],
            alternative_suggestions=[]
        )

        # If score is low, find alternatives
        if compatibility.overall_score < 70:
            compatibility.alternative_suggestions = find_alternative_dishes(
                current_dish=dish,
                all_dishes=all_dishes,
                user_profile=user_profile
            )

        return compatibility

    except Exception as e:
        logger.error(f"Error in calculate_dish_compatibility: {e}")
        # Return default low score on error
        return create_default_compatibility_score(dish)


def find_alternative_dishes(
    current_dish,
    all_dishes: List,
    user_profile: dict,
    max_alternatives: int = 2
) -> List[AlternativeSuggestion]:
    """
    Find better alternative dishes when current dish has low compatibility.

    Uses LLM to intelligently suggest similar dishes with better compatibility.

    Args:
        current_dish: The low-scoring dish.
        all_dishes: List of all available dishes.
        user_profile: User profile for matching.
        max_alternatives: Maximum number of alternatives to suggest.

    Returns:
        List[AlternativeSuggestion]: List of better alternatives.
    """
    if len(all_dishes) <= 1:
        return []

    # Filter out current dish and create simple dish list
    other_dishes = [
        {
            "dish_id": d.dish_id,
            "name": d.dish_name,
            "description": d.description,
            "allergens": d.allergens if hasattr(d, 'allergens') else []
        }
        for d in all_dishes
        if d.dish_id != current_dish.dish_id
    ]

    if not other_dishes:
        return []

    prompt = ChatPromptTemplate.from_template("""
You are suggesting alternative dishes for a user.

**Current Dish (low compatibility):** {current_dish}

**User Profile:**
- Allergens to avoid: {allergens}
- Health Goals: {health_goals}
- Dietary Pattern: {dietary_pattern}

**Available Alternative Dishes:**
{alternatives}

**Task:**
Suggest up to {max_alternatives} better alternatives that:
1. Are SAFE (no user allergens)
2. Better match health goals
3. Align with dietary pattern
4. Are similar in type/category to current dish (if possible)

**Output Format (JSON array only):**
[
  {{
    "dish_id": "id",
    "dish_name": "name",
    "compatibility_score": <estimated 0-100>,
    "reason": "why this is better"
  }}
]

If no good alternatives exist, return empty array [].
""")

    try:
        response = llm.invoke(prompt.format_messages(
            current_dish=current_dish.dish_name,
            allergens=", ".join(user_profile["allergens"]) if user_profile["allergens"] else "None",
            health_goals=", ".join(user_profile["health_goals"]) if user_profile["health_goals"] else "None",
            dietary_pattern=user_profile["dietary_pattern"],
            alternatives=json.dumps(other_dishes[:10]),  # Limit to 10 for context size
            max_alternatives=max_alternatives
        ))

        content = response.content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        suggestions_data = json.loads(content)

        return [AlternativeSuggestion(**s) for s in suggestions_data[:max_alternatives]]

    except Exception as e:
        logger.error(f"Error finding alternatives: {e}")
        return []


def create_default_compatibility_score(dish) -> CompatibilityScore:
    """
    Create a default compatibility score when LLM analysis fails.

    Args:
        dish: Dish object.

    Returns:
        CompatibilityScore: Default safe score.
    """
    return CompatibilityScore(
        dish_id=dish.dish_id,
        dish_name=dish.dish_name,
        overall_score=50,
        allergen_safety=AllergenSafetyScore(
            score=50,
            level=SafetyLevel.WARNING,
            detected_allergens=[],
            reasoning="Unable to analyze allergen safety"
        ),
        nutrition_match=NutritionMatchScore(
            score=50,
            level=MatchLevel.MODERATE,
            matched_goals=[],
            conflicts=[],
            reasoning="Unable to analyze nutrition"
        ),
        taste_preference=TastePreferenceScore(
            score=50,
            level=MatchLevel.MODERATE,
            matched_cuisines=[],
            matched_tastes=[],
            reasoning="Unable to analyze taste preferences"
        ),
        dietary_pattern=DietaryPatternScore(
            score=50,
            level=MatchLevel.MODERATE,
            user_pattern="unknown",
            dish_category="unknown",
            reasoning="Unable to analyze dietary pattern"
        ),
        recommendation="Unable to generate compatibility score. Please review dish details manually.",
        alternative_suggestions=[]
    )
