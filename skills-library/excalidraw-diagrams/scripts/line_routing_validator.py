#!/usr/bin/env python3
"""
Line Routing Validator for Excalidraw Diagrams

Detects common routing issues in diagram arrows/lines:
1. Lines crossing through boxes (instead of routing around)
2. Elbowed lines not entering boxes at 90 degrees
3. Non-elbowed lines entering boxes outside 45-degree tolerance
4. Unnecessary line crossings
5. Lines at angles when they could be straight

Usage:
    from line_routing_validator import validate_diagram, ValidationIssue

    issues = validate_diagram("diagram.excalidraw")
    for issue in issues:
        print(f"{issue.severity}: {issue.message}")
"""

import json
import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Tuple, Optional, Set


class Severity(Enum):
    ERROR = "error"      # Definitely wrong - lines through boxes
    WARNING = "warning"  # Likely wrong - bad angles, unnecessary crossings
    INFO = "info"        # Could be improved - suboptimal routing


@dataclass
class Point:
    """2D point with utility methods."""
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def distance_to(self, other: "Point") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __repr__(self) -> str:
        return f"({self.x:.1f}, {self.y:.1f})"


@dataclass
class Box:
    """Represents a box/shape in the diagram."""
    id: str
    x: float
    y: float
    width: float
    height: float
    element_type: str  # rectangle, ellipse, diamond

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """Return (left, top, right, bottom)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def contains_point(self, p: Point, margin: float = 0) -> bool:
        """Check if point is inside the box (with optional margin)."""
        left, top, right, bottom = self.bounds
        return (left - margin <= p.x <= right + margin and
                top - margin <= p.y <= bottom + margin)

    def get_edge_normal(self, p: Point) -> Tuple[str, Point]:
        """Get the closest edge and its outward normal for a point near the box."""
        cx, cy = self.center.x, self.center.y
        left, top, right, bottom = self.bounds

        # Determine which edge is closest
        distances = {
            "left": abs(p.x - left),
            "right": abs(p.x - right),
            "top": abs(p.y - top),
            "bottom": abs(p.y - bottom),
        }
        closest_edge = min(distances, key=distances.get)

        normals = {
            "left": Point(-1, 0),
            "right": Point(1, 0),
            "top": Point(0, -1),
            "bottom": Point(0, 1),
        }
        return closest_edge, normals[closest_edge]


@dataclass
class LineSegment:
    """A segment of a line/arrow."""
    start: Point
    end: Point

    @property
    def direction(self) -> Point:
        """Normalized direction vector."""
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        length = math.sqrt(dx*dx + dy*dy)
        if length < 0.001:
            return Point(0, 0)
        return Point(dx / length, dy / length)

    @property
    def length(self) -> float:
        return self.start.distance_to(self.end)

    @property
    def angle(self) -> float:
        """Angle in radians from horizontal."""
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        return math.atan2(dy, dx)

    @property
    def is_horizontal(self) -> bool:
        """Check if segment is roughly horizontal (within 5 degrees)."""
        angle = abs(self.angle)
        return angle < math.radians(5) or angle > math.radians(175)

    @property
    def is_vertical(self) -> bool:
        """Check if segment is roughly vertical (within 5 degrees)."""
        angle = abs(self.angle)
        return abs(angle - math.pi/2) < math.radians(5)

    @property
    def is_orthogonal(self) -> bool:
        """Check if segment is horizontal or vertical."""
        return self.is_horizontal or self.is_vertical

    def intersects_box(self, box: Box, exclude_endpoints: bool = True) -> bool:
        """Check if this segment passes through a box interior."""
        left, top, right, bottom = box.bounds

        # Use parametric line intersection
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y

        # Skip if segment is too short
        if self.length < 1:
            return False

        # Check intersection with each edge of the box
        # We're looking for segments that cross THROUGH the box, not just touch it

        # Sample points along the segment
        num_samples = max(10, int(self.length / 5))
        interior_hits = 0

        for i in range(1, num_samples):  # Skip endpoints
            t = i / num_samples
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)

            # Check if point is strictly inside box (with small margin)
            margin = 2  # pixels
            if (left + margin < px < right - margin and
                top + margin < py < bottom - margin):
                interior_hits += 1

        # Consider it a crossing if significant portion is inside
        return interior_hits >= 2

    def intersects_segment(self, other: "LineSegment") -> Optional[Point]:
        """Check if two segments intersect, return intersection point or None."""
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y
        x3, y3 = other.start.x, other.start.y
        x4, y4 = other.end.x, other.end.y

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 0.0001:
            return None  # Parallel

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        # Check if intersection is within both segments (with small margin for endpoints)
        margin = 0.05  # Allow slight overlap at endpoints
        if margin < t < 1 - margin and margin < u < 1 - margin:
            ix = x1 + t * (x2 - x1)
            iy = y1 + t * (y2 - y1)
            return Point(ix, iy)

        return None


@dataclass
class Arrow:
    """Represents an arrow/line in the diagram."""
    id: str
    x: float
    y: float
    points: List[Point]  # Relative to (x, y)
    elbowed: bool
    start_binding: Optional[str]  # ID of connected element
    end_binding: Optional[str]

    @property
    def absolute_points(self) -> List[Point]:
        """Get points in absolute coordinates."""
        return [Point(self.x + p.x, self.y + p.y) for p in self.points]

    @property
    def segments(self) -> List[LineSegment]:
        """Get all line segments in this arrow."""
        abs_points = self.absolute_points
        return [LineSegment(abs_points[i], abs_points[i+1])
                for i in range(len(abs_points) - 1)]

    @property
    def start_point(self) -> Point:
        return self.absolute_points[0]

    @property
    def end_point(self) -> Point:
        return self.absolute_points[-1]


@dataclass
class ValidationIssue:
    """A detected routing issue."""
    severity: Severity
    issue_type: str
    message: str
    arrow_id: str
    location: Optional[Point] = None
    details: Optional[dict] = None

    def __repr__(self) -> str:
        loc = f" at {self.location}" if self.location else ""
        return f"[{self.severity.value.upper()}] {self.issue_type}: {self.message}{loc}"


class LineRoutingValidator:
    """Validates line routing in Excalidraw diagrams."""

    # Configuration thresholds
    ELBOW_ANGLE_TOLERANCE = 5  # degrees - elbowed lines should be within 5° of 90°
    STRAIGHT_ANGLE_TOLERANCE = 45  # degrees - non-elbowed entry angle tolerance
    COULD_BE_STRAIGHT_THRESHOLD = 10  # pixels - if endpoints are this close in one axis
    MIN_SEGMENT_LENGTH = 5  # pixels - ignore very short segments

    def __init__(self, diagram_path: Optional[str] = None, diagram_data: Optional[dict] = None):
        """Initialize with either a file path or diagram data dict."""
        if diagram_path:
            with open(diagram_path) as f:
                self.data = json.load(f)
            self.path = diagram_path
        elif diagram_data:
            self.data = diagram_data
            self.path = "<data>"
        else:
            raise ValueError("Must provide either diagram_path or diagram_data")

        self.boxes: List[Box] = []
        self.arrows: List[Arrow] = []
        self.issues: List[ValidationIssue] = []

        self._parse_elements()

    def _parse_elements(self):
        """Parse boxes and arrows from the diagram."""
        for elem in self.data.get("elements", []):
            elem_type = elem.get("type")
            elem_id = elem.get("id", "unknown")

            if elem_type in ("rectangle", "ellipse", "diamond"):
                self.boxes.append(Box(
                    id=elem_id,
                    x=elem.get("x", 0),
                    y=elem.get("y", 0),
                    width=elem.get("width", 0),
                    height=elem.get("height", 0),
                    element_type=elem_type,
                ))
            elif elem_type == "arrow":
                points = [Point(p[0], p[1]) for p in elem.get("points", [[0, 0]])]

                # Extract binding IDs
                start_binding = None
                end_binding = None
                if elem.get("startBinding"):
                    start_binding = elem["startBinding"].get("elementId")
                if elem.get("endBinding"):
                    end_binding = elem["endBinding"].get("elementId")

                self.arrows.append(Arrow(
                    id=elem_id,
                    x=elem.get("x", 0),
                    y=elem.get("y", 0),
                    points=points,
                    elbowed=elem.get("elbowed", False),
                    start_binding=start_binding,
                    end_binding=end_binding,
                ))

    def validate(self) -> List[ValidationIssue]:
        """Run all validation checks and return issues found."""
        self.issues = []

        self._check_lines_crossing_boxes()
        self._check_entry_angles()
        self._check_line_crossings()
        self._check_could_be_straight()

        return self.issues

    def _get_connected_boxes(self, arrow: Arrow) -> Set[str]:
        """Get IDs of boxes this arrow connects to."""
        connected = set()
        if arrow.start_binding:
            connected.add(arrow.start_binding)
        if arrow.end_binding:
            connected.add(arrow.end_binding)

        # Also check proximity to box edges
        for box in self.boxes:
            if box.contains_point(arrow.start_point, margin=10):
                connected.add(box.id)
            if box.contains_point(arrow.end_point, margin=10):
                connected.add(box.id)

        return connected

    def _check_lines_crossing_boxes(self):
        """Check for lines that pass through boxes they shouldn't."""
        for arrow in self.arrows:
            connected = self._get_connected_boxes(arrow)

            for segment in arrow.segments:
                if segment.length < self.MIN_SEGMENT_LENGTH:
                    continue

                for box in self.boxes:
                    # Skip boxes this arrow is connected to
                    if box.id in connected:
                        continue

                    if segment.intersects_box(box):
                        self.issues.append(ValidationIssue(
                            severity=Severity.ERROR,
                            issue_type="line_crosses_box",
                            message=f"Line segment crosses through box",
                            arrow_id=arrow.id,
                            location=box.center,
                            details={"box_id": box.id},
                        ))

    def _check_entry_angles(self):
        """Check that lines enter boxes at appropriate angles."""
        for arrow in self.arrows:
            segments = arrow.segments
            if not segments:
                continue

            # Check start entry angle
            start_segment = segments[0]
            if start_segment.length >= self.MIN_SEGMENT_LENGTH:
                self._check_single_entry_angle(
                    arrow, start_segment, arrow.start_point, is_start=True
                )

            # Check end entry angle
            end_segment = segments[-1]
            if end_segment.length >= self.MIN_SEGMENT_LENGTH:
                self._check_single_entry_angle(
                    arrow, end_segment, arrow.end_point, is_start=False
                )

    def _check_single_entry_angle(self, arrow: Arrow, segment: LineSegment,
                                   entry_point: Point, is_start: bool):
        """Check entry angle for a single endpoint."""
        # Find the box this point is entering
        target_box = None
        for box in self.boxes:
            if box.contains_point(entry_point, margin=15):
                target_box = box
                break

        if not target_box:
            return  # Not connected to a box

        # Get the edge and normal
        edge, normal = target_box.get_edge_normal(entry_point)

        # Calculate the angle between segment direction and the normal
        # We want the direction of the line as it approaches the box
        if is_start:
            # For start point, the arrow LEAVES from here, so the approach
            # direction is from the second point toward the first
            direction = segment.direction  # Points away from box
        else:
            # For end point, the arrow ARRIVES here
            direction = segment.direction  # Points toward box

        # We want angle from perpendicular entry, so compare with inward normal
        # The inward normal is opposite of the outward normal
        inward_normal = Point(-normal.x, -normal.y)

        # For the entry to be perpendicular, direction should align with inward normal
        # We compute the acute angle between them
        dot = abs(direction.x * inward_normal.x + direction.y * inward_normal.y)
        # Clamp to avoid floating point issues
        dot = max(0, min(1, dot))
        angle_from_perpendicular = math.degrees(math.acos(dot))

        if arrow.elbowed:
            # Elbowed arrows should enter perpendicular to the box edge
            # angle_from_perpendicular should be close to 0
            if angle_from_perpendicular > self.ELBOW_ANGLE_TOLERANCE:
                self.issues.append(ValidationIssue(
                    severity=Severity.WARNING,
                    issue_type="elbow_not_perpendicular",
                    message=f"Elbowed line enters box at {angle_from_perpendicular:.1f}° from perpendicular (should be < {self.ELBOW_ANGLE_TOLERANCE}°)",
                    arrow_id=arrow.id,
                    location=entry_point,
                    details={
                        "angle": angle_from_perpendicular,
                        "edge": edge,
                        "is_start": is_start,
                    },
                ))
        else:
            # Non-elbowed lines should enter within 45 degrees of perpendicular
            if angle_from_perpendicular > self.STRAIGHT_ANGLE_TOLERANCE:
                self.issues.append(ValidationIssue(
                    severity=Severity.WARNING,
                    issue_type="bad_entry_angle",
                    message=f"Line enters box at {angle_from_perpendicular:.1f}° from perpendicular (should be < {self.STRAIGHT_ANGLE_TOLERANCE}°)",
                    arrow_id=arrow.id,
                    location=entry_point,
                    details={
                        "angle": angle_from_perpendicular,
                        "edge": edge,
                        "is_start": is_start,
                    },
                ))

    def _check_line_crossings(self):
        """Check for unnecessary line crossings between arrows."""
        all_segments = []
        for arrow in self.arrows:
            for seg in arrow.segments:
                if seg.length >= self.MIN_SEGMENT_LENGTH:
                    all_segments.append((arrow.id, seg))

        crossings = []
        checked = set()

        for i, (id1, seg1) in enumerate(all_segments):
            for j, (id2, seg2) in enumerate(all_segments):
                if i >= j or id1 == id2:
                    continue

                pair_key = (min(id1, id2), max(id1, id2))
                if pair_key in checked:
                    continue
                checked.add(pair_key)

                intersection = seg1.intersects_segment(seg2)
                if intersection:
                    crossings.append((id1, id2, intersection))

        for id1, id2, point in crossings:
            self.issues.append(ValidationIssue(
                severity=Severity.WARNING,
                issue_type="line_crossing",
                message=f"Lines cross each other (arrows {id1[:8]}... and {id2[:8]}...)",
                arrow_id=id1,
                location=point,
                details={"other_arrow_id": id2},
            ))

    def _check_could_be_straight(self):
        """Check for lines that are angled but could be straight."""
        for arrow in self.arrows:
            # Only check non-elbowed arrows with exactly 2 points (one segment)
            if arrow.elbowed or len(arrow.points) != 2:
                continue

            segment = arrow.segments[0]
            if segment.length < self.MIN_SEGMENT_LENGTH:
                continue

            # Check if line is nearly horizontal or vertical but not quite
            dx = abs(segment.end.x - segment.start.x)
            dy = abs(segment.end.y - segment.start.y)

            # If one dimension is very small relative to the other, it could be straight
            if dx < self.COULD_BE_STRAIGHT_THRESHOLD and dy > dx * 3:
                # Could be vertical
                if not segment.is_vertical:
                    self.issues.append(ValidationIssue(
                        severity=Severity.INFO,
                        issue_type="could_be_straight",
                        message=f"Line could be vertical (dx={dx:.1f}px)",
                        arrow_id=arrow.id,
                        location=segment.start,
                        details={"suggested": "vertical", "offset": dx},
                    ))
            elif dy < self.COULD_BE_STRAIGHT_THRESHOLD and dx > dy * 3:
                # Could be horizontal
                if not segment.is_horizontal:
                    self.issues.append(ValidationIssue(
                        severity=Severity.INFO,
                        issue_type="could_be_straight",
                        message=f"Line could be horizontal (dy={dy:.1f}px)",
                        arrow_id=arrow.id,
                        location=segment.start,
                        details={"suggested": "horizontal", "offset": dy},
                    ))

    def get_summary(self) -> dict:
        """Get a summary of validation results."""
        by_severity = {s: [] for s in Severity}
        by_type = {}

        for issue in self.issues:
            by_severity[issue.severity].append(issue)
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)

        return {
            "total_issues": len(self.issues),
            "errors": len(by_severity[Severity.ERROR]),
            "warnings": len(by_severity[Severity.WARNING]),
            "info": len(by_severity[Severity.INFO]),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "arrows_checked": len(self.arrows),
            "boxes_checked": len(self.boxes),
        }


def validate_diagram(path: str) -> List[ValidationIssue]:
    """Convenience function to validate a diagram file."""
    validator = LineRoutingValidator(diagram_path=path)
    return validator.validate()


def validate_diagram_data(data: dict) -> List[ValidationIssue]:
    """Convenience function to validate diagram data."""
    validator = LineRoutingValidator(diagram_data=data)
    return validator.validate()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python line_routing_validator.py <diagram.excalidraw> [...]")
        sys.exit(1)

    total_issues = 0

    for path in sys.argv[1:]:
        print(f"\n{'='*60}")
        print(f"Validating: {path}")
        print('='*60)

        try:
            validator = LineRoutingValidator(diagram_path=path)
            issues = validator.validate()
            summary = validator.get_summary()

            print(f"\nSummary: {summary['total_issues']} issues "
                  f"({summary['errors']} errors, {summary['warnings']} warnings, {summary['info']} info)")
            print(f"Checked {summary['arrows_checked']} arrows and {summary['boxes_checked']} boxes")

            if issues:
                print("\nIssues found:")
                for issue in sorted(issues, key=lambda i: (i.severity.value, i.issue_type)):
                    print(f"  {issue}")
            else:
                print("\nNo routing issues detected!")

            total_issues += len(issues)

        except Exception as e:
            print(f"Error validating {path}: {e}")
            total_issues += 1

    sys.exit(1 if total_issues > 0 else 0)
