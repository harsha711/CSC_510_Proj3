"""
Unit tests for compatibility_service.py

Tests the AI-powered compatibility scoring service including:
- Batch compatibility calculation
- User profile extraction
- Default score generation
- Score calculation logic
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.compatibility_service import (
    calculate_compatibility_scores,
    extract_user_profile,
    calculate_batch_compatibility,
    create_default_compatibility_score,
    calculate_dish_compatibility,
    find_alternative_dishes
)
from app.models.compatibility_model import (
    CompatibilityScore, CompatibilityResult,
    AllergenSafetyScore, NutritionMatchScore, TastePreferenceScore, DietaryPatternScore,
    SafetyLevel, MatchLevel
)


class TestExtractUserProfile:
    """Test user profile extraction from context"""

    def test_extract_complete_profile(self):
        """Test extracting a complete user profile"""
        context = [
            {
                "user_allergens": ["peanuts", "shellfish"],
                "user_profile": {
                    "health_goals": ["low-carb", "high-protein"],
                    "cuisine_preferences": ["italian", "mexican"],
                    "taste_preferences": ["spicy", "savory"],
                    "dietary_pattern": "omnivore"
                }
            }
        ]

        profile = extract_user_profile(context)

        assert profile is not None
        assert profile["allergens"] == ["peanuts", "shellfish"]
        assert profile["health_goals"] == ["low-carb", "high-protein"]
        assert profile["cuisine_preferences"] == ["italian", "mexican"]
        assert profile["taste_preferences"] == ["spicy", "savory"]
        assert profile["dietary_pattern"] == "omnivore"

    def test_extract_profile_allergens_only(self):
        """Test extracting profile with only allergens"""
        context = [{"user_allergens": ["dairy"]}]

        profile = extract_user_profile(context)

        assert profile is not None
        assert profile["allergens"] == ["dairy"]
        assert profile["health_goals"] == []
        assert profile["dietary_pattern"] == "omnivore"

    def test_extract_profile_no_allergens(self):
        """Test extracting profile without allergens"""
        context = [
            {
                "user_profile": {
                    "health_goals": ["weight-loss"],
                    "dietary_pattern": "vegetarian"
                }
            }
        ]

        profile = extract_user_profile(context)

        assert profile is not None
        assert profile["allergens"] == []
        assert profile["health_goals"] == ["weight-loss"]
        assert profile["dietary_pattern"] == "vegetarian"

    def test_extract_profile_empty_context(self):
        """Test extracting profile from empty context"""
        profile = extract_user_profile([])
        assert profile is None

    def test_extract_profile_none_context(self):
        """Test extracting profile from None context"""
        profile = extract_user_profile(None)
        assert profile is None

    def test_extract_profile_no_user_data(self):
        """Test extracting profile with no user data"""
        context = [{"other_key": "value"}]
        profile = extract_user_profile(context)
        assert profile is None


class TestCreateDefaultCompatibilityScore:
    """Test default compatibility score creation"""

    def test_create_default_score(self):
        """Test creating a default compatibility score"""
        dish = Mock()
        dish.dish_id = "dish123"
        dish.dish_name = "Test Dish"

        score = create_default_compatibility_score(dish)

        assert isinstance(score, CompatibilityScore)
        assert score.dish_id == "dish123"
        assert score.dish_name == "Test Dish"
        assert score.overall_score == 50
        assert score.allergen_safety.score == 50
        assert score.allergen_safety.level == SafetyLevel.WARNING
        assert score.nutrition_match.score == 50
        assert score.taste_preference.score == 50
        assert score.dietary_pattern.score == 50
        assert "Unable to analyze" in score.allergen_safety.reasoning

    def test_default_score_has_all_fields(self):
        """Test that default score has all required fields"""
        dish = Mock()
        dish.dish_id = "dish456"
        dish.dish_name = "Another Dish"

        score = create_default_compatibility_score(dish)

        assert hasattr(score, 'allergen_safety')
        assert hasattr(score, 'nutrition_match')
        assert hasattr(score, 'taste_preference')
        assert hasattr(score, 'dietary_pattern')
        assert hasattr(score, 'recommendation')
        assert hasattr(score, 'alternative_suggestions')
        assert score.alternative_suggestions == []


class TestCalculateCompatibilityScores:
    """Test main compatibility scoring function"""

    def test_no_menu_results(self):
        """Test scoring with no menu results"""
        state = Mock()
        state.menu_results = None
        state.context = []

        result = calculate_compatibility_scores(state)

        assert "compatibility_results" in result
        assert isinstance(result["compatibility_results"], CompatibilityResult)
        assert result["compatibility_results"].scores == {}

    def test_empty_menu_results(self):
        """Test scoring with empty menu results"""
        state = Mock()
        state.menu_results = Mock()
        state.menu_results.menu_results = {}
        state.context = []

        result = calculate_compatibility_scores(state)

        assert result["compatibility_results"].scores == {}

    def test_no_user_profile(self):
        """Test scoring without user profile"""
        state = Mock()
        state.menu_results = Mock()
        state.menu_results.menu_results = {"pizza": [Mock()]}
        state.context = []

        result = calculate_compatibility_scores(state)

        assert result["compatibility_results"].scores == {}


class TestBatchCompatibilityCalculation:
    """Test batch compatibility calculation"""

    def test_empty_dishes_list(self):
        """Test batch calculation with empty dishes"""
        result = calculate_batch_compatibility([], {"allergens": []})
        assert result == {}

    @patch('app.services.compatibility_service.llm')
    def test_batch_calculation_with_llm_response(self, mock_llm):
        """Test batch calculation with mocked LLM response"""
        # Mock dish
        dish = Mock()
        dish.dish_id = "dish123"
        dish.dish_name = "Pizza"
        dish.description = "Cheese pizza"
        dish.ingredients = ["cheese", "dough", "tomato"]
        dish.allergens = ["dairy"]
        dish.nutrition_facts = {"calories": 300}
        dish.price = 12.99

        # Mock LLM response
        mock_response = Mock()
        mock_response.content = '''
        [
          {
            "dish_id": "dish123",
            "overall_score": 75,
            "allergen_safety": {
              "score": 100,
              "level": "SAFE",
              "detected_allergens": [],
              "reasoning": "No user allergens detected"
            },
            "nutrition_match": {
              "score": 75,
              "level": "GOOD",
              "matched_goals": [],
              "conflicts": [],
              "reasoning": "Neutral nutrition"
            },
            "taste_preference": {
              "score": 75,
              "level": "GOOD",
              "matched_cuisines": [],
              "matched_tastes": [],
              "reasoning": "No preferences set"
            },
            "dietary_pattern": {
              "score": 75,
              "level": "GOOD",
              "user_pattern": "omnivore",
              "dish_category": "regular",
              "reasoning": "Suitable for omnivore"
            },
            "recommendation": "Good choice"
          }
        ]
        '''
        mock_llm.invoke.return_value = mock_response

        user_profile = {
            "allergens": [],
            "health_goals": [],
            "cuisine_preferences": [],
            "taste_preferences": [],
            "dietary_pattern": "omnivore"
        }

        result = calculate_batch_compatibility([dish], user_profile)

        assert "dish123" in result
        assert isinstance(result["dish123"], CompatibilityScore)
        assert result["dish123"].overall_score == 75

    @patch('app.services.compatibility_service.llm')
    def test_batch_calculation_llm_error_fallback(self, mock_llm):
        """Test batch calculation with LLM error falls back to default"""
        mock_llm.invoke.side_effect = Exception("LLM error")

        dish = Mock()
        dish.dish_id = "dish123"
        dish.dish_name = "Pizza"
        dish.description = "Cheese pizza"
        dish.ingredients = ["cheese"]
        dish.allergens = []
        dish.nutrition_facts = {}
        dish.price = 10.00

        user_profile = {"allergens": [], "health_goals": [], "cuisine_preferences": [], "taste_preferences": [], "dietary_pattern": "omnivore"}

        result = calculate_batch_compatibility([dish], user_profile)

        assert "dish123" in result
        assert result["dish123"].overall_score == 50  # Default score


class TestWeightedFormulaEnforcement:
    """Test weighted formula enforcement in batch scoring"""

    @patch('app.services.compatibility_service.llm')
    def test_weighted_formula_corrects_wrong_llm_score(self, mock_llm):
        """Test that weighted formula corrects incorrect LLM scores"""
        dish = Mock()
        dish.dish_id = "dish123"
        dish.dish_name = "Test Dish"
        dish.description = "Test"
        dish.ingredients = ["ingredient"]
        dish.allergens = []
        dish.nutrition_facts = {}
        dish.price = 10.0

        # LLM gives wrong overall score (0 instead of calculated)
        mock_response = Mock()
        mock_response.content = '''
        [
          {
            "dish_id": "dish123",
            "overall_score": 0,
            "allergen_safety": {"score": 100, "level": "SAFE", "detected_allergens": [], "reasoning": "Safe"},
            "nutrition_match": {"score": 75, "level": "GOOD", "matched_goals": [], "conflicts": [], "reasoning": "Good"},
            "taste_preference": {"score": 50, "level": "MODERATE", "matched_cuisines": [], "matched_tastes": [], "reasoning": "Moderate"},
            "dietary_pattern": {"score": 80, "level": "GOOD", "user_pattern": "omnivore", "dish_category": "regular", "reasoning": "Good"},
            "recommendation": "Test"
          }
        ]
        '''
        mock_llm.invoke.return_value = mock_response

        user_profile = {"allergens": [], "health_goals": [], "cuisine_preferences": [], "taste_preferences": [], "dietary_pattern": "omnivore"}

        result = calculate_batch_compatibility([dish], user_profile)

        # Calculated: (100*0.4) + (75*0.25) + (50*0.2) + (80*0.15) = 40 + 18.75 + 10 + 12 = 80.75 → 81
        assert result["dish123"].overall_score == 81  # Corrected score


class TestSevenDishLimit:
    """Test 7-dish performance optimization"""

    @patch('app.services.compatibility_service.calculate_batch_compatibility')
    def test_limits_to_seven_dishes(self, mock_batch):
        """Test that scoring limits to 7 dishes"""
        mock_batch.return_value = {}

        state = Mock()
        state.menu_results = Mock()

        # Create 10 mock dishes
        dishes = [Mock(dish_id=f"dish{i}", dish_name=f"Dish {i}") for i in range(10)]
        state.menu_results.menu_results = {"query": dishes}

        state.context = [{"user_allergens": ["peanuts"]}]

        calculate_compatibility_scores(state)

        # Check that batch was called with only 7 dishes
        mock_batch.assert_called_once()
        called_dishes = mock_batch.call_args[1]["dishes"]
        assert len(called_dishes) == 7

    @patch('app.services.compatibility_service.calculate_batch_compatibility')
    def test_processes_all_if_under_seven(self, mock_batch):
        """Test that all dishes are processed if under 7"""
        mock_batch.return_value = {}

        state = Mock()
        state.menu_results = Mock()

        # Create 5 mock dishes
        dishes = [Mock(dish_id=f"dish{i}", dish_name=f"Dish {i}") for i in range(5)]
        state.menu_results.menu_results = {"query": dishes}

        state.context = [{"user_allergens": ["peanuts"]}]

        calculate_compatibility_scores(state)

        # Check that batch was called
        mock_batch.assert_called_once()
        # Get the dishes argument (keyword argument named 'dishes')
        called_dishes = mock_batch.call_args.kwargs.get('dishes') or mock_batch.call_args[0][0]
        assert len(called_dishes) == 5


class TestSafetyOverride:
    """Test allergen safety override logic"""

    @patch('app.services.compatibility_service.llm')
    def test_safety_override_reduces_high_score(self, mock_llm):
        """Test that low allergen score overrides high overall score"""
        dish = Mock()
        dish.dish_id = "dish123"
        dish.dish_name = "Peanut Dish"
        dish.description = "Contains peanuts"
        dish.ingredients = ["peanuts"]
        dish.allergens = ["peanuts"]
        dish.nutrition_facts = {}
        dish.price = 10.0

        # Allergen score is 30 (unsafe), but other scores are high
        mock_response = Mock()
        mock_response.content = '''
        [
          {
            "dish_id": "dish123",
            "overall_score": 100,
            "allergen_safety": {"score": 30, "level": "UNSAFE", "detected_allergens": ["peanuts"], "reasoning": "Contains allergen"},
            "nutrition_match": {"score": 100, "level": "EXCELLENT", "matched_goals": [], "conflicts": [], "reasoning": "Great nutrition"},
            "taste_preference": {"score": 100, "level": "EXCELLENT", "matched_cuisines": [], "matched_tastes": [], "reasoning": "Delicious"},
            "dietary_pattern": {"score": 100, "level": "EXCELLENT", "user_pattern": "omnivore", "dish_category": "regular", "reasoning": "Perfect match"},
            "recommendation": "Avoid due to allergen"
          }
        ]
        '''
        mock_llm.invoke.return_value = mock_response

        user_profile = {"allergens": ["peanuts"], "health_goals": [], "cuisine_preferences": [], "taste_preferences": [], "dietary_pattern": "omnivore"}

        result = calculate_batch_compatibility([dish], user_profile)

        # Safety override should cap at 49
        assert result["dish123"].overall_score < 50
        assert result["dish123"].overall_score == 49


class TestRoundingBehavior:
    """Test score rounding in compatibility calculation"""

    @patch('app.services.compatibility_service.llm')
    def test_rounds_float_scores_to_int(self, mock_llm):
        """Test that float scores are rounded to integers"""
        dish = Mock()
        dish.dish_id = "dish123"
        dish.dish_name = "Test"
        dish.description = "Test"
        dish.ingredients = []
        dish.allergens = []
        dish.nutrition_facts = {}
        dish.price = 10.0

        # LLM returns float scores
        mock_response = Mock()
        mock_response.content = '''
        [
          {
            "dish_id": "dish123",
            "overall_score": 75.7,
            "allergen_safety": {"score": 99.9, "level": "SAFE", "detected_allergens": [], "reasoning": "Safe"},
            "nutrition_match": {"score": 74.3, "level": "GOOD", "matched_goals": [], "conflicts": [], "reasoning": "Good"},
            "taste_preference": {"score": 50.5, "level": "MODERATE", "matched_cuisines": [], "matched_tastes": [], "reasoning": "Ok"},
            "dietary_pattern": {"score": 80.2, "level": "GOOD", "user_pattern": "omnivore", "dish_category": "regular", "reasoning": "Good"},
            "recommendation": "Test"
          }
        ]
        '''
        mock_llm.invoke.return_value = mock_response

        user_profile = {"allergens": [], "health_goals": [], "cuisine_preferences": [], "taste_preferences": [], "dietary_pattern": "omnivore"}

        result = calculate_batch_compatibility([dish], user_profile)

        score = result["dish123"]
        # All scores should be integers
        assert isinstance(score.overall_score, int)
        assert isinstance(score.allergen_safety.score, int)
        assert isinstance(score.nutrition_match.score, int)
        assert isinstance(score.taste_preference.score, int)
        assert isinstance(score.dietary_pattern.score, int)
