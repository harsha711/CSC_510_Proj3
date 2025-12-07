# Lenient Filtering Mode - Prioritizing Results Over Strict Filtering

## Overview

With limited data in the database, the system has been updated to use **lenient filtering mode**. Instead of aggressively filtering out dishes, we now:

1. **Return more dishes** with lower thresholds
2. **Rely on AI compatibility scoring** to warn users about issues
3. **Sort by compatibility score** in descending order

This ensures users always see results, even if they don't perfectly match the query.

## Changes Made

### 1. FAISS Similarity Threshold: 0.8 → 0.5

**File**: [backend/app/services/faiss_service.py:259](backend/app/services/faiss_service.py#L259)

```python
# BEFORE
def search_dishes(query, restaurant_id=None, top_k=20, threshold=0.8):

# AFTER
def search_dishes(query, restaurant_id=None, top_k=20, threshold=0.5):
```

**Impact**:
- More semantically related dishes pass the initial FAISS search
- Prevents empty results when database is small
- Downstream filters and compatibility scoring handle specificity

### 2. Lenient Filter Application

**File**: [backend/app/services/restaurant_service.py:638-690](backend/app/services/restaurant_service.py#L638-L690)

**Changes**:
- **Price filters**: 10% margin allowed, only exclude if >150% over budget
- **Ingredient include**: Only filter out if ZERO overlap with many specified ingredients
- **Ingredient exclude**: DISABLED (handled by compatibility scorer)
- **Allergen filtering**: DISABLED (handled by compatibility scorer with safety warnings)
- **Nutrition filtering**: DISABLED (handled by compatibility scorer)

**Before**:
```python
# Strict filtering - excluded dishes immediately
if filters.allergens.exclude:
    excluded_allergens = {a.lower() for a in filters.allergens.exclude}
    dish_allergens = {a.lower() for a in d.allergens}
    if excluded_allergens.intersection(dish_allergens):
        continue  # Dish excluded, user never sees it
```

**After**:
```python
# Allergen filtering - DISABLED (let compatibility scorer handle it)
# Allergen safety is handled by compatibility scoring with proper warnings
# This ensures users can still see dishes even if they contain allergens
filtered.append(d)  # All dishes pass, compatibility scorer warns about issues
```

### 3. Lenient LLM Validation

**File**: [backend/app/services/restaurant_service.py:692-726](backend/app/services/restaurant_service.py#L692-L726)

**Updated Prompt**:
```
IMPORTANT: Be VERY LENIENT in your validation. The goal is to show dishes to the user.
- If a dish is even remotely related to the query, include it.
- If the query is general (like "show dishes", "what do you have"), include ALL dishes.
- Only exclude dishes that are completely unrelated to the query.
- Compatibility scoring will handle detailed matching and warnings.

When in doubt, INCLUDE the dish.
```

### 4. Sort by Compatibility Score (Descending)

**File**: [backend/app/services/response_synthesizer_tool.py:92-99](backend/app/services/response_synthesizer_tool.py#L92-L99)

```python
# SORT BY COMPATIBILITY SCORE (highest first)
# Dishes with no compatibility score go to the end
dish_results.sort(
    key=lambda d: d.compatibility_score.overall_score if d.compatibility_score else -1,
    reverse=True
)
```

**Impact**:
- Best matches appear first (score 80-100)
- Moderate matches in the middle (score 50-79)
- Poor matches at the end (score 0-49)
- Users can quickly identify suitable dishes

## New User Experience

### Example Query: "Show dishes under $20 that do not contain fish"

#### Old Behavior (Strict Filtering):
```
Result: 0 dishes found
Reason: All fish dishes filtered out before compatibility scoring
User sees: "No results found"
```

#### New Behavior (Lenient Filtering):
```
Result: 5 dishes returned, sorted by compatibility:

1. Veggie Pasta - $15 (Score: 85/100) ✅ SAFE
   - No fish, under $20, good nutrition

2. Chicken Salad - $18 (Score: 78/100) ✅ SAFE
   - No fish, under $20, moderate match

3. Margherita Pizza - $22 (Score: 60/100) ⚠️ WARNING
   - No fish, but OVER $20 by $2

4. Grilled Salmon - $19 (Score: 25/100) ❌ UNSAFE
   - Contains FISH (allergen warning)
   - Under $20 (price okay)

5. Seafood Platter - $35 (Score: 10/100) ❌ UNSAFE
   - Contains FISH (allergen warning)
   - Over budget by $15
```

**Key Benefits**:
1. User sees 5 options instead of 0
2. Best matches (no fish, under $20) appear first
3. Fish dishes show LOW compatibility scores with warnings
4. User can make informed decision
5. If desperate, user might accept the $22 pizza (close to budget)

## Architecture: Multi-Stage Filtering Pipeline

```
User Query: "Show dishes under $20 without fish"
    ↓
[1. FAISS Semantic Search]
    threshold=0.5 (LENIENT)
    ↓
Retrieved: 10 dishes (including fish dishes, various prices)
    ↓
[2. LLM Filter Extraction]
    Extracts: max_price=$20, exclude_allergens=["fish"]
    ↓
[3. Lenient Filtering]
    - Price: Allow up to $30 (50% margin)
    - Allergens: DISABLED (pass all dishes)
    ↓
Filtered: 8 dishes (only extreme outliers removed)
    ↓
[4. LLM Validation]
    "Be very lenient, when in doubt include the dish"
    ↓
Validated: 7 dishes
    ↓
[5. AI Compatibility Scoring]
    Analyzes each dish against user profile
    - Veggie Pasta: 85/100 (no fish, good price)
    - Salmon: 25/100 (CONTAINS FISH - warning)
    ↓
[6. Sort by Compatibility (Descending)]
    Best matches first, worst matches last
    ↓
Final Result: 7 dishes, sorted by score, with detailed warnings
```

## Compatibility Scoring as the Safety Net

With lenient filtering, **compatibility scoring becomes critical**:

### Allergen Safety (40% weight)
- **Score 80-100**: No allergens detected ✅
- **Score 50-79**: Minor allergen concerns ⚠️
- **Score 0-49**: CONTAINS USER ALLERGENS ❌

### Overall Score Calculation
```python
overall_score = (
    allergen_safety * 0.4 +     # 40% - Most important
    nutrition_match * 0.25 +    # 25%
    taste_preference * 0.20 +   # 20%
    dietary_pattern * 0.15      # 15%
)

# Safety override
if allergen_safety < 50:
    overall_score = min(overall_score, 49)  # Force low score
```

### Frontend Display
```tsx
{dish.compatibility_score && (
  <div className="compatibility-score-container">
    <div className={`overall-score score-${Math.floor(score / 20)}`}>
      {score}/100
    </div>

    {/* Allergen Safety */}
    <div className={`allergen-safety ${level.toLowerCase()}`}>
      {level === 'UNSAFE' ? '❌' : level === 'WARNING' ? '⚠️' : '✅'}
      Allergen Safety: {score}/100
    </div>

    {/* Detected Allergens */}
    {detected_allergens.length > 0 && (
      <div className="allergen-warning">
        ⚠️ Contains: {detected_allergens.join(', ')}
      </div>
    )}
  </div>
)}
```

## When to Use Strict vs Lenient Mode

### Use Lenient Mode (Current) When:
- Database has < 50 dishes
- Users frequently see "no results found"
- Building/testing new features
- User satisfaction > strict accuracy

### Use Strict Mode When:
- Database has > 200 dishes per restaurant
- Users complain about irrelevant results
- Allergy concerns are critical (though compatibility scoring still handles this)
- System is mature and well-populated

## Configuration

To switch between modes in the future, add environment variables:

```python
# .env
FAISS_THRESHOLD=0.5          # Lower = more lenient
ENABLE_ALLERGEN_FILTER=false # Disable strict allergen filtering
ENABLE_INGREDIENT_FILTER=false
PRICE_MARGIN_PERCENT=10      # Allow 10% price flexibility
```

## Testing the Changes

### Test Case 1: General Query
```bash
Query: "show me all dishes"
Expected: Return ALL dishes, sorted by compatibility
```

### Test Case 2: Price Filter
```bash
Query: "dishes under $15"
User Profile: allergic to peanuts

Expected:
- Dishes up to ~$16.50 included (10% margin)
- Dishes with peanuts have LOW scores (25/100) but still shown
- Best matches (no peanuts, under $15) appear first
```

### Test Case 3: Allergen Query
```bash
Query: "nut-free dishes"
User Profile: allergic to tree nuts

Expected:
- ALL dishes returned (including nut dishes)
- Nut dishes have score < 50 with ❌ UNSAFE warning
- Nut-free dishes have score > 70 with ✅ SAFE indicator
```

## Benefits of This Approach

1. **Better User Experience**: Users always see results
2. **Informed Decisions**: Warnings help users make safe choices
3. **Transparent**: Users understand WHY dishes have low scores
4. **Flexible**: Works with both small and large databases
5. **Safe**: Allergen warnings are MORE visible than silent filtering
6. **Discovery**: Users might find unexpected dishes they like

## Related Documentation

- [FAISS_THRESHOLD_FIX.md](FAISS_THRESHOLD_FIX.md) - Details on FAISS threshold changes
- [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md) - How compatibility scores display in UI
- [backend/devDocs/COMPATIBILITY_SCORING_IMPLEMENTATION.md](backend/devDocs/COMPATIBILITY_SCORING_IMPLEMENTATION.md) - Compatibility scoring algorithm
