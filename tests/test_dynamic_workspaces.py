import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / ".config/hypr/scripts"),
)

from dynamic_workspaces import active_workspace_after_compaction, workspace_plan


class WorkspacePlanTests(unittest.TestCase):
    def test_keeps_focus_on_a_gap_that_will_receive_moved_windows(self):
        destination = active_workspace_after_compaction(
            active_id=3,
            occupied_ids={1, 2, 4},
            moves={4: 3},
        )

        self.assertIsNone(destination)

    def test_follows_the_active_windows_when_their_workspace_is_compacted(self):
        destination = active_workspace_after_compaction(
            active_id=4,
            occupied_ids={1, 2, 4},
            moves={4: 3},
        )

        self.assertEqual(destination, 3)

    def test_moves_focus_out_of_an_extra_empty_workspace_before_removing_it(self):
        destination = active_workspace_after_compaction(
            active_id=6,
            occupied_ids={1, 2, 3, 4},
            moves={},
        )

        self.assertEqual(destination, 5)

    def test_moves_windows_from_a_later_workspace_into_a_gap(self):
        plan, _, moves = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 1},
                {"id": 3, "windows": 0},
                {"id": 4, "windows": 2},
            ],
        )

        self.assertEqual(moves, {4: 3})
        self.assertTrue(plan[4])

    def test_compacts_multiple_gaps_in_workspace_order(self):
        _, _, moves = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 0},
                {"id": 3, "windows": 1},
                {"id": 4, "windows": 0},
                {"id": 5, "windows": 1},
            ],
        )

        self.assertEqual(moves, {3: 2, 5: 3})

    def test_keeps_three_baseline_workspaces_without_creating_an_extra(self):
        plan, create_id, moves = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 0},
                {"id": 3, "windows": 1},
            ],
        )

        self.assertEqual(plan, {1: True, 2: True, 3: True})
        self.assertIsNone(create_id)
        self.assertEqual(moves, {3: 2})

    def test_creates_a_trailing_workspace_when_all_existing_workspaces_are_full(self):
        plan, create_id, moves = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 1},
                {"id": 3, "windows": 1},
            ],
        )

        self.assertEqual(create_id, 4)
        self.assertTrue(plan[4])
        self.assertEqual(moves, {})

    def test_reuses_a_gap_before_allocating_a_higher_workspace_number(self):
        plan, create_id, moves = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 1},
                {"id": 3, "windows": 1},
                {"id": 5, "windows": 1},
            ],
        )

        self.assertIsNone(create_id)
        self.assertTrue(plan[5])
        self.assertEqual(moves, {5: 4})

    def test_keeps_only_one_extra_empty_workspace_when_baseline_is_full(self):
        plan, create_id, moves = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 1},
                {"id": 3, "windows": 1},
                {"id": 4, "windows": 0},
                {"id": 5, "windows": 0},
            ],
        )

        self.assertTrue(plan[4])
        self.assertFalse(plan[5])
        self.assertIsNone(create_id)
        self.assertEqual(moves, {})

    def test_removes_extra_empty_workspaces_when_a_baseline_is_empty(self):
        plan, create_id, moves = workspace_plan(
            [
                {"id": 1, "windows": 1},
                {"id": 2, "windows": 0},
                {"id": 3, "windows": 1},
                {"id": 4, "windows": 0},
            ],
        )

        self.assertFalse(plan[4])
        self.assertIsNone(create_id)
        self.assertEqual(moves, {3: 2})


if __name__ == "__main__":
    unittest.main()
