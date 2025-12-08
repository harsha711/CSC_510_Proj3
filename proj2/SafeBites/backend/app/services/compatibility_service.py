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
    temperature=0.1,  # Lower temperature for faster, more consistent scoring
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

    # Collect all dishes
    all_dishes = []
    for query, dishes in menu_results.menu_results.items():
        all_dishes.extend(dishes)

    # PERFORMANCE OPTIMIZATION: Limit to first 7 dishes for faster response
    # Full compatibility scoring takes 30-40 seconds, limiting improves UX
    max_dishes_to_score = 7
    if len(all_dishes) > max_dishes_to_score:
        logger.info(f"Limiting compatibility scoring from {len(all_dishes)} to {max_dishes_to_score} dishes for performance")
        all_dishes = all_dishes[:max_dishes_to_score]

    logger.info(f"Calculating compatibility for {len(all_dishes)} dishes using batch processing")

    # OPTIMIZATION: Batch process all dishes in one LLM call
    scores = calculate_batch_compatibility(
        dishes=all_dishes,
        user_profile=user_profile
    )

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


def calculate_batch_compatibility(dishes: List, user_profile: dict) -> Dict[str, CompatibilityScore]:
    """
    OPTIMIZED: Calculate compatibility scores for multiple dishes in one LLM call.

    This is much faster than calling the LLM once per dish.

    Args:
        dishes: List of DishData objects to score.
        user_profile: User profile dictionary.

    Returns:
        Dict[str, CompatibilityScore]: Map of dish_id to CompatibilityScore.
    """
    if not dishes:
        return {}

    # Build compact dish list for LLM
    dishes_data = []
    for dish in dishes:
        dishes_data.append({
            "id": dish.dish_id,
            "name": dish.dish_name,
            "description": dish.description,
            "ingredients": dish.ingredients,
            "allergens": dish.allergens if dish.allergens else [],
            "nutrition": dish.nutrition_facts if dish.nutrition_facts else {},
            "price": dish.price
        })

    prompt = ChatPromptTemplate.from_template("""
You are analyzing multiple dishes for compatibility with a user's profile.

**User Profile:**
- Allergens to avoid: {allergens}
- Health Goals: {health_goals}
- Cuisine Preferences: {cuisine_preferences}
- Taste Preferences: {taste_preferences}
- Dietary Pattern: {dietary_pattern}

**Dishes to Analyze:**
{dishes_json}

**Task:**
For EACH dish, score it on these 4 factors (0-100):

1. **Allergen Safety**: Check if dish contains user allergens
   - 100 = Safe, 50-99 = Warning, 0-49 = Unsafe
   - Level: SAFE/WARNING/UNSAFE

2. **Nutrition Match**: How well nutrition aligns with health goals
   - If user has no health goals: give neutral 75 score with level GOOD
   - Higher = better match

3. **Taste Preference**: Match with cuisine/taste preferences
   - If user has no cuisine/taste preferences: give neutral 75 score with level GOOD
   - Always provide reasoning even if no preferences (e.g., "No specific preferences set")
   - Higher = better match

4. **Dietary Pattern**: Alignment with dietary pattern
   - Higher = better alignment

**Calculate Overall Score:**
- ALWAYS use weighted formula: (Allergen × 0.40) + (Nutrition × 0.25) + (Taste × 0.20) + (Dietary × 0.15)
- Example: If Allergen=100, Nutrition=75, Taste=50, Dietary=80 → Overall = (100×0.40)+(75×0.25)+(50×0.20)+(80×0.15) = 40+18.75+10+12 = 80.75 → 81
- IMPORTANT: Low taste score should NOT make overall score 0!
- Safety override: If allergen < 50, then overall must be < 50 (reduce overall score accordingly)

**Output Format (JSON array):**
[
  {{
    "dish_id": "id",
    "overall_score": <0-100>,
    "allergen_safety": {{
      "score": <0-100>,
      "level": "SAFE|WARNING|UNSAFE",
      "detected_allergens": [],
      "reasoning": "brief"
    }},
    "nutrition_match": {{
      "score": <0-100>,
      "level": "EXCELLENT|GOOD|MODERATE|POOR",
      "matched_goals": [],
      "conflicts": [],
      "reasoning": "brief"
    }},
    "taste_preference": {{
      "score": <0-100>,
      "level": "EXCELLENT|GOOD|MODERATE|POOR",
      "matched_cuisines": [],
      "matched_tastes": [],
      "reasoning": "brief"
    }},
    "dietary_pattern": {{
      "score": <0-100>,
      "level": "EXCELLENT|GOOD|MODERATE|POOR",
      "user_pattern": "{dietary_pattern}",
      "dish_category": "category",
      "reasoning": "brief"
    }},
    "recommendation": "1-2 sentence recommendation"
  }}
]

Be concise. No extra text. Safety first.
""")

    try:
        response = llm.invoke(prompt.format_messages(
            allergens=", ".join(user_profile["allergens"]) if user_profile["allergens"] else "None",
            health_goals=", ".join(user_profile["health_goals"]) if user_profile["health_goals"] else "None",
            cuisine_preferences=", ".join(user_profile["cuisine_preferences"]) if user_profile["cuisine_preferences"] else "None",
            taste_preferences=", ".join(user_profile["taste_preferences"]) if user_profile["taste_preferences"] else "None",
            dietary_pattern=user_profile["dietary_pattern"],
            dishes_json=json.dumps(dishes_data, indent=2)
        ))

        content = response.content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        scores_data = json.loads(content)

        # Convert to CompatibilityScore objects
        scores = {}
        dish_lookup = {d.dish_id: d for d in dishes}

        for score_data in scores_data:
            dish_id = score_data["dish_id"]
            dish = dish_lookup.get(dish_id)

            if not dish:
                continue

            # Convert all float scores to integers (LLM sometimes returns floats)
            def round_score(data):
                """Recursively round all score fields to integers."""
                if isinstance(data, dict):
                    return {k: round_score(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [round_score(item) for item in data]
                elif isinstance(data, float) and k == "score":
                    return round(data)
                else:
                    return data

            # Round scores in all sub-dictionaries
            score_data["overall_score"] = round(score_data["overall_score"])
            for key in ["allergen_safety", "nutrition_match", "taste_preference", "dietary_pattern"]:
                if key in score_data and "score" in score_data[key]:
                    score_data[key]["score"] = round(score_data[key]["score"])

                    # Ensure all required fields are present
                    if "reasoning" not in score_data[key]:
                        score_data[key]["reasoning"] = "No analysis provided"

            # ENFORCE weighted formula if LLM didn't follow it correctly
            # This prevents taste mismatch from causing 0 overall score
            allergen = score_data["allergen_safety"]["score"]
            nutrition = score_data["nutrition_match"]["score"]
            taste = score_data["taste_preference"]["score"]
            dietary = score_data["dietary_pattern"]["score"]

            calculated_score = round((allergen * 0.40) + (nutrition * 0.25) + (taste * 0.20) + (dietary * 0.15))

            # Apply safety override: if allergen < 50, overall must be < 50
            if allergen < 50 and calculated_score >= 50:
                calculated_score = min(calculated_score, 49)

            # Use calculated score if LLM gave 0 or very wrong score
            if score_data["overall_score"] == 0 or abs(score_data["overall_score"] - calculated_score) > 20:
                logger.warning(f"LLM gave overall_score={score_data['overall_score']}, but calculated={calculated_score}. Using calculated.")
                score_data["overall_score"] = calculated_score

            scores[dish_id] = CompatibilityScore(
                dish_id=dish_id,
                dish_name=dish.dish_name,
                overall_score=score_data["overall_score"],
                allergen_safety=AllergenSafetyScore(**score_data["allergen_safety"]),
                nutrition_match=NutritionMatchScore(**score_data["nutrition_match"]),
                taste_preference=TastePreferenceScore(**score_data["taste_preference"]),
                dietary_pattern=DietaryPatternScore(**score_data["dietary_pattern"]),
                recommendation=score_data["recommendation"],
                alternative_suggestions=[]  # Skip alternatives for speed
            )

            logger.debug(f"Scored {dish.dish_name}: {scores[dish_id].overall_score}/100")

        return scores

    except Exception as e:
        logger.error(f"Error in batch compatibility scoring: {e}")
        # Fallback to individual scoring if batch fails
        logger.warning("Batch scoring failed, falling back to individual scoring")
        scores = {}
        for dish in dishes:
            scores[dish.dish_id] = create_default_compatibility_score(dish)
        return scores


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
