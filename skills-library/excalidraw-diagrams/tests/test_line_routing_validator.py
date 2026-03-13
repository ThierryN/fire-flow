#!/usr/bin/env python3
"""
Unit tests for the line routing validator.
"""

import sys
import os
import json
import math
import unittest

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from line_routing_validator import (
    LineRoutingValidator, ValidationIssue, Severity,
    Point, Box, LineSegment, Arrow,
    validate_diagram_data
)


def make_diagram(elements):
    """Create a minimal diagram structure with given elements."""
    return {
        "type": "excalidraw",
        "version": 2,
        "elements": elements,
    }


def make_box(id, x, y, width, height, elem_type="rectangle"):
    """Create a box element."""
    return {
        "type": elem_type,
        "id": id,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
    }


def make_arrow(id, x, y, points, elbowed=False, start_binding=None, end_binding=None):
    """Create an arrow element."""
    return {
        "type": "arrow",
        "id": id,
        "x": x,
        "y": y,
        "points": points,
        "elbowed": elbowed,
        "startBinding": {"elementId": start_binding} if start_binding else None,
        "endBinding": {"elementId": end_binding} if end_binding else None,
    }


class TestPoint(unittest.TestCase):
    """Tests for the Point class."""

    def test_point_addition(self):
        p1 = Point(10, 20)
        p2 = Point(5, 15)
        result = p1 + p2
        self.assertEqual(result.x, 15)
        self.assertEqual(result.y, 35)

    def test_point_subtraction(self):
        p1 = Point(10, 20)
        p2 = Point(5, 15)
        result = p1 - p2
        self.assertEqual(result.x, 5)
        self.assertEqual(result.y, 5)

    def test_distance_to(self):
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        self.assertAlmostEqual(p1.distance_to(p2), 5.0)


class TestBox(unittest.TestCase):
    """Tests for the Box class."""

    def test_center(self):
        box = Box(id="b1", x=100, y=100, width=50, height=30, element_type="rectangle")
        center = box.center
        self.assertEqual(center.x, 125)
        self.assertEqual(center.y, 115)

    def test_bounds(self):
        box = Box(id="b1", x=100, y=100, width=50, height=30, element_type="rectangle")
        left, top, right, bottom = box.bounds
        self.assertEqual(left, 100)
        self.assertEqual(top, 100)
        self.assertEqual(right, 150)
        self.assertEqual(bottom, 130)

    def test_contains_point_inside(self):
        box = Box(id="b1", x=100, y=100, width=50, height=30, element_type="rectangle")
        self.assertTrue(box.contains_point(Point(125, 115)))

    def test_contains_point_outside(self):
        box = Box(id="b1", x=100, y=100, width=50, height=30, element_type="rectangle")
        self.assertFalse(box.contains_point(Point(50, 50)))

    def test_contains_point_with_margin(self):
        box = Box(id="b1", x=100, y=100, width=50, height=30, element_type="rectangle")
        # Point just outside, but within margin
        self.assertTrue(box.contains_point(Point(95, 115), margin=10))


class TestLineSegment(unittest.TestCase):
    """Tests for the LineSegment class."""

    def test_horizontal_segment(self):
        seg = LineSegment(Point(0, 0), Point(100, 0))
        self.assertTrue(seg.is_horizontal)
        self.assertFalse(seg.is_vertical)

    def test_vertical_segment(self):
        seg = LineSegment(Point(0, 0), Point(0, 100))
        self.assertFalse(seg.is_horizontal)
        self.assertTrue(seg.is_vertical)

    def test_diagonal_segment(self):
        seg = LineSegment(Point(0, 0), Point(100, 100))
        self.assertFalse(seg.is_horizontal)
        self.assertFalse(seg.is_vertical)

    def test_length(self):
        seg = LineSegment(Point(0, 0), Point(3, 4))
        self.assertAlmostEqual(seg.length, 5.0)

    def test_intersects_box_through(self):
        """Line passing through box center should be detected."""
        seg = LineSegment(Point(0, 50), Point(200, 50))
        box = Box(id="b1", x=80, y=30, width=40, height=40, element_type="rectangle")
        self.assertTrue(seg.intersects_box(box))

    def test_intersects_box_miss(self):
        """Line missing box should not be detected."""
        seg = LineSegment(Point(0, 0), Point(200, 0))
        box = Box(id="b1", x=80, y=30, width=40, height=40, element_type="rectangle")
        self.assertFalse(seg.intersects_box(box))

    def test_segment_intersection(self):
        """Two crossing segments should return intersection point."""
        seg1 = LineSegment(Point(0, 50), Point(100, 50))
        seg2 = LineSegment(Point(50, 0), Point(50, 100))
        intersection = seg1.intersects_segment(seg2)
        self.assertIsNotNone(intersection)
        self.assertAlmostEqual(intersection.x, 50, places=1)
        self.assertAlmostEqual(intersection.y, 50, places=1)

    def test_segment_no_intersection(self):
        """Parallel segments should not intersect."""
        seg1 = LineSegment(Point(0, 0), Point(100, 0))
        seg2 = LineSegment(Point(0, 50), Point(100, 50))
        self.assertIsNone(seg1.intersects_segment(seg2))


class TestLineCrossesBox(unittest.TestCase):
    """Tests for detecting lines that cross through boxes."""

    def test_arrow_through_unconnected_box(self):
        """Arrow passing through a box it's not connected to."""
        # Boxes far apart, with an unconnected box in between
        diagram = make_diagram([
            make_box("box1", 0, 100, 80, 40),       # Left box
            make_box("box2", 400, 100, 80, 40),    # Right box, far away
            make_box("middle", 200, 100, 60, 60),  # Box in the middle, not near endpoints
            make_arrow("arr1", 80, 120, [[0, 0], [320, 0]]),  # Long arrow through middle
        ])

        issues = validate_diagram_data(diagram)
        errors = [i for i in issues if i.severity == Severity.ERROR]

        self.assertGreater(len(errors), 0)
        self.assertTrue(any(i.issue_type == "line_crosses_box" for i in errors))

    def test_arrow_around_box(self):
        """Arrow that routes around a box should not trigger error."""
        diagram = make_diagram([
            make_box("box1", 100, 100, 80, 40),
            make_box("box2", 300, 100, 80, 40),
            # Arrow goes around, not through
            make_arrow("arr1", 180, 140, [[0, 0], [0, 50], [200, 50], [200, 0]]),
        ])

        issues = validate_diagram_data(diagram)
        errors = [i for i in issues if i.severity == Severity.ERROR]

        # Should not have any "line_crosses_box" errors
        box_crossing_errors = [i for i in errors if i.issue_type == "line_crosses_box"]
        self.assertEqual(len(box_crossing_errors), 0)


class TestElbowedLineAngles(unittest.TestCase):
    """Tests for elbowed line entry angle validation."""

    def test_elbowed_perpendicular_entry(self):
        """Elbowed line entering perpendicular to box edge is OK."""
        # Box at (100, 100) with size 80x40
        # Arrow entering from left side, going right then down
        diagram = make_diagram([
            make_box("box1", 100, 100, 80, 40),
            # Start at (50, 120), go right, then perpendicular into left edge
            make_arrow("arr1", 50, 120, [
                [0, 0],      # Start at 50, 120
                [50, 0],     # Go right to 100, 120 (touches left edge)
            ], elbowed=True),
        ])

        issues = validate_diagram_data(diagram)
        elbow_issues = [i for i in issues if i.issue_type == "elbow_not_perpendicular"]

        # Horizontal line entering left edge is perpendicular
        self.assertEqual(len(elbow_issues), 0)

    def test_elbowed_non_perpendicular_entry(self):
        """Elbowed line entering at angle should trigger warning."""
        # Box at (100, 100) with size 80x40
        # Arrow entering at 45 degrees
        diagram = make_diagram([
            make_box("box1", 100, 100, 80, 40),
            # Diagonal entry into box
            make_arrow("arr1", 50, 80, [
                [0, 0],      # Start at 50, 80
                [50, 40],    # End at 100, 120 (diagonal into left edge)
            ], elbowed=True),
        ])

        issues = validate_diagram_data(diagram)
        elbow_issues = [i for i in issues if i.issue_type == "elbow_not_perpendicular"]

        # 45 degree entry should trigger warning
        self.assertGreater(len(elbow_issues), 0)


class TestStraightLineAngles(unittest.TestCase):
    """Tests for non-elbowed line entry angle validation."""

    def test_straight_perpendicular_entry(self):
        """Straight line entering perpendicular is OK."""
        diagram = make_diagram([
            make_box("box1", 100, 100, 80, 40),
            make_arrow("arr1", 50, 120, [[0, 0], [50, 0]], elbowed=False),
        ])

        issues = validate_diagram_data(diagram)
        angle_issues = [i for i in issues if i.issue_type == "bad_entry_angle"]
        self.assertEqual(len(angle_issues), 0)

    def test_straight_shallow_angle_entry(self):
        """Straight line entering at shallow angle should warn."""
        # Box at (100, 100), line enters left edge at bad angle
        # Left edge has inward normal (1, 0) - perpendicular entry is horizontal
        # A line coming in at >45° from horizontal should warn
        #
        # Direction (10, 60) -> angle from horizontal = atan(60/10) = 80°
        # Which is 80° from perpendicular (horizontal) - should trigger
        diagram = make_diagram([
            make_box("box1", 100, 100, 80, 40),
            # Start at (90, 40), end at (100, 100) - enters left edge from above
            # Direction is (10, 60), about 80° from horizontal
            make_arrow("arr1", 90, 40, [[0, 0], [10, 70]], elbowed=False),
        ])

        issues = validate_diagram_data(diagram)
        angle_issues = [i for i in issues if i.issue_type == "bad_entry_angle"]

        # Should detect the bad angle (more than 45 degrees from perpendicular)
        self.assertGreater(len(angle_issues), 0)


class TestLineCrossings(unittest.TestCase):
    """Tests for detecting line crossings."""

    def test_crossing_lines_detected(self):
        """Two crossing arrows should be detected."""
        diagram = make_diagram([
            make_arrow("arr1", 0, 50, [[0, 0], [100, 0]]),     # Horizontal
            make_arrow("arr2", 50, 0, [[0, 0], [0, 100]]),    # Vertical, crosses arr1
        ])

        issues = validate_diagram_data(diagram)
        crossing_issues = [i for i in issues if i.issue_type == "line_crossing"]

        self.assertGreater(len(crossing_issues), 0)

    def test_parallel_lines_no_crossing(self):
        """Parallel arrows should not trigger crossing warning."""
        diagram = make_diagram([
            make_arrow("arr1", 0, 50, [[0, 0], [100, 0]]),
            make_arrow("arr2", 0, 100, [[0, 0], [100, 0]]),  # Parallel
        ])

        issues = validate_diagram_data(diagram)
        crossing_issues = [i for i in issues if i.issue_type == "line_crossing"]

        self.assertEqual(len(crossing_issues), 0)


class TestCouldBeStraight(unittest.TestCase):
    """Tests for detecting lines that could be straight but aren't."""

    def test_nearly_vertical_line(self):
        """Line that's almost vertical should trigger info."""
        # The could_be_straight check requires:
        # 1. dx < COULD_BE_STRAIGHT_THRESHOLD (10)
        # 2. dy > dx * 3
        # 3. NOT already is_vertical (within 5° of 90°)
        #
        # For a line 100px long with 9px offset: angle = atan(9/100) = 5.1°
        # This is just outside the is_vertical tolerance, so should warn.
        diagram = make_diagram([
            make_arrow("arr1", 100, 0, [[0, 0], [9, 100]], elbowed=False),
        ])

        issues = validate_diagram_data(diagram)
        straight_issues = [i for i in issues if i.issue_type == "could_be_straight"]

        self.assertGreater(len(straight_issues), 0)
        self.assertEqual(straight_issues[0].details["suggested"], "vertical")

    def test_nearly_horizontal_line(self):
        """Line that's almost horizontal should trigger info."""
        # Same logic as vertical but rotated
        diagram = make_diagram([
            make_arrow("arr1", 0, 100, [[0, 0], [100, 9]], elbowed=False),
        ])

        issues = validate_diagram_data(diagram)
        straight_issues = [i for i in issues if i.issue_type == "could_be_straight"]

        self.assertGreater(len(straight_issues), 0)
        self.assertEqual(straight_issues[0].details["suggested"], "horizontal")

    def test_intentionally_diagonal_line(self):
        """Intentionally diagonal line should not trigger."""
        diagram = make_diagram([
            make_arrow("arr1", 0, 0, [[0, 0], [100, 100]], elbowed=False),
        ])

        issues = validate_diagram_data(diagram)
        straight_issues = [i for i in issues if i.issue_type == "could_be_straight"]

        self.assertEqual(len(straight_issues), 0)


class TestValidatorSummary(unittest.TestCase):
    """Tests for validation summary generation."""

    def test_summary_counts(self):
        """Summary should correctly count issues by type and severity."""
        diagram = make_diagram([
            make_box("box1", 100, 100, 80, 40),
            make_box("box2", 300, 100, 80, 40),
            make_box("middle", 190, 100, 40, 40),
            make_arrow("arr1", 180, 120, [[0, 0], [200, 0]]),
        ])

        validator = LineRoutingValidator(diagram_data=diagram)
        validator.validate()
        summary = validator.get_summary()

        self.assertIn("total_issues", summary)
        self.assertIn("errors", summary)
        self.assertIn("warnings", summary)
        self.assertIn("info", summary)
        self.assertIn("by_type", summary)
        self.assertIn("arrows_checked", summary)
        self.assertIn("boxes_checked", summary)


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
