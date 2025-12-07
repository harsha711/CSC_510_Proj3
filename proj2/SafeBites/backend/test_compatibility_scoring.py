"""
Test Script for AI-Powered Meal Compatibility Scoring

This script tests the compatibility scoring feature end-to-end:
1. Creates a test user with profile
2. Performs a dish search
3. Verifies compatibility scores are attached to results
"""
import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"

def test_compatibility_scoring():
    print("=" * 80)
    print("Testing AI-Powered Meal Compatibility Scoring")
    print("=" * 80)

    # Step 1: Create test user with full profile
    print("\n1. Creating test user with profile...")
    user_data = {
        "name": "Compatibility Test User",
        "username": f"comp_test_user_{int(__import__('time').time())}",
        "password": "testpass123",
        "allergen_preferences": ["peanuts", "shellfish"],
        "health_goals": ["low-carb", "high-protein"],
        "cuisine_preferences": ["Italian", "Mexican"],
        "taste_preferences": ["spicy", "savory"],
        "dietary_pattern": "vegetarian"
    }

    try:
        response = requests.post(f"{BASE_URL}/users/signup", json=user_data)
        response.raise_for_status()
        user_id = response.json()["_id"]
        print(f"✅ User created with ID: {user_id}")
        print(f"   Profile: {user_data['dietary_pattern']} diet")
        print(f"   Allergens: {', '.join(user_data['allergen_preferences'])}")
        print(f"   Health goals: {', '.join(user_data['health_goals'])}")
        print(f"   Cuisine prefs: {', '.join(user_data['cuisine_preferences'])}")
    except Exception as e:
        print(f"❌ Failed to create user: {e}")
        return

    # Step 2: Login to get token (if needed)
    print("\n2. Logging in...")
    try:
        response = requests.post(
            f"{BASE_URL}/users/login",
            params={
                "username": user_data["username"],
                "password": user_data["password"]
            }
        )
        response.raise_for_status()
        auth_token = response.json()["token"]
        print(f"✅ Login successful, token: {auth_token[:20]}...")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        print(f"   Note: Login is optional for this test")
        auth_token = None

    # Step 3: Search for dishes with compatibility scoring
    print("\n3. Searching for dishes (compatibility scoring should activate)...")
    search_query = {
        "query": "show me all dishes",
        "restaurant_id": "rest_1",
        "user_id": user_id
    }

    try:
        response = requests.post(
            f"{BASE_URL}/restaurants/search",
            json=search_query
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ Search completed, status: {result.get('status')}")

        # Step 4: Check if compatibility scores are present
        print("\n4. Analyzing compatibility scores...")
        has_scores = False
        dishes_analyzed = 0

        for query_response in result.get("responses", []):
            if query_response["type"] == "menu_search":
                dishes = query_response["result"]
                print(f"\n   Found {len(dishes)} dishes")

                for dish in dishes[:3]:  # Check first 3 dishes
                    dishes_analyzed += 1
                    print(f"\n   📌 Dish: {dish['name']}")
                    print(f"      Price: ${dish.get('price', 'N/A')}")

                    comp_score = dish.get("compatibility_score")
                    if comp_score:
                        has_scores = True
                        print(f"\n      🎯 Compatibility Score: {comp_score['overall_score']}/100")

                        # Allergen Safety
                        allergen = comp_score["allergen_safety"]
                        icon = "✅" if allergen["level"] == "SAFE" else "⚠️" if allergen["level"] == "WARNING" else "❌"
                        print(f"      {icon} Allergen Safety: {allergen['score']}/100 ({allergen['level']})")
                        if allergen['detected_allergens']:
                            print(f"         Detected: {', '.join(allergen['detected_allergens'])}")
                        print(f"         Reasoning: {allergen['reasoning'][:100]}...")

                        # Nutrition Match
                        nutrition = comp_score["nutrition_match"]
                        icon = "✅" if nutrition["level"] == "EXCELLENT" else "⚠️" if nutrition["level"] in ["GOOD", "MODERATE"] else "❌"
                        print(f"      {icon} Nutrition Match: {nutrition['score']}/100 ({nutrition['level']})")
                        if nutrition['matched_goals']:
                            print(f"         Matched goals: {', '.join(nutrition['matched_goals'])}")
                        if nutrition['conflicts']:
                            print(f"         Conflicts: {', '.join(nutrition['conflicts'])}")
                        print(f"         Reasoning: {nutrition['reasoning'][:100]}...")

                        # Taste Preference
                        taste = comp_score["taste_preference"]
                        icon = "✅" if taste["level"] == "EXCELLENT" else "⚠️" if taste["level"] in ["GOOD", "MODERATE"] else "❌"
                        print(f"      {icon} Taste Preference: {taste['score']}/100 ({taste['level']})")
                        if taste['matched_cuisines']:
                            print(f"         Matched cuisines: {', '.join(taste['matched_cuisines'])}")
                        if taste['matched_tastes']:
                            print(f"         Matched tastes: {', '.join(taste['matched_tastes'])}")

                        # Dietary Pattern
                        dietary = comp_score["dietary_pattern"]
                        icon = "✅" if dietary["level"] == "EXCELLENT" else "⚠️" if dietary["level"] in ["GOOD", "MODERATE"] else "❌"
                        print(f"      {icon} Dietary Pattern: {dietary['score']}/100 ({dietary['level']})")
                        print(f"         User pattern: {dietary['user_pattern']}")
                        print(f"         Dish category: {dietary['dish_category']}")

                        # Recommendation
                        print(f"\n      💡 AI Recommendation:")
                        print(f"         {comp_score['recommendation']}")

                        # Alternatives
                        if comp_score['alternative_suggestions']:
                            print(f"\n      🔄 Alternative Suggestions:")
                            for alt in comp_score['alternative_suggestions']:
                                print(f"         - {alt['dish_name']} ({alt['compatibility_score']}/100)")
                                print(f"           Reason: {alt['reason']}")

                    else:
                        print(f"      ⚠️  No compatibility score (user may not have profile)")

        print("\n" + "=" * 80)
        print("Test Summary:")
        print(f"  Dishes analyzed: {dishes_analyzed}")
        print(f"  Compatibility scores present: {'✅ YES' if has_scores else '❌ NO'}")

        if has_scores:
            print("\n✅ SUCCESS: Compatibility scoring is working correctly!")
        else:
            print("\n❌ FAILURE: Compatibility scores not found in response")
            print("   Possible issues:")
            print("   - User profile may not be fetched in context")
            print("   - Compatibility scorer node may not be executing")
            print("   - Check backend logs for errors")

        print("=" * 80)

    except Exception as e:
        print(f"❌ Search failed: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        return

if __name__ == "__main__":
    test_compatibility_scoring()
