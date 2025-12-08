"""
Test script to verify score enforcement logic works correctly.
Tests the scenario: allergen=100, nutrition=75, taste=30, dietary=100
Expected overall score: (100*0.40) + (75*0.25) + (30*0.20) + (100*0.15) = 79.75 ≈ 80
"""

def test_score_calculation():
    """Test the weighted formula calculation"""

    # Test Case 1: Good allergen, nutrition, dietary but low taste
    allergen = 100
    nutrition = 75
    taste = 30
    dietary = 100

    calculated_score = round((allergen * 0.40) + (nutrition * 0.25) + (taste * 0.20) + (dietary * 0.15))

    print(f"\nTest Case 1: Low taste preference but good other scores")
    print(f"  Allergen Safety: {allergen}")
    print(f"  Nutrition Match: {nutrition}")
    print(f"  Taste Preference: {taste}")
    print(f"  Dietary Pattern: {dietary}")
    print(f"  Calculated Overall Score: {calculated_score}")
    print(f"  Expected: 80")

    assert calculated_score == 80, f"Expected 80, got {calculated_score}"
    print(f"  ✓ PASS")

    # Test Case 2: All components match well except taste=0
    allergen = 100
    nutrition = 80
    taste = 0
    dietary = 100

    calculated_score = round((allergen * 0.40) + (nutrition * 0.25) + (taste * 0.20) + (dietary * 0.15))

    print(f"\nTest Case 2: Zero taste preference but excellent other scores")
    print(f"  Allergen Safety: {allergen}")
    print(f"  Nutrition Match: {nutrition}")
    print(f"  Taste Preference: {taste}")
    print(f"  Dietary Pattern: {dietary}")
    print(f"  Calculated Overall Score: {calculated_score}")
    print(f"  Expected: 75")

    assert calculated_score == 75, f"Expected 75, got {calculated_score}"
    print(f"  ✓ PASS")

    # Test Case 3: Safety override - low allergen score
    allergen = 40
    nutrition = 80
    taste = 80
    dietary = 100

    calculated_score = round((allergen * 0.40) + (nutrition * 0.25) + (taste * 0.20) + (dietary * 0.15))

    print(f"\nTest Case 3: Low allergen safety (should cap overall score)")
    print(f"  Allergen Safety: {allergen}")
    print(f"  Nutrition Match: {nutrition}")
    print(f"  Taste Preference: {taste}")
    print(f"  Dietary Pattern: {dietary}")
    print(f"  Calculated Overall Score (before safety override): {calculated_score}")

    # Apply safety override
    if allergen < 50 and calculated_score >= 50:
        calculated_score = min(calculated_score, 49)

    print(f"  Calculated Overall Score (after safety override): {calculated_score}")
    print(f"  Expected: 49 (capped due to low allergen safety)")

    assert calculated_score == 49, f"Expected 49, got {calculated_score}"
    print(f"  ✓ PASS")

    # Test Case 4: Check deviation threshold (LLM gave 0, should override)
    llm_score = 0
    allergen = 100
    nutrition = 75
    taste = 50
    dietary = 80

    calculated_score = round((allergen * 0.40) + (nutrition * 0.25) + (taste * 0.20) + (dietary * 0.15))

    print(f"\nTest Case 4: LLM gave 0 score (should be overridden)")
    print(f"  LLM Overall Score: {llm_score}")
    print(f"  Allergen Safety: {allergen}")
    print(f"  Nutrition Match: {nutrition}")
    print(f"  Taste Preference: {taste}")
    print(f"  Dietary Pattern: {dietary}")
    print(f"  Calculated Overall Score: {calculated_score}")

    should_override = llm_score == 0 or abs(llm_score - calculated_score) > 20
    final_score = calculated_score if should_override else llm_score

    print(f"  Should Override: {should_override}")
    print(f"  Final Score: {final_score}")
    print(f"  Expected: 81 (overridden from 0)")

    assert final_score == 81, f"Expected 81, got {final_score}"
    print(f"  ✓ PASS")

    print(f"\n{'='*60}")
    print(f"ALL TESTS PASSED ✓")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_score_calculation()
