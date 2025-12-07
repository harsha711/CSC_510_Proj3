# AI-Powered Meal Compatibility Scoring - Implementation Guide

## Overview

This document describes the complete implementation of the **AI-Powered Meal Compatibility Score** feature in SafeBites. This feature provides real-time, multi-factor compatibility analysis between dishes and user dietary profiles.

## Feature Description

The compatibility scoring system analyzes dishes across 4 dimensions:

1. **Allergen Safety (40% weight)** - Checks for user allergens in dish ingredients
2. **Nutrition Match (25% weight)** - Aligns dish nutrition with health goals (low-carb, high-protein, etc.)
3. **Taste Preference (20% weight)** - Matches cuisine and taste preferences
4. **Dietary Pattern (15% weight)** - Aligns with dietary pattern (vegetarian, vegan, pescatarian, omnivore)

### Example Output

```
Dish: "Spicy Arrabbiata Pasta"
Overall Compatibility Score: 75/100

Breakdown:
✅ Allergen Safety: 100/100 (SAFE - no allergens detected)
⚠️  Nutrition Match: 45/100 (MODERATE - high carb conflicts with low-carb goal)
✅ Taste Preference: 95/100 (EXCELLENT - matches spicy + Italian preferences)
⚠️  Dietary Pattern: 60/100 (MODERATE - contains meat, user mostly vegetarian)

AI Recommendation: "This dish matches your taste preferences well, but it's high in carbs which may conflict with your low-carb goal. Consider our vegetarian Spicy Penne Arrabbiata instead (92% match)"

Alternative Suggestions:
1. Vegetarian Spicy Penne Arrabbiata (92/100) - Better aligns with dietary pattern
2. Grilled Chicken Salad (88/100) - Lower carbs, matches health goals
```

---

## Implementation Details

### 1. Database Schema Extensions

#### User Model (`backend/app/models/user_model.py`)

**New Fields Added:**
```python
class UserCreate(BaseModel):
    # Existing fields
    name: str
    username: str
    password: str
    allergen_preferences: List[str] = []

    # NEW FIELDS for compatibility scoring
    health_goals: List[str] = []              # ["low-carb", "high-protein", "weight-loss"]
    cuisine_preferences: List[str] = []        # ["Italian", "Mexican", "Indian"]
    taste_preferences: List[str] = []          # ["spicy", "sweet", "savory"]
    dietary_pattern: str = "omnivore"          # "vegetarian", "vegan", "pescatarian", "omnivore"
```

**Why These Fields:**
- `health_goals`: Allows nutrition matching (e.g., "low-carb" → avoid high-carb dishes)
- `cuisine_preferences`: Enables taste preference matching
- `taste_preferences`: Matches flavor profiles (spicy, sweet, savory)
- `dietary_pattern`: Ensures dishes align with dietary restrictions

---

### 2. Compatibility Score Models

#### New File: `backend/app/models/compatibility_model.py`

**Key Models:**

```python
class AllergenSafetyScore(BaseModel):
    score: int                        # 0-100
    level: SafetyLevel                # SAFE/WARNING/UNSAFE
    detected_allergens: List[str]     # Allergens found that match user allergies
    reasoning: str                    # Explanation

class NutritionMatchScore(BaseModel):
    score: int                        # 0-100
    level: MatchLevel                 # EXCELLENT/GOOD/MODERATE/POOR
    matched_goals: List[str]          # Health goals that align
    conflicts: List[str]              # Health goals that conflict
    reasoning: str

class TastePreferenceScore(BaseModel):
    score: int                        # 0-100
    level: MatchLevel
    matched_cuisines: List[str]
    matched_tastes: List[str]
    reasoning: str

class DietaryPatternScore(BaseModel):
    score: int                        # 0-100
    level: MatchLevel
    user_pattern: str                 # User's dietary pattern
    dish_category: str                # Detected dish category
    reasoning: str

class CompatibilityScore(BaseModel):
    dish_id: str
    dish_name: str
    overall_score: int                # Weighted average
    allergen_safety: AllergenSafetyScore
    nutrition_match: NutritionMatchScore
    taste_preference: TastePreferenceScore
    dietary_pattern: DietaryPatternScore
    recommendation: str               # AI-generated recommendation
    alternative_suggestions: List[AlternativeSuggestion]
```

---

### 3. Compatibility Scoring Service

#### New File: `backend/app/services/compatibility_service.py`

**Main Functions:**

##### `calculate_compatibility_scores(state)`
- **Entry point** for LangGraph node
- Extracts user profile from context
- Scores all dishes in menu_results
- Returns `{"compatibility_results": CompatibilityResult}`

##### `calculate_dish_compatibility(dish, user_profile, all_dishes)`
- Uses LLM (gpt-4o-mini) to analyze dish against user profile
- Generates scores for all 4 dimensions
- Calculates weighted overall score
- **Safety Override**: If allergen safety < 50, overall score must be < 50

**LLM Prompt Strategy:**
```
Analyze dish across 4 dimensions:
1. Allergen Safety (0-100)
2. Nutrition Match (0-100)
3. Taste Preference (0-100)
4. Dietary Pattern (0-100)

Overall Score = Allergen(40%) + Nutrition(25%) + Taste(20%) + Dietary(15%)
Safety Override: If allergen < 50, overall < 50
```

##### `find_alternative_dishes(current_dish, all_dishes, user_profile)`
- Triggered when overall score < 70
- Uses LLM to suggest up to 2 better alternatives
- Filters for safer, more compatible dishes

---

### 4. State Management Updates

#### `backend/app/services/state_service.py`

**Updated `rebuild_context()` function:**

```python
# OLD: Only fetched allergen preferences
if user_id:
    allergen_prefs = user_doc.get("allergen_preferences", [])
    context.append({"user_allergens": allergen_prefs})

# NEW: Fetches complete user profile
if user_id:
    # Add allergen preferences
    allergen_prefs = user_doc.get("allergen_preferences", [])
    context.append({"user_allergens": allergen_prefs})

    # Add full profile for compatibility scoring
    health_goals = user_doc.get("health_goals", [])
    cuisine_preferences = user_doc.get("cuisine_preferences", [])
    taste_preferences = user_doc.get("taste_preferences", [])
    dietary_pattern = user_doc.get("dietary_pattern", "omnivore")

    if health_goals or cuisine_preferences or taste_preferences:
        context.append({
            "user_profile": {
                "health_goals": health_goals,
                "cuisine_preferences": cuisine_preferences,
                "taste_preferences": taste_preferences,
                "dietary_pattern": dietary_pattern
            }
        })
```

**Why This Matters:**
- Context is passed to all LangGraph nodes
- `compatibility_service.py` extracts user profile from context
- No need for separate database calls in scoring service

---

### 5. LangGraph Pipeline Integration

#### `backend/app/flow/state.py`

**Added to ChatState:**
```python
class ChatState(BaseModel):
    # ... existing fields ...
    compatibility_results: Optional[CompatibilityResult] = None
```

#### `backend/app/flow/graph.py`

**Updated Pipeline Flow:**

```
OLD FLOW:
context_resolver → intent_classifier → query_part_generator
                                            ↓
                  ┌───────────────────────┼─────────────────────┐
                  ↓                       ↓                     ↓
            menu_retriever      dish_info_retriever    user_preferences_retriever
                  ↓                       ↓                     ↓
                  └───────────────────────┴─────────────────────┘
                                            ↓
                                  format_final_response

NEW FLOW:
context_resolver → intent_classifier → query_part_generator
                                            ↓
                  ┌───────────────────────┼─────────────────────┐
                  ↓                       ↓                     ↓
            menu_retriever      dish_info_retriever    user_preferences_retriever
                  ↓                                             ↓
          compatibility_scorer                                  ↓
                  ↓                       ↓                     ↓
                  └───────────────────────┴─────────────────────┘
                                            ↓
                                  format_final_response
```

**Key Changes:**
- Added `compatibility_scorer` node after `menu_retriever`
- Scorer runs in parallel with other services (except menu, which it depends on)
- Results flow to `format_final_response`

---

### 6. Response Synthesis Updates

#### `backend/app/models/responder_model.py`

**Added CompatibilityScoreBreakdown to DishResult:**

```python
class CompatibilityScoreBreakdown(BaseModel):
    overall_score: int
    allergen_safety: Dict[str, Any]
    nutrition_match: Dict[str, Any]
    taste_preference: Dict[str, Any]
    dietary_pattern: Dict[str, Any]
    recommendation: str
    alternative_suggestions: List[Dict[str, Any]]

class DishResult(BaseModel):
    # ... existing fields ...
    compatibility_score: Optional[CompatibilityScoreBreakdown] = None  # NEW
```

#### `backend/app/services/response_synthesizer_tool.py`

**Updated to Attach Compatibility Scores:**

```python
# For each dish in menu results
for dish in dishes:
    compatibility_score = None

    # Check if compatibility score exists
    if state.compatibility_results and state.compatibility_results.scores:
        comp_score = state.compatibility_results.scores.get(dish.dish_id)
        if comp_score:
            compatibility_score = CompatibilityScoreBreakdown(
                overall_score=comp_score.overall_score,
                allergen_safety=comp_score.allergen_safety.model_dump(),
                # ... other fields
            )

    dish_results.append(DishResult(
        # ... dish fields ...
        compatibility_score=compatibility_score  # Attached here
    ))
```

---

## API Response Format

### Before (without compatibility scoring):

```json
{
  "responses": [
    {
      "query": "show me pasta dishes",
      "type": "menu_search",
      "result": [
        {
          "_id": "dish_123",
          "name": "Spicy Arrabbiata Pasta",
          "price": 12.99,
          "ingredients": ["pasta", "tomato", "garlic", "chili"],
          "explicit_allergens": ["wheat_gluten"]
        }
      ]
    }
  ]
}
```

### After (with compatibility scoring):

```json
{
  "responses": [
    {
      "query": "show me pasta dishes",
      "type": "menu_search",
      "result": [
        {
          "_id": "dish_123",
          "name": "Spicy Arrabbiata Pasta",
          "price": 12.99,
          "ingredients": ["pasta", "tomato", "garlic", "chili"],
          "explicit_allergens": ["wheat_gluten"],
          "compatibility_score": {
            "overall_score": 75,
            "allergen_safety": {
              "score": 100,
              "level": "SAFE",
              "detected_allergens": [],
              "reasoning": "No allergens detected that match user allergies"
            },
            "nutrition_match": {
              "score": 45,
              "level": "MODERATE",
              "matched_goals": [],
              "conflicts": ["low-carb"],
              "reasoning": "High in carbohydrates (60g), conflicts with low-carb goal"
            },
            "taste_preference": {
              "score": 95,
              "level": "EXCELLENT",
              "matched_cuisines": ["Italian"],
              "matched_tastes": ["spicy"],
              "reasoning": "Perfect match for Italian and spicy preferences"
            },
            "dietary_pattern": {
              "score": 60,
              "level": "MODERATE",
              "user_pattern": "vegetarian",
              "dish_category": "contains meat",
              "reasoning": "Contains meat, user follows vegetarian diet 80% of time"
            },
            "recommendation": "This dish matches your taste preferences excellently, but it's high in carbs which conflicts with your low-carb goal. Consider a salad-based alternative.",
            "alternative_suggestions": [
              {
                "dish_id": "dish_456",
                "dish_name": "Grilled Chicken Caesar Salad",
                "compatibility_score": 88,
                "reason": "Lower in carbs, better aligns with health goals"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

---

## Testing Guide

### 1. Create Test User with Profile

```bash
# Create user via API
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "username": "testuser",
    "password": "password123",
    "allergen_preferences": ["peanuts", "shellfish"],
    "health_goals": ["low-carb", "high-protein"],
    "cuisine_preferences": ["Italian", "Mexican"],
    "taste_preferences": ["spicy", "savory"],
    "dietary_pattern": "vegetarian"
  }'

# Response: {"id": "USER_ID"}
```

### 2. Login and Get Auth Token

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# Response: {"token": "AUTH_TOKEN"}
```

### 3. Test Compatibility Scoring

```bash
# Search for dishes (compatibility scores will be attached)
curl -X POST http://localhost:8000/restaurants/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me pasta dishes",
    "restaurant_id": "rest_1",
    "user_id": "USER_ID"
  }'

# Response will include compatibility_score for each dish
```

### 4. Expected Behavior

**User Profile:**
- Allergens: peanuts, shellfish
- Health Goals: low-carb, high-protein
- Cuisines: Italian, Mexican
- Tastes: spicy, savory
- Pattern: vegetarian

**Dish: "Spicy Arrabbiata Pasta"**
- ✅ Allergen Safety: 100 (no peanuts/shellfish)
- ⚠️ Nutrition Match: 45 (high carb, conflicts with low-carb)
- ✅ Taste Preference: 95 (Italian + spicy match)
- ⚠️ Dietary Pattern: 60 (contains meat, user vegetarian)
- **Overall: 75/100**

**Dish: "Peanut Butter Chicken"**
- ❌ Allergen Safety: 0 (contains peanuts)
- ⚠️ Nutrition Match: 70 (high protein is good)
- ⚠️ Taste Preference: 60 (savory matches)
- ❌ Dietary Pattern: 40 (meat, user vegetarian)
- **Overall: 20/100** (safety override kicks in)

---

## Key Design Decisions

### 1. Why LLM-Based Scoring?

**Advantages:**
- Handles nuanced analysis (e.g., "low-carb" → check carb content)
- Provides natural language explanations
- Can reason about complex nutrition conflicts
- Adapts to various health goals without hardcoding

**Disadvantages:**
- Slower than rule-based (but acceptable for real-time)
- Requires LLM API costs
- Needs careful prompt engineering

**Decision:** Use LLM with temperature=0.3 for consistent, explainable scoring

### 2. Why Weighted Scoring?

**Weights:**
- Allergen Safety: 40% (safety is paramount)
- Nutrition Match: 25% (important for health goals)
- Taste Preference: 20% (enhances user experience)
- Dietary Pattern: 15% (respects dietary choices)

**Safety Override:** If allergen safety < 50, overall must be < 50
- Ensures unsafe dishes are always flagged
- User safety > taste preferences

### 3. Why Alternative Suggestions?

- Triggered when overall score < 70
- Helps users find better options
- Limited to 2 suggestions (avoid overwhelming)
- LLM intelligently picks similar but safer/healthier alternatives

---

## Files Modified/Created

### Created (6 files):
1. `backend/app/models/compatibility_model.py` - Score models
2. `backend/app/services/compatibility_service.py` - Scoring logic
3. `COMPATIBILITY_SCORING_IMPLEMENTATION.md` - This documentation

### Modified (6 files):
1. `backend/app/models/user_model.py` - Added profile fields
2. `backend/app/services/state_service.py` - Fetch full user profile
3. `backend/app/flow/state.py` - Added compatibility_results field
4. `backend/app/flow/graph.py` - Integrated scorer node
5. `backend/app/models/responder_model.py` - Added CompatibilityScoreBreakdown
6. `backend/app/services/response_synthesizer_tool.py` - Attach scores to dishes

---

## Performance Considerations

### LLM Call Costs
- **Per dish**: 1 LLM call (~1500 tokens in + ~300 tokens out)
- **Per alternative search**: 1 LLM call (~500 tokens)
- **Optimization**: Only score dishes that are retrieved (not entire menu)

### Caching Strategy (Future Enhancement)
- Cache compatibility scores for (user_id, dish_id) pairs
- Invalidate when user profile changes
- Reduces LLM calls by ~80% for returning users

---

## Future Enhancements

### 1. Score Caching
```python
# Check cache before scoring
cache_key = f"{user_id}:{dish_id}:{user_profile_hash}"
if cached_score := redis.get(cache_key):
    return cached_score

# Score and cache
score = calculate_compatibility(...)
redis.setex(cache_key, ttl=3600, value=score)
```

### 2. Batch Scoring
```python
# Instead of scoring dishes one-by-one
for dish in dishes:
    score = calculate_compatibility(dish)  # 10 dishes = 10 LLM calls

# Score in batches
scores = batch_calculate_compatibility(dishes)  # 10 dishes = 1 LLM call
```

### 3. User Feedback Loop
- Track when users ignore low-scoring dishes
- Adjust weights based on user behavior
- Example: If user always picks spicy dishes (even with low nutrition score),
  increase taste_preference weight for that user

### 4. Real-Time Profile Updates
- Allow users to temporarily adjust preferences ("today I want something sweet")
- Apply temporary boost to certain factors without changing profile

---

## Troubleshooting

### Compatibility scores not appearing in response

**Check:**
1. User has profile fields set (health_goals, cuisine_preferences, etc.)
2. User ID is being passed in request
3. Backend logs show "Fetching user profile for user_id: ..."
4. Compatibility scorer node is executing (check logs)

**Debug:**
```bash
# Check if user profile exists
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer AUTH_TOKEN"

# Should return user with health_goals, cuisine_preferences, etc.
```

### All scores are 50 (default)

**Cause:** LLM analysis failed, returning default score

**Fix:**
- Check OpenAI API key is valid
- Check LLM usage logs in `logs/llm_usage.csv`
- Review error logs for JSON parsing errors

### Safety override not working

**Expected:** Dish with allergens should have overall_score < 50

**Check:**
- User allergen_preferences are set
- Allergen names match (case-insensitive): "peanuts" vs "Peanuts"
- Dish explicit_allergens field is populated

---

## Summary

The AI-Powered Meal Compatibility Scoring feature transforms SafeBites from a simple dish search system into an intelligent dietary assistant. It:

1. **Protects user safety** with allergen detection (40% weight)
2. **Supports health goals** through nutrition matching (25% weight)
3. **Enhances experience** with taste preference matching (20% weight)
4. **Respects dietary choices** through pattern alignment (15% weight)

The implementation leverages LLMs for nuanced analysis while maintaining real-time performance. With comprehensive scoring, natural language explanations, and intelligent alternative suggestions, users can make informed, personalized dining decisions.

**Next Steps:**
1. Update frontend to display compatibility scores visually
2. Test with real user data
3. Gather user feedback on scoring accuracy
4. Implement caching for performance optimization
