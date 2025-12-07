# Quick Start Guide - AI-Powered Meal Compatibility Scoring

## Prerequisites
- Backend server running on `http://localhost:8000`
- MongoDB running
- OpenAI API key configured in `.env`

## Option 1: Automated Test (Recommended)

```bash
cd backend
python test_compatibility_scoring.py
```

This will automatically:
1. ✅ Create a test user with full profile
2. ✅ Login and get auth token
3. ✅ Search for Italian dishes
4. ✅ Display compatibility scores with visual breakdown

---

## Option 2: Manual Testing with cURL

### Step 1: Create User with Profile

```bash
curl -X POST http://localhost:8000/users/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "username": "johndoe123",
    "password": "mypassword",
    "allergen_preferences": ["peanuts", "shellfish"],
    "health_goals": ["low-carb", "high-protein"],
    "cuisine_preferences": ["Italian", "Mexican"],
    "taste_preferences": ["spicy", "savory"],
    "dietary_pattern": "vegetarian"
  }'
```

**Response:**
```json
{
  "_id": "674d5e8f9c1234567890abcd",
  "name": "John Doe",
  "username": "johndoe123",
  "allergen_preferences": ["peanuts", "shellfish"],
  "health_goals": ["low-carb", "high-protein"],
  "cuisine_preferences": ["Italian", "Mexican"],
  "taste_preferences": ["spicy", "savory"],
  "dietary_pattern": "vegetarian"
}
```

**Save the `_id` value - you'll need it for the next step!**

### Step 2: Search for Dishes (with Compatibility Scoring)

```bash
# Replace USER_ID with the _id from step 1
curl -X POST http://localhost:8000/restaurants/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me pasta dishes",
    "restaurant_id": "rest_1",
    "user_id": "674d5e8f9c1234567890abcd"
  }'
```

**Response will include compatibility_score for each dish:**
```json
{
  "responses": [{
    "query": "show me pasta dishes",
    "type": "menu_search",
    "result": [{
      "_id": "dish_123",
      "name": "Spicy Arrabbiata Pasta",
      "price": 12.99,
      "compatibility_score": {
        "overall_score": 75,
        "allergen_safety": {
          "score": 100,
          "level": "SAFE",
          "detected_allergens": [],
          "reasoning": "No allergens detected"
        },
        "nutrition_match": {
          "score": 45,
          "level": "MODERATE",
          "matched_goals": [],
          "conflicts": ["low-carb"],
          "reasoning": "High in carbs"
        },
        "taste_preference": {
          "score": 95,
          "level": "EXCELLENT",
          "matched_cuisines": ["Italian"],
          "matched_tastes": ["spicy"]
        },
        "dietary_pattern": {
          "score": 100,
          "level": "EXCELLENT",
          "user_pattern": "vegetarian",
          "dish_category": "vegetarian"
        },
        "recommendation": "Matches taste preferences excellently...",
        "alternative_suggestions": []
      }
    }]
  }]
}
```

---

## Understanding Profile Fields

### `allergen_preferences` (list)
Allergens to avoid. Used for **allergen safety scoring (40% weight)**.

**Example values:**
- `"peanuts"`
- `"dairy"`
- `"shellfish"`
- `"wheat_gluten"`
- `"tree_nuts"`
- `"soy"`
- `"egg"`
- `"fish"`
- `"sesame"`

### `health_goals` (list)
Health/dietary goals. Used for **nutrition matching (25% weight)**.

**Example values:**
- `"low-carb"` - Prefers low-carbohydrate dishes
- `"high-protein"` - Prefers high-protein dishes
- `"low-fat"` - Prefers low-fat dishes
- `"low-calorie"` - Prefers low-calorie dishes
- `"weight-loss"` - Similar to low-calorie
- `"muscle-gain"` - Similar to high-protein
- `"low-sodium"` - Prefers low-sodium dishes

### `cuisine_preferences` (list)
Preferred cuisines. Used for **taste preference scoring (20% weight)**.

**Example values:**
- `"Italian"`
- `"Mexican"`
- `"Chinese"`
- `"Indian"`
- `"Thai"`
- `"Japanese"`
- `"Mediterranean"`
- `"American"`

### `taste_preferences` (list)
Taste profiles. Used for **taste preference scoring (20% weight)**.

**Example values:**
- `"spicy"`
- `"sweet"`
- `"savory"`
- `"sour"`
- `"bitter"`
- `"umami"`
- `"mild"`

### `dietary_pattern` (string)
Primary dietary pattern. Used for **dietary pattern scoring (15% weight)**.

**Allowed values:**
- `"omnivore"` (default) - Eats everything
- `"vegetarian"` - No meat/fish
- `"vegan"` - No animal products
- `"pescatarian"` - No meat but eats fish

---

## Example Scenarios

### Scenario 1: Health-Conscious User
```json
{
  "health_goals": ["low-carb", "high-protein"],
  "dietary_pattern": "omnivore"
}
```
→ High scores for: grilled chicken, fish, salads
→ Low scores for: pasta, pizza, desserts

### Scenario 2: Allergy-Aware User
```json
{
  "allergen_preferences": ["peanuts", "dairy"]
}
```
→ Dishes with peanuts/dairy get allergen safety = 0
→ Overall score forced < 50 (safety override)

### Scenario 3: Vegetarian Italian Lover
```json
{
  "dietary_pattern": "vegetarian",
  "cuisine_preferences": ["Italian"],
  "taste_preferences": ["savory"]
}
```
→ High scores for: vegetarian pasta, pizza margherita
→ Low scores for: meat dishes

---

## Scoring System

### Overall Score = Weighted Average
- **Allergen Safety**: 40%
- **Nutrition Match**: 25%
- **Taste Preference**: 20%
- **Dietary Pattern**: 15%

### Safety Override Rule
If allergen safety < 50, overall score MUST be < 50
**User safety is paramount!**

### Score Ranges
- **80-100**: Excellent match (✅ green)
- **60-79**: Good match (⚠️ yellow)
- **40-59**: Moderate match (⚠️ orange)
- **0-39**: Poor match (❌ red)

---

## Troubleshooting

### Issue: No compatibility scores in response

**Check:**
1. ✅ User has profile fields set (health_goals, cuisine_preferences, etc.)
2. ✅ You're passing `user_id` in the search request
3. ✅ Backend server is running
4. ✅ MongoDB is running

**Debug:**
```bash
# Check if user profile exists
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Issue: 404 Not Found

**Common mistakes:**
- ❌ Using `/users` instead of `/users/signup`
- ❌ Using JSON body for login instead of query params
- ✅ Use `/users/signup` for registration
- ✅ Use query params for `/users/login?username=...&password=...`

### Issue: All scores are 50 (default)

**Cause:** LLM analysis failed

**Fix:**
1. Check OpenAI API key in `.env`
2. Check `logs/llm_usage.csv` for errors
3. Check backend console for error messages

---

## Next Steps

1. ✅ Run the automated test: `python test_compatibility_scoring.py`
2. ✅ Create users with different profiles to test different scenarios
3. ✅ Integrate into your frontend to display scores visually
4. ✅ Gather user feedback on scoring accuracy

For complete implementation details, see `COMPATIBILITY_SCORING_IMPLEMENTATION.md`
