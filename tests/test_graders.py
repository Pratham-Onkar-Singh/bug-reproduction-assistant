"""
Test suite for grader functions.

Tests verify:
- Graders return values in [0.0, 1.0] range
- Graders are deterministic
- Graders correctly score different scenarios
- Partial credit is awarded correctly
- Perfect scores are achievable
"""

import pytest
from server.grader import grade_easy, grade_medium, grade_hard


class TestGradeEasy:
    """Test suite for grade_easy() function."""

    def test_perfect_score(self):
        """Perfect score: crash triggered + correct steps + correct parameter."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["open_upload_page", "upload_file"],
            "parameters": {"file_size": "100MB"},
            "step_count": 2
        }
        score = grade_easy(state)
        assert score == 1.0, f"Expected 1.0, got {score}"

    def test_no_parameters(self):
        """Score with no parameters set."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["open_upload_page", "upload_file"],
            "parameters": {},
            "step_count": 2
        }
        score = grade_easy(state)
        # 0.5 (crash) + 0.3 (both steps) + 0 (no file_size) = 0.8
        assert score == 0.8, f"Expected 0.8, got {score}"

    def test_no_crash(self):
        """Score without triggering crash."""
        state = {
            "crash_triggered": False,
            "steps_taken": ["open_upload_page", "upload_file"],
            "parameters": {"file_size": "100MB"},
            "step_count": 2
        }
        score = grade_easy(state)
        # 0 (no crash) + 0.3 (both steps) + 0.2 (file_size) = 0.5
        assert score == 0.5, f"Expected 0.5, got {score}"

    def test_partial_steps(self):
        """Score with only one correct step."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["open_upload_page"],
            "parameters": {"file_size": "100MB"},
            "step_count": 1
        }
        score = grade_easy(state)
        # 0.5 (crash) + 0.15 (1 of 2 steps) + 0.2 (file_size) = 0.85
        assert score == 0.85, f"Expected 0.85, got {score}"

    def test_no_steps(self):
        """Score with no steps taken."""
        state = {
            "crash_triggered": True,
            "steps_taken": [],
            "parameters": {"file_size": "100MB"},
            "step_count": 0
        }
        score = grade_easy(state)
        # 0.5 (crash) + 0 (no steps) + 0.2 (file_size) = 0.7
        assert score == 0.7, f"Expected 0.7, got {score}"

    def test_wrong_file_size(self):
        """Score with incorrect file size parameter."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["open_upload_page", "upload_file"],
            "parameters": {"file_size": "50MB"},
            "step_count": 2
        }
        score = grade_easy(state)
        # 0.5 (crash) + 0.3 (both steps) + 0 (wrong file_size) = 0.8
        assert score == 0.8, f"Expected 0.8, got {score}"

    def test_zero_score(self):
        """Minimum score: nothing correct."""
        state = {
            "crash_triggered": False,
            "steps_taken": [],
            "parameters": {},
            "step_count": 0
        }
        score = grade_easy(state)
        assert score == 0.0, f"Expected 0.0, got {score}"

    def test_duplicate_steps(self):
        """Steps with duplicates (set operation should dedup)."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["open_upload_page", "open_upload_page", "upload_file"],
            "parameters": {"file_size": "100MB"},
            "step_count": 3
        }
        score = grade_easy(state)
        # Set dedups: {open_upload_page, upload_file} = 2 matches
        # 0.5 (crash) + 0.3 (both steps via set) + 0.2 (file_size) = 1.0
        assert score == 1.0, f"Expected 1.0, got {score}"

    def test_score_in_range(self):
        """All scores should be in [0.0, 1.0]."""
        test_cases = [
            {"crash_triggered": True, "steps_taken": ["open_upload_page"], "parameters": {"file_size": "50MB"}, "step_count": 1},
            {"crash_triggered": False, "steps_taken": ["upload_file"], "parameters": {}, "step_count": 1},
            {"crash_triggered": True, "steps_taken": ["random_step"], "parameters": {"file_size": "100MB"}, "step_count": 1},
        ]
        for state in test_cases:
            score = grade_easy(state)
            assert 0.0 <= score <= 1.0, f"Score {score} out of range for state {state}"


class TestGradeMedium:
    """Test suite for grade_medium() function."""

    def test_perfect_score(self):
        """Perfect score: crash + all steps + all parameters + efficiency."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB"},
            "step_count": 3
        }
        score = grade_medium(state)
        # 0.4 (crash) + 0.3 (all 3 steps) + 0.1 (csv) + 0.1 (file_size) + 0.1 (efficiency 1-3/6=0.5 → 0.05) 
        # Wait, efficiency = max(0, 1 - 3/6) = 0.5, so 0.1*0.5 = 0.05
        # Total = 0.4 + 0.3 + 0.1 + 0.1 + 0.05 = 0.95
        expected = 0.95
        assert score == expected, f"Expected {expected}, got {score}"

    def test_efficiency_max_at_step_6(self):
        """At step 6, efficiency bonus is 0."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB"},
            "step_count": 6
        }
        score = grade_medium(state)
        # 0.4 + 0.3 + 0.1 + 0.1 + 0 (efficiency = 1 - 6/6 = 0) = 0.9
        assert score == 0.9 or score == 0.900, f"Expected 0.9, got {score}"

    def test_no_crash(self):
        """Score without crash triggered."""
        state = {
            "crash_triggered": False,
            "steps_taken": ["login", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB"},
            "step_count": 3
        }
        score = grade_medium(state)
        # 0 (no crash) + 0.3 + 0.1 + 0.1 + 0.05 = 0.55
        assert score == 0.55, f"Expected 0.55, got {score}"

    def test_partial_steps(self):
        """Score with only 2 of 3 required steps."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB"},
            "step_count": 2
        }
        score = grade_medium(state)
        # 0.4 (crash) + 0.2 (2 of 3 steps) + 0.1 + 0.1 + 0.067 (efficiency) ≈ 0.867
        efficiency_bonus = 0.1 * max(0, 1 - 2/6)  # 0.1 * 0.667 = 0.067
        expected = round(0.4 + 0.3*(2/3) + 0.1 + 0.1 + efficiency_bonus, 3)
        assert score == expected, f"Expected {expected}, got {score}"

    def test_missing_parameters(self):
        """Score without some parameters."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv"},  # Missing file_size
            "step_count": 3
        }
        score = grade_medium(state)
        # 0.4 + 0.3 + 0.1 + 0 (no file_size) + 0.05 = 0.85
        assert score == 0.85, f"Expected 0.85, got {score}"

    def test_zero_score(self):
        """Minimum score in medium task (efficiency bonus at step 0)."""
        state = {
            "crash_triggered": False,
            "steps_taken": [],
            "parameters": {},
            "step_count": 0
        }
        score = grade_medium(state)
        # Even with nothing, efficiency bonus at step 0 = 0.1 * (1 - 0/6) = 0.1
        assert score == 0.1, f"Expected 0.1, got {score}"

    def test_score_in_range(self):
        """All scores should be in [0.0, 1.0]."""
        test_cases = [
            {"crash_triggered": True, "steps_taken": ["login"], "parameters": {"file_type": "csv"}, "step_count": 1},
            {"crash_triggered": False, "steps_taken": ["open_upload_page", "upload_file"], "parameters": {"file_size": "100MB"}, "step_count": 2},
            {"crash_triggered": True, "steps_taken": ["login", "open_upload_page", "upload_file", "random"], "parameters": {"file_type": "json"}, "step_count": 4},
        ]
        for state in test_cases:
            score = grade_medium(state)
            assert 0.0 <= score <= 1.0, f"Score {score} out of range for state {state}"

    def test_deterministic(self):
        """Grader should be deterministic (same input = same output)."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB"},
            "step_count": 3
        }
        score1 = grade_medium(state)
        score2 = grade_medium(state)
        assert score1 == score2, f"Grader not deterministic: {score1} != {score2}"


class TestGradeHard:
    """Test suite for grade_hard() function."""

    def test_perfect_score(self):
        """Perfect score: crash + all steps + all parameters + efficiency."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "set_role_admin", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB", "role": "admin"},
            "step_count": 4
        }
        score = grade_hard(state)
        # 0.4 (crash) + 0.3 (all 4 steps) + 0.05 (csv) + 0.05 (file_size) + 0.1 (role) + 0.1*max(0, 1-4/6)
        # = 0.4 + 0.3 + 0.05 + 0.05 + 0.1 + 0.1*0.333 = 0.4 + 0.3 + 0.05 + 0.05 + 0.1 + 0.033 ≈ 0.933
        efficiency_bonus = 0.1 * max(0, 1 - 4/6)
        expected = round(0.4 + 0.3 + 0.05 + 0.05 + 0.1 + efficiency_bonus, 3)
        assert score == expected, f"Expected {expected}, got {score}"

    def test_missing_role_parameter(self):
        """Score without admin role parameter."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "set_role_admin", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB"},  # Missing role
            "step_count": 4
        }
        score = grade_hard(state)
        # 0.4 + 0.3 + 0.05 + 0.05 + 0 (no role) + 0.033 ≈ 0.783
        efficiency_bonus = 0.1 * max(0, 1 - 4/6)
        expected = round(0.4 + 0.3 + 0.05 + 0.05 + 0 + efficiency_bonus, 3)
        assert score == expected, f"Expected {expected}, got {score}"

    def test_partial_steps(self):
        """Score with only 3 of 4 required steps."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "set_role_admin", "upload_file"],  # Missing open_upload_page
            "parameters": {"file_type": "csv", "file_size": "100MB", "role": "admin"},
            "step_count": 3
        }
        score = grade_hard(state)
        # 0.4 + 0.225 (3 of 4 steps) + 0.05 + 0.05 + 0.1 + 0.050 (efficiency) ≈ 0.875
        efficiency_bonus = 0.1 * max(0, 1 - 3/6)
        expected = round(0.4 + 0.3*(3/4) + 0.05 + 0.05 + 0.1 + efficiency_bonus, 3)
        assert score == expected, f"Expected {expected}, got {score}"

    def test_no_crash(self):
        """Score without triggering crash."""
        state = {
            "crash_triggered": False,
            "steps_taken": ["login", "set_role_admin", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB", "role": "admin"},
            "step_count": 4
        }
        score = grade_hard(state)
        # 0 (no crash) + 0.3 + 0.05 + 0.05 + 0.1 + 0.033 ≈ 0.533
        efficiency_bonus = 0.1 * max(0, 1 - 4/6)
        expected = round(0 + 0.3 + 0.05 + 0.05 + 0.1 + efficiency_bonus, 3)
        assert score == expected, f"Expected {expected}, got {score}"

    def test_zero_score(self):
        """Minimum score in hard task (efficiency bonus at step 0)."""
        state = {
            "crash_triggered": False,
            "steps_taken": [],
            "parameters": {},
            "step_count": 0
        }
        score = grade_hard(state)
        # Even with nothing, efficiency bonus at step 0 = 0.1 * (1 - 0/6) = 0.1
        assert score == 0.1, f"Expected 0.1, got {score}"

    def test_efficiency_bonus_progression(self):
        """Verify efficiency bonus scales with step_count."""
        # Test at different step counts
        test_cases = [
            (1, 0.1 * (1 - 1/6)),  # step 1
            (2, 0.1 * (1 - 2/6)),  # step 2
            (3, 0.1 * (1 - 3/6)),  # step 3
            (6, 0.1 * (1 - 6/6)),  # step 6 (no bonus)
        ]
        
        for step_count, expected_efficiency_bonus in test_cases:
            state = {
                "crash_triggered": False,
                "steps_taken": [],
                "parameters": {},
                "step_count": step_count
            }
            score = grade_hard(state)
            expected_score = round(expected_efficiency_bonus, 3)
            assert score == expected_score, f"Step {step_count}: expected {expected_score}, got {score}"

    def test_score_in_range(self):
        """All scores should be in [0.0, 1.0]."""
        test_cases = [
            {"crash_triggered": True, "steps_taken": ["login"], "parameters": {"role": "admin"}, "step_count": 1},
            {"crash_triggered": False, "steps_taken": ["login", "set_role_admin"], "parameters": {"file_type": "csv"}, "step_count": 2},
            {"crash_triggered": True, "steps_taken": ["login", "set_role_admin", "open_upload_page", "upload_file"], "parameters": {"file_type": "csv", "file_size": "100MB", "role": "admin"}, "step_count": 4},
        ]
        for state in test_cases:
            score = grade_hard(state)
            assert 0.0 <= score <= 1.0, f"Score {score} out of range for state {state}"

    def test_deterministic(self):
        """Grader should be deterministic (same input = same output)."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["login", "set_role_admin", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB", "role": "admin"},
            "step_count": 4
        }
        score1 = grade_hard(state)
        score2 = grade_hard(state)
        assert score1 == score2, f"Grader not deterministic: {score1} != {score2}"


class TestGraderComparison:
    """Compare behavior across graders."""

    def test_difficulty_progression(self):
        """Verify that hard tasks are harder than medium, which are harder than easy."""
        # Perfect score in each task
        easy_perfect = {
            "crash_triggered": True,
            "steps_taken": ["open_upload_page", "upload_file"],
            "parameters": {"file_size": "100MB"},
            "step_count": 2
        }
        
        medium_perfect = {
            "crash_triggered": True,
            "steps_taken": ["login", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB"},
            "step_count": 3
        }
        
        hard_perfect = {
            "crash_triggered": True,
            "steps_taken": ["login", "set_role_admin", "open_upload_page", "upload_file"],
            "parameters": {"file_type": "csv", "file_size": "100MB", "role": "admin"},
            "step_count": 4
        }
        
        easy_score = grade_easy(easy_perfect)
        medium_score = grade_medium(medium_perfect)
        hard_score = grade_hard(hard_perfect)
        
        # All should be achievable (>= 0.9)
        assert easy_score >= 0.9, f"Easy perfect score too low: {easy_score}"
        assert medium_score >= 0.9, f"Medium perfect score too low: {medium_score}"
        assert hard_score >= 0.9, f"Hard perfect score too low: {hard_score}"

    def test_all_graders_return_float(self):
        """Verify all graders return float type."""
        state = {
            "crash_triggered": True,
            "steps_taken": ["open_upload_page"],
            "parameters": {},
            "step_count": 1
        }
        
        easy_score = grade_easy(state)
        medium_score = grade_medium(state)
        hard_score = grade_hard(state)
        
        assert isinstance(easy_score, float), f"grade_easy returned {type(easy_score)}"
        assert isinstance(medium_score, float), f"grade_medium returned {type(medium_score)}"
        assert isinstance(hard_score, float), f"grade_hard returned {type(hard_score)}"
