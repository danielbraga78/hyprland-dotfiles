import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / ".config/hypr/scripts"),
)

from dynamic_workspaces import workspace_plan


class WorkspacePlanTests(unittest.TestCase):
    def test_keeps_three_baseline_workspaces_without_creating_an_extra(self):
        plan, create_id = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 0},
                {"id": 3, "windows": 1},
            ],
            active_id=1,
        )

        self.assertEqual(plan, {1: True, 2: True, 3: True})
        self.assertIsNone(create_id)

    def test_creates_a_trailing_workspace_when_all_existing_workspaces_are_full(self):
        plan, create_id = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 1},
                {"id": 3, "windows": 1},
            ],
            active_id=3,
        )

        self.assertEqual(create_id, 4)
        self.assertTrue(plan[4])

    def test_reuses_a_gap_before_allocating_a_higher_workspace_number(self):
        plan, create_id = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 1},
                {"id": 3, "windows": 1},
                {"id": 5, "windows": 1},
            ],
            active_id=5,
        )

        self.assertEqual(create_id, 4)
        self.assertTrue(plan[4])

    def test_keeps_only_one_extra_empty_workspace_when_baseline_is_full(self):
        plan, create_id = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 1},
                {"id": 3, "windows": 1},
                {"id": 4, "windows": 0},
                {"id": 5, "windows": 0},
            ],
            active_id=4,
        )

        self.assertTrue(plan[4])
        self.assertFalse(plan[5])
        self.assertIsNone(create_id)

    def test_removes_extra_empty_workspaces_when_a_baseline_is_empty(self):
        plan, create_id = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 0},
                {"id": 3, "windows": 1},
                {"id": 4, "windows": 0},
            ],
            active_id=4,
        )

        self.assertFalse(plan[4])
        self.assertIsNone(create_id)


if __name__ == "__main__":
    unittest.main()
