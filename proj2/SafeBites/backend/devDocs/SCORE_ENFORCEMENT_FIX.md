# Score Enforcement Fix

## Problem

Users reported that dishes were receiving an **overall compatibility score of 0** even when they had:
- ✅ Allergen match (score: 100)
- ✅ Nutrition match (score: 75-80)
- ✅ Dietary pattern match (score: 100)
- ❌ Taste preference mismatch (score: 0-30)

**Example scenario:**
- User has allergen preferences and dietary pattern: vegan
- Dish matches all allergens and is vegan
- Dish is Italian cuisine but user prefers Asian cuisine
- **Expected overall score:** ~75-80 (weighted average)
- **Actual overall score:** 0 ❌

## Root Cause

The LLM (GPT-4o-mini) was not consistently following the weighted scoring formula in the prompt:

```
Overall Score = (Allergen × 0.40) + (Nutrition × 0.25) + (Taste × 0.20) + (Dietary × 0.15)
```

When taste preference didn't match, the LLM sometimes:
1. Set `overall_score = 0` (ignoring the formula completely)
2. Gave excessive weight to taste preference (treating it as a deal-breaker)
3. Provided scores that deviated significantly from the mathematical calculation

## Solution

Added **mathematical enforcement** of the weighted formula in [compatibility_service.py](app/services/compatibility_service.py) (lines 273-289):

```python
# ENFORCE weighted formula if LLM didn't follow it correctly
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
```

### Key Features:

1. **Calculate mathematically correct score** from component scores
2. **Safety override**: If allergen safety < 50, cap overall score at 49 (safety is paramount)
3. **Override LLM score** if:
   - LLM gives 0 (clearly wrong)
   - LLM deviates by >20 points from calculated score
4. **Log warning** when overriding for debugging

## Test Results

Verified with unit tests ([test_score_enforcement.py](test_score_enforcement.py)):

### Test Case 1: Low taste, good other scores
- Allergen: 100, Nutrition: 75, Taste: 30, Dietary: 100
- **Result:** 80 ✓

### Test Case 2: Zero taste, excellent other scores
- Allergen: 100, Nutrition: 80, Taste: 0, Dietary: 100
- **Result:** 75 ✓

### Test Case 3: Safety override
- Allergen: 40, Nutrition: 80, Taste: 80, Dietary: 100
- **Calculated:** 67
- **After override:** 49 ✓ (capped due to low allergen safety)

### Test Case 4: LLM gave 0 score
- LLM score: 0
- Allergen: 100, Nutrition: 75, Taste: 50, Dietary: 80
- **Calculated:** 81
- **Final:** 81 ✓ (overridden from 0)

## Impact

- ✅ Prevents zero overall scores when only one component (taste) doesn't match
- ✅ Ensures weighted formula is always respected
- ✅ Maintains safety priority (allergens are 40% of score)
- ✅ Provides transparency through logging when LLM scores are overridden
- ✅ No impact on performance (simple arithmetic operation)

## Example Before/After

**Scenario:** Vegan user looking at vegan Italian pasta, but prefers Asian cuisine

### Before Fix:
```json
{
  "allergen_safety": {"score": 100},
  "nutrition_match": {"score": 80},
  "taste_preference": {"score": 25},
  "dietary_pattern": {"score": 100},
  "overall_score": 0  ❌
}
```

### After Fix:
```json
{
  "allergen_safety": {"score": 100},
  "nutrition_match": {"score": 80},
  "taste_preference": {"score": 25},
  "dietary_pattern": {"score": 100},
  "overall_score": 80  ✓
}
```
**Calculation:** (100×0.40) + (80×0.25) + (25×0.20) + (100×0.15) = 40 + 20 + 5 + 15 = 80

## Files Modified

- [app/services/compatibility_service.py](app/services/compatibility_service.py) (lines 273-289)

## Related Issues

- User feedback: "there is allergen match, nutrition match, diet match, just taste match was not there. that dish got a zero compataibility score, please fix the scoring"
- Previous fix: Updated prompt to emphasize weighted formula (insufficient alone)
- Current fix: Mathematical enforcement in code (reliable)

## Testing

Run the test suite:
```bash
cd backend
python3 test_score_enforcement.py
```

## Monitoring

Check backend logs for warning messages when score enforcement kicks in:
```
WARNING: LLM gave overall_score=0, but calculated=80. Using calculated.
```

This indicates the LLM attempted to violate the scoring rules but was corrected by the enforcement logic.
