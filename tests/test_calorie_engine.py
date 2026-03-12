"""
FitMY Test Suite: Calorie Engine

Tests for BMR, TDEE, and macro split calculations.
These are deterministic — results must be exact.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from execution.calculate_bmr import calculate_bmr
from execution.macro_split import calculate_macro_split


class TestCalculateBMR:
    """Tests for the Mifflin-St Jeor BMR calculator."""

    def test_male_bmr(self):
        """Male, 80kg, 175cm, 25 years old."""
        # BMR = (10 × 80) + (6.25 × 175) - (5 × 25) + 5
        # BMR = 800 + 1093.75 - 125 + 5 = 1773.75 → 1774
        result = calculate_bmr("male", 80, 175, 25)
        assert result == 1774

    def test_female_bmr(self):
        """Female, 60kg, 160cm, 30 years old."""
        # BMR = (10 × 60) + (6.25 × 160) - (5 × 30) - 161
        # BMR = 600 + 1000 - 150 - 161 = 1289
        result = calculate_bmr("female", 60, 160, 30)
        assert result == 1289

    def test_case_insensitive_gender(self):
        """Gender should be case-insensitive."""
        result1 = calculate_bmr("Male", 80, 175, 25)
        result2 = calculate_bmr("MALE", 80, 175, 25)
        result3 = calculate_bmr("male", 80, 175, 25)
        assert result1 == result2 == result3

    def test_invalid_gender_raises(self):
        """Invalid gender should raise ValueError."""
        with pytest.raises(ValueError, match="Gender must be 'male' or 'female'"):
            calculate_bmr("other", 80, 175, 25)

    def test_weight_too_low_raises(self):
        """Weight below 30kg should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_bmr("male", 20, 175, 25)

    def test_weight_too_high_raises(self):
        """Weight above 300kg should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_bmr("male", 350, 175, 25)

    def test_age_too_young_raises(self):
        """Age below 13 should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_bmr("male", 80, 175, 10)

    def test_height_too_short_raises(self):
        """Height below 100cm should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_bmr("male", 80, 90, 25)


class TestMacroSplit:
    """Tests for macro split calculations."""

    def test_fat_loss_split(self):
        """Fat loss: 40P / 30C / 30F at 2000 kcal."""
        result = calculate_macro_split(2000, "fat_loss")
        assert result["protein_g"] == 200  # 800 kcal / 4
        assert result["carbs_g"] == 150    # 600 kcal / 4
        assert result["fats_g"] == 67      # 600 kcal / 9 ≈ 66.67 → 67

    def test_maintenance_split(self):
        """Maintenance: 30P / 40C / 30F at 2000 kcal."""
        result = calculate_macro_split(2000, "maintenance")
        assert result["protein_g"] == 150
        assert result["carbs_g"] == 200
        assert result["fats_g"] == 67

    def test_muscle_gain_split(self):
        """Muscle gain: 35P / 45C / 20F at 2500 kcal."""
        result = calculate_macro_split(2500, "muscle_gain")
        assert result["protein_g"] == 219  # 875 kcal / 4 = 218.75 → 219
        assert result["carbs_g"] == 281    # 1125 kcal / 4 = 281.25 → 281
        assert result["fats_g"] == 56      # 500 kcal / 9 = 55.56 → 56

    def test_invalid_goal_raises(self):
        """Invalid goal should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_macro_split(2000, "bulk")

    def test_calorie_target_too_low_raises(self):
        """Calorie target below 1200 should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_macro_split(1000, "fat_loss")
