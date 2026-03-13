#!/usr/bin/env python3
"""
Excalidraw Diagram Generator

A Python library for programmatically generating Excalidraw diagrams.
Outputs .excalidraw JSON files that can be opened in Excalidraw.

Usage:
    from excalidraw_generator import Diagram, Box, Arrow, Text

    d = Diagram()
    box1 = d.box(100, 100, "Start", color="blue")
    box2 = d.box(300, 100, "End", color="green")
    d.arrow(box1, box2, "flow")
    d.save("my_diagram.excalidraw")
"""

import json
import random
import math
import uuid
from dataclasses import dataclass, field
from typing import Optional, Literal, Any, Union, List
from pathlib import Path


# ============================================================================
# Constants (from Excalidraw source)
# ============================================================================

FONT_FAMILY = {
    "hand": 1,       # Virgil - hand-drawn style
    "normal": 2,     # Helvetica - clean system font
    "code": 3,       # Cascadia - monospace
    "excalifont": 5, # Excalifont - rough hand-drawn
    "nunito": 6,     # Nunito - clean sans-serif (good for roughness=0)
    "lilita": 7,     # Lilita One - bold headings
    "comic": 8,      # Comic Shanns - playful
    "liberation": 9, # Liberation Sans - clean sans-serif
}

TEXT_ALIGN = {"left": "left", "center": "center", "right": "right"}
VERTICAL_ALIGN = {"top": "top", "middle": "middle", "bottom": "bottom"}

FILL_STYLE = {
    "hachure": "hachure",      # diagonal lines
    "solid": "solid",          # solid fill
    "cross-hatch": "cross-hatch",
    "zigzag": "zigzag",
}

STROKE_STYLE = {"solid": "solid", "dashed": "dashed", "dotted": "dotted"}

ROUNDNESS = {
    "sharp": None,
    "round": {"type": 3},  # Adaptive radius
}

ARROWHEADS = {
    "arrow": "arrow",
    "triangle": "triangle",
    "bar": "bar",
    "dot": "circle",  # 'dot' is legacy
    "circle": "circle",
    "diamond": "diamond",
    "none": None,
}

# Color palette (Excalidraw's open-color based palette)
COLORS = {
    "black": "#1e1e1e",
    "white": "#ffffff",
    "transparent": "transparent",
    # Stroke colors (shade index 4)
    "red": "#e03131",
    "pink": "#c2255c",
    "grape": "#9c36b5",
    "violet": "#6741d9",
    "blue": "#1971c2",
    "cyan": "#0c8599",
    "teal": "#099268",
    "green": "#2f9e44",
    "yellow": "#f08c00",
    "orange": "#e8590c",
    "gray": "#868e96",
    # Background colors (shade index 1) - lighter versions
    "red_bg": "#ffe3e3",
    "pink_bg": "#ffdeeb",
    "grape_bg": "#f3d9fa",
    "violet_bg": "#e5dbff",
    "blue_bg": "#d0ebff",
    "cyan_bg": "#c5f6fa",
    "teal_bg": "#c3fae8",
    "green_bg": "#d3f9d8",
    "yellow_bg": "#fff3bf",
    "orange_bg": "#ffe8cc",
    "gray_bg": "#e9ecef",
}

# Background color mapping for stroke colors
BG_FOR_STROKE = {
    "red": "red_bg",
    "pink": "pink_bg",
    "grape": "grape_bg",
    "violet": "violet_bg",
    "blue": "blue_bg",
    "cyan": "cyan_bg",
    "teal": "teal_bg",
    "green": "green_bg",
    "yellow": "yellow_bg",
    "orange": "orange_bg",
    "gray": "gray_bg",
    "black": "transparent",
}


# ============================================================================
# Configuration Classes
# ============================================================================

# Font metrics for different font families (char_width multiplier, line_height multiplier)
FONT_METRICS = {
    "hand": {"char_width": 0.6, "line_height": 1.35},      # Virgil
    "normal": {"char_width": 0.55, "line_height": 1.25},   # Helvetica
    "code": {"char_width": 0.6, "line_height": 1.4},       # Cascadia
    "excalifont": {"char_width": 0.6, "line_height": 1.35},# Excalifont
    "nunito": {"char_width": 0.55, "line_height": 1.3},    # Nunito
    "lilita": {"char_width": 0.65, "line_height": 1.3},    # Lilita One (bold)
    "comic": {"char_width": 0.58, "line_height": 1.35},    # Comic Shanns
    "liberation": {"char_width": 0.55, "line_height": 1.25}, # Liberation Sans
}


@dataclass
class BoxStyle:
    """Style configuration for box elements."""
    h_padding: float = 40      # Horizontal padding (total, split between sides)
    v_padding: float = 24      # Vertical padding (total, split between top/bottom)
    min_width: float = 80      # Minimum box width
    min_height: float = 40     # Minimum box height
    font_size: int = 18        # Default font size for box labels
    font_family: str = "hand"  # Font family for box labels


@dataclass
class RoutingConfig:
    """Configuration for arrow routing behavior."""
    alignment_threshold: float = 20    # Pixels - if within this range, use straight line
    orthogonal_angle_min: float = 0.2  # Min angle ratio for orthogonal routing
    orthogonal_angle_max: float = 0.8  # Max angle ratio for orthogonal routing
    label_offset_h: float = 18         # Label offset for horizontal segments
    label_offset_v: float = 12         # Label offset for vertical segments
    label_font_size: int = 14          # Font size for arrow labels


@dataclass
class FlowchartStyle:
    """Style configuration for flowchart diagrams."""
    # Node colors by type
    start_color: str = "green"
    end_color: str = "red"
    process_color: str = "blue"
    decision_color: str = "yellow"

    # Decision branch routing
    decision_branch_extent: float = 30     # Horizontal extent from diamond
    decision_label_offset_left: float = -25
    decision_label_offset_right: float = 10
    decision_label_offset_y: float = -20

    # Back-edge routing
    back_edge_margin: float = 40           # Base margin from diagram edge
    back_edge_span_multiplier: float = 0.15  # Additional offset as fraction of span
    back_edge_label_offset: float = 10

    # Column connector routing
    column_connector_clearance: float = 20  # Clearance before entering target
    column_connector_label_offset: float = 10


# ============================================================================
# Grid-Based A* Router for Orthogonal Edge Routing
# ============================================================================

from heapq import heappush, heappop
from typing import Set, Dict, Tuple

@dataclass
class GridRouter:
    """A* pathfinding on orthogonal grid for connector routing.

    Builds a grid aligned to shape boundaries (not uniform pixels) and uses
    A* search with a turn penalty to find optimal orthogonal routes that
    avoid crossing shapes.

    Attributes:
        shapes: List of Element objects to route around
        margin: Clearance distance around shapes
        bend_penalty: Cost penalty for each turn (encourages straight paths)
    """

    shapes: list  # List[Element] - shapes to avoid
    margin: float = 15
    bend_penalty: float = 50

    def __post_init__(self):
        self.x_coords: List[float] = []
        self.y_coords: List[float] = []
        self.obstacles: Set[Tuple[int, int]] = set()
        self._build_grid()

    def _build_grid(self):
        """Build grid aligned to shape boundaries."""
        x_set: Set[float] = set()
        y_set: Set[float] = set()

        for shape in self.shapes:
            # Add shape boundaries and margin boundaries
            x_set.update([
                shape.left - self.margin,
                shape.left,
                shape.center_x,
                shape.right,
                shape.right + self.margin
            ])
            y_set.update([
                shape.top - self.margin,
                shape.top,
                shape.center_y,
                shape.bottom,
                shape.bottom + self.margin
            ])

        self.x_coords = sorted(x_set)
        self.y_coords = sorted(y_set)

        # Mark grid cells inside shapes as obstacles
        for shape in self.shapes:
            for xi, x in enumerate(self.x_coords):
                for yi, y in enumerate(self.y_coords):
                    # Check if point is inside shape (with small tolerance)
                    if (shape.left - 1 <= x <= shape.right + 1 and
                        shape.top - 1 <= y <= shape.bottom + 1):
                        self.obstacles.add((xi, yi))

    def _to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to nearest grid cell."""
        xi = min(range(len(self.x_coords)),
                 key=lambda i: abs(self.x_coords[i] - x))
        yi = min(range(len(self.y_coords)),
                 key=lambda i: abs(self.y_coords[i] - y))
        return (xi, yi)

    def _to_world(self, xi: int, yi: int) -> Tuple[float, float]:
        """Convert grid cell to world coordinates."""
        return (self.x_coords[xi], self.y_coords[yi])

    def _neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get orthogonal neighbors (up, down, left, right), skipping obstacles."""
        xi, yi = cell
        neighbors = []
        for dxi, dyi in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nxi, nyi = xi + dxi, yi + dyi
            if (0 <= nxi < len(self.x_coords) and
                0 <= nyi < len(self.y_coords) and
                (nxi, nyi) not in self.obstacles):
                neighbors.append((nxi, nyi))
        return neighbors

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Manhattan distance heuristic."""
        ax, ay = self._to_world(*a)
        bx, by = self._to_world(*b)
        return abs(ax - bx) + abs(ay - by)

    def find_route(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
    ) -> List[Tuple[float, float]]:
        """Find optimal orthogonal route using A*.

        Args:
            start: (x, y) world coordinates of start point
            end: (x, y) world coordinates of end point

        Returns:
            List of (x, y) waypoints for the route
        """
        start_cell = self._to_grid(*start)
        end_cell = self._to_grid(*end)

        # Handle case where start/end are in obstacles (connection points on shapes)
        # Allow these cells temporarily
        start_in_obstacle = start_cell in self.obstacles
        end_in_obstacle = end_cell in self.obstacles
        if start_in_obstacle:
            self.obstacles.discard(start_cell)
        if end_in_obstacle:
            self.obstacles.discard(end_cell)

        # A* search with turn penalty
        # State includes direction to penalize turns
        open_set: list = []
        heappush(open_set, (0, 0, start_cell, None, [start_cell]))  # (f, counter, cell, dir, path)
        counter = 1  # Tie-breaker for heap

        g_score: Dict[Tuple[Tuple[int, int], Optional[str]], float] = {
            (start_cell, None): 0
        }
        visited: Set[Tuple[Tuple[int, int], Optional[str]]] = set()

        result_path = None

        while open_set:
            f, _, current, last_dir, path = heappop(open_set)

            state = (current, last_dir)
            if state in visited:
                continue
            visited.add(state)

            if current == end_cell:
                result_path = path
                break

            for neighbor in self._neighbors(current):
                # Determine direction of this move
                if neighbor[0] != current[0]:
                    new_dir = 'h'  # horizontal
                else:
                    new_dir = 'v'  # vertical

                # Calculate cost
                nx, ny = self._to_world(*neighbor)
                cx, cy = self._to_world(*current)
                move_cost = abs(nx - cx) + abs(ny - cy)

                # Add bend penalty if direction changed
                if last_dir is not None and new_dir != last_dir:
                    move_cost += self.bend_penalty

                tentative_g = g_score.get((current, last_dir), float('inf')) + move_cost
                new_state = (neighbor, new_dir)

                if tentative_g < g_score.get(new_state, float('inf')):
                    g_score[new_state] = tentative_g
                    f_score = tentative_g + self._heuristic(neighbor, end_cell)
                    heappush(open_set, (f_score, counter, neighbor, new_dir, path + [neighbor]))
                    counter += 1

        # Restore obstacle state
        if start_in_obstacle:
            self.obstacles.add(start_cell)
        if end_in_obstacle:
            self.obstacles.add(end_cell)

        if result_path:
            # Convert path to world coordinates and simplify
            world_path = [self._to_world(*cell) for cell in result_path]
            return self._simplify_path(world_path)
        else:
            # No path found - return direct line (fallback)
            return [start, end]

    def _simplify_path(self, path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Remove redundant waypoints from path (keep only turn points)."""
        if len(path) <= 2:
            return path

        simplified = [path[0]]
        for i in range(1, len(path) - 1):
            prev = path[i - 1]
            curr = path[i]
            next_pt = path[i + 1]

            # Check if direction changes at this point
            prev_horizontal = (prev[1] == curr[1])
            next_horizontal = (curr[1] == next_pt[1])

            if prev_horizontal != next_horizontal:
                simplified.append(curr)

        simplified.append(path[-1])
        return simplified


@dataclass
class LayoutConfig:
    """Configuration for layout algorithms."""
    horizontal_spacing: float = 80
    vertical_spacing: float = 100
    direction: str = "TB"  # TB (top-bottom) or LR (left-right)

    # Column splitting
    target_aspect_ratio: float = 1.0
    aspect_ratio_tolerance: float = 0.7
    column_gap: float = 150
    min_layers_to_split: int = 4


@dataclass
class ArchitectureStyle:
    """Style configuration for architecture diagrams."""
    component_color: str = "blue"
    database_color: str = "green"
    service_color: str = "violet"
    user_color: str = "gray"
    queue_color: str = "orange"
    cache_color: str = "cyan"


@dataclass
class DiagramStyle:
    """Global style settings for the entire diagram.

    Attributes:
        roughness: Sloppiness level (0=architect/clean, 1=artist/normal, 2=cartoonist/rough)
        stroke_style: Line style ("solid", "dashed", "dotted")
        color_scheme: Named color scheme ("default", "monochrome", "corporate", "vibrant")
        font: Font family ("hand", "normal", "code", "nunito", "excalifont", or "auto")
              When "auto", uses "nunito" for roughness=0, "hand" otherwise
    """
    roughness: int = 1              # 0=clean lines, 1=normal hand-drawn, 2=rough sketch
    stroke_style: str = "solid"     # solid, dashed, dotted
    stroke_width: int = 2           # Line thickness (1-4)
    color_scheme: str = "default"   # Color scheme name
    font: str = "auto"              # Font family or "auto" for roughness-based selection

    def get_font(self) -> str:
        """Get the effective font family based on settings."""
        if self.font == "auto":
            return "nunito" if self.roughness == 0 else "hand"
        return self.font


# Predefined color schemes
COLOR_SCHEMES = {
    "default": {
        # Standard Excalidraw colors
        "primary": "blue",
        "secondary": "green",
        "accent": "violet",
        "warning": "yellow",
        "danger": "red",
        "neutral": "gray",
        "info": "cyan",
        "highlight": "orange",
    },
    "monochrome": {
        "primary": "black",
        "secondary": "gray",
        "accent": "gray",
        "warning": "gray",
        "danger": "black",
        "neutral": "gray",
        "info": "gray",
        "highlight": "black",
    },
    "corporate": {
        "primary": "blue",
        "secondary": "teal",
        "accent": "violet",
        "warning": "orange",
        "danger": "red",
        "neutral": "gray",
        "info": "cyan",
        "highlight": "blue",
    },
    "vibrant": {
        "primary": "violet",
        "secondary": "cyan",
        "accent": "orange",
        "warning": "yellow",
        "danger": "red",
        "neutral": "teal",
        "info": "blue",
        "highlight": "green",
    },
    "earth": {
        "primary": "teal",
        "secondary": "green",
        "accent": "orange",
        "warning": "yellow",
        "danger": "red",
        "neutral": "gray",
        "info": "cyan",
        "highlight": "teal",
    },
}


def get_scheme_color(scheme_name: str, role: str) -> str:
    """Get a color from a named scheme.

    Args:
        scheme_name: Name of the color scheme
        role: Semantic role (primary, secondary, accent, warning, danger, neutral, info, highlight)

    Returns:
        Color name from the scheme
    """
    scheme = COLOR_SCHEMES.get(scheme_name, COLOR_SCHEMES["default"])
    return scheme.get(role, "blue")


# ============================================================================
# Element Classes
# ============================================================================

def _gen_id() -> str:
    """Generate a unique element ID."""
    return str(uuid.uuid4())[:20].replace("-", "")

def _gen_seed() -> int:
    """Generate a random seed for roughjs rendering."""
    return random.randint(1, 2_000_000_000)

def _base_element(
    elem_type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    stroke_color: str = "#1e1e1e",
    bg_color: str = "transparent",
    fill_style: str = "solid",
    stroke_width: int = 2,
    stroke_style: str = "solid",
    roughness: int = 1,
    opacity: int = 100,
    angle: float = 0,
    roundness: Optional[dict] = None,
) -> dict:
    """Create a base element with common properties."""
    return {
        "id": _gen_id(),
        "type": elem_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": angle,
        "strokeColor": stroke_color,
        "backgroundColor": bg_color,
        "fillStyle": fill_style,
        "strokeWidth": stroke_width,
        "strokeStyle": stroke_style,
        "roughness": roughness,
        "opacity": opacity,
        "seed": _gen_seed(),
        "version": 1,
        "versionNonce": _gen_seed(),
        "index": None,
        "isDeleted": False,
        "groupIds": [],
        "frameId": None,
        "boundElements": None,
        "updated": 1,
        "link": None,
        "locked": False,
        "roundness": roundness,
    }


def rectangle(
    x: float,
    y: float,
    width: float,
    height: float,
    color: str = "black",
    fill: bool = True,
    rounded: bool = True,
    **kwargs
) -> dict:
    """Create a rectangle element."""
    stroke = COLORS.get(color, color)
    bg = COLORS.get(BG_FOR_STROKE.get(color, "transparent"), "transparent") if fill else "transparent"

    elem = _base_element(
        "rectangle", x, y, width, height,
        stroke_color=stroke,
        bg_color=bg,
        roundness=ROUNDNESS["round"] if rounded else ROUNDNESS["sharp"],
        **kwargs
    )
    return elem


def ellipse(
    x: float,
    y: float,
    width: float,
    height: float,
    color: str = "black",
    fill: bool = True,
    **kwargs
) -> dict:
    """Create an ellipse element."""
    stroke = COLORS.get(color, color)
    bg = COLORS.get(BG_FOR_STROKE.get(color, "transparent"), "transparent") if fill else "transparent"

    elem = _base_element(
        "ellipse", x, y, width, height,
        stroke_color=stroke,
        bg_color=bg,
        **kwargs
    )
    return elem


def diamond(
    x: float,
    y: float,
    width: float,
    height: float,
    color: str = "black",
    fill: bool = True,
    **kwargs
) -> dict:
    """Create a diamond element."""
    stroke = COLORS.get(color, color)
    bg = COLORS.get(BG_FOR_STROKE.get(color, "transparent"), "transparent") if fill else "transparent"

    elem = _base_element(
        "diamond", x, y, width, height,
        stroke_color=stroke,
        bg_color=bg,
        **kwargs
    )
    return elem


def text(
    x: float,
    y: float,
    content: str,
    font_size: int = 20,
    font_family: str = "hand",
    color: str = "black",
    align: str = "center",
    **kwargs
) -> dict:
    """Create a text element."""
    stroke = COLORS.get(color, color)
    ff = FONT_FAMILY.get(font_family, 1)

    # Estimate dimensions based on content
    lines = content.split("\n")
    max_line_len = max(len(line) for line in lines)
    width = max_line_len * font_size * 0.6
    height = len(lines) * font_size * 1.35

    elem = _base_element(
        "text", x, y, width, height,
        stroke_color=stroke,
        bg_color="transparent",
        **kwargs
    )
    # Calculate baseline for proper SVG export
    # Baseline is the distance from top to the text baseline
    line_height_multiplier = 1.25
    num_lines = len(lines)
    baseline = font_size * 0.82  # Single line baseline approximation
    if num_lines > 1:
        # For multi-line, baseline is at bottom of first line
        baseline = font_size * 0.82

    elem.update({
        "fontSize": font_size,
        "fontFamily": ff,
        "text": content,
        "textAlign": TEXT_ALIGN.get(align, "center"),
        "verticalAlign": "top",
        "containerId": None,
        "originalText": content,
        "autoResize": True,
        "lineHeight": line_height_multiplier,
        "baseline": baseline,
    })
    return elem


def measure_text_for_box(
    label: str,
    font_size: int = 18,
    font_family: str = "hand",
    box_style: BoxStyle = None,
) -> tuple:
    """
    Calculate required dimensions for text content in a box.

    Args:
        label: Text content (supports multi-line with \\n)
        font_size: Font size in pixels
        font_family: Font family name (hand, normal, code, excalifont)
        box_style: Optional BoxStyle for padding/min size (uses defaults if None)

    Returns (width, height) with appropriate padding for a box element.
    """
    style = box_style or BoxStyle()
    metrics = FONT_METRICS.get(font_family, FONT_METRICS["hand"])

    lines = label.split("\n")
    max_line_len = max(len(line) for line in lines) if lines else 0

    # Calculate text dimensions using font metrics
    text_width = max_line_len * font_size * metrics["char_width"]
    text_height = len(lines) * font_size * metrics["line_height"]

    # Add padding from style config
    box_width = max(style.min_width, text_width + style.h_padding)
    box_height = max(style.min_height, text_height + style.v_padding)

    return (box_width, box_height)


def arrow(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    color: str = "black",
    start_head: Optional[str] = None,
    end_head: str = "arrow",
    label: Optional[str] = None,
    routing: str = "auto",  # "auto", "straight", "orthogonal"
    **kwargs
) -> List[dict]:
    """Create an arrow element, optionally with a label. Returns list of elements.

    Args:
        routing: "straight" for direct line, "orthogonal" for right-angle routing,
                 "auto" to choose based on alignment
    """
    stroke = COLORS.get(color, color)

    # Calculate points relative to start
    dx = end_x - start_x
    dy = end_y - start_y

    # Determine if we should use orthogonal routing
    use_orthogonal = False
    alignment_threshold = 30  # Pixels - if within this range, consider "aligned"

    if routing == "orthogonal":
        use_orthogonal = True
    elif routing == "auto":
        # Use orthogonal only if significantly offset in both dimensions
        # and not close to 45 degrees
        if abs(dx) > alignment_threshold and abs(dy) > alignment_threshold:
            angle_ratio = min(abs(dx), abs(dy)) / max(abs(dx), abs(dy))
            # If ratio is between 0.2 and 0.8, it's awkward diagonal - use orthogonal
            if 0.2 < angle_ratio < 0.8:
                use_orthogonal = True

    if use_orthogonal and abs(dx) > alignment_threshold and abs(dy) > alignment_threshold:
        # Create orthogonal path: vertical first, then horizontal (or vice versa)
        # Choose based on which direction is dominant
        if abs(dy) > abs(dx):
            # Mostly vertical - go vertical first, then horizontal
            mid_y = dy / 2
            points = [[0, 0], [0, mid_y], [dx, mid_y], [dx, dy]]
        else:
            # Mostly horizontal - go horizontal first, then vertical
            mid_x = dx / 2
            points = [[0, 0], [mid_x, 0], [mid_x, dy], [dx, dy]]
    else:
        # Straight line
        points = [[0, 0], [dx, dy]]

    elem = _base_element(
        "arrow", start_x, start_y,
        abs(dx), abs(dy),
        stroke_color=stroke,
        bg_color="transparent",
        **kwargs
    )
    # Use elbowed mode for orthogonal routing (sharp 90-degree corners)
    is_orthogonal = len(points) > 2
    elem.update({
        "points": points,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": ARROWHEADS.get(start_head),
        "endArrowhead": ARROWHEADS.get(end_head, "arrow"),
        "elbowed": is_orthogonal,  # Sharp corners for orthogonal paths
        "roundness": None if is_orthogonal else ROUNDNESS.get("round"),
    })
    # Add elbow-specific properties when elbowed
    if is_orthogonal:
        elem.update({
            "fixedSegments": None,
            "startIsSpecial": None,
            "endIsSpecial": None,
        })

    elements = [elem]

    # Add label if provided - always black for readability
    # Position at midpoint with clear offset to avoid overlap with shapes
    if label:
        # For orthogonal paths, place label at the middle segment
        if len(points) > 2:
            # Middle of the path
            mid_idx = len(points) // 2
            p1 = points[mid_idx - 1]
            p2 = points[mid_idx]
            mid_x = start_x + (p1[0] + p2[0]) / 2
            mid_y = start_y + (p1[1] + p2[1]) / 2
            # Offset based on segment direction
            if abs(p2[0] - p1[0]) > abs(p2[1] - p1[1]):
                mid_y -= 20  # Horizontal segment - label above
            else:
                mid_x += 20  # Vertical segment - label to right
        else:
            mid_x = start_x + dx * 0.5
            mid_y = start_y + dy * 0.5
            if abs(dx) > abs(dy):
                mid_y -= 20
            else:
                mid_x += 20

        label_elem = text(mid_x, mid_y, label, font_size=14, color="black")
        elements.append(label_elem)

    return elements


def line(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    color: str = "black",
    **kwargs
) -> dict:
    """Create a line element."""
    stroke = COLORS.get(color, color)
    dx = end_x - start_x
    dy = end_y - start_y

    elem = _base_element(
        "line", start_x, start_y,
        abs(dx), abs(dy),
        stroke_color=stroke,
        bg_color="transparent",
        **kwargs
    )
    elem.update({
        "points": [[0, 0], [dx, dy]],
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": None,
    })
    return elem


# ============================================================================
# Diagram Class - High-Level API
# ============================================================================

@dataclass
class Element:
    """Wrapper for element with position tracking."""
    data: dict
    x: float
    y: float
    width: float
    height: float
    id: str = ""

    def __post_init__(self):
        self.id = self.data.get("id", "")

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def top(self) -> float:
        return self.y

    @property
    def left(self) -> float:
        return self.x


class Diagram:
    """High-level API for creating Excalidraw diagrams."""

    def __init__(
        self,
        background: str = "#ffffff",
        box_style: BoxStyle = None,
        routing_config: RoutingConfig = None,
        diagram_style: DiagramStyle = None,
    ):
        self.elements: List[dict] = []
        self.background = background
        self.box_style = box_style or BoxStyle()
        self.routing = routing_config or RoutingConfig()
        self.style = diagram_style or DiagramStyle()

        # Sync box_style font with diagram style if using auto
        if self.box_style.font_family == "hand":  # Default value
            self.box_style.font_family = self.style.get_font()

    def add(self, *elements: Union[dict, List[dict]]) -> None:
        """Add raw elements to the diagram."""
        for elem in elements:
            if isinstance(elem, list):
                self.elements.extend(elem)
            else:
                self.elements.append(elem)

    def scheme_color(self, role: str) -> str:
        """Get a color from the current color scheme.

        Args:
            role: Semantic color role - "primary", "secondary", "accent",
                  "warning", "danger", "neutral", "info", or "highlight"

        Returns:
            The color name from the current scheme.
        """
        return get_scheme_color(self.style.color_scheme, role)

    def box(
        self,
        x: float,
        y: float,
        label: str,
        width: float = None,
        height: float = None,
        color: str = "blue",
        shape: Literal["rectangle", "ellipse", "diamond"] = "rectangle",
        font_size: int = None,
    ) -> Element:
        """Create a labeled box (rectangle, ellipse, or diamond).

        If width or height is not specified, they are auto-calculated based on
        the label text content with appropriate padding.
        """
        # Use configured font size if not specified
        if font_size is None:
            font_size = self.box_style.font_size

        # Auto-calculate dimensions if not specified
        if width is None or height is None:
            auto_width, auto_height = measure_text_for_box(
                label, font_size, self.box_style.font_family, self.box_style
            )
            if width is None:
                width = auto_width
            if height is None:
                height = auto_height

        shape_funcs = {
            "rectangle": rectangle,
            "ellipse": ellipse,
            "diamond": diamond,
        }
        # Apply diagram-wide style settings
        shape_elem = shape_funcs[shape](
            x, y, width, height, color=color,
            roughness=self.style.roughness,
            stroke_style=self.style.stroke_style,
            stroke_width=self.style.stroke_width,
        )

        # Add shape first (background)
        self.elements.append(shape_elem)

        # Add centered text as a single element (supports multi-line with \n)
        lines = label.split("\n")
        font_family = self.box_style.font_family
        metrics = FONT_METRICS.get(font_family, FONT_METRICS["hand"])
        line_height = font_size * metrics["line_height"]
        total_text_height = len(lines) * line_height

        # Calculate vertical center position for text block
        text_y = y + (height - total_text_height) / 2 + font_size * 0.2

        # Create single text element with full label (including \n)
        text_elem = text(
            x,  # left edge of box - textAlign:center will center within width
            text_y,
            label,  # Full label with \n characters preserved
            font_size=font_size,
            font_family=font_family,
            color="black",
            align="center"
        )
        # Set text width to match box, so center alignment works correctly
        text_elem["width"] = width
        text_elem["textAlign"] = "center"
        text_elem["verticalAlign"] = "top"
        self.elements.append(text_elem)

        return Element(shape_elem, x, y, width, height)

    def text_box(
        self,
        x: float,
        y: float,
        content: str,
        font_size: int = 20,
        color: str = "black",
        font_family: str = None,
    ) -> Element:
        """Create a standalone text element."""
        ff = font_family or self.box_style.font_family
        elem = text(x, y, content, font_size=font_size, font_family=ff, color=color)
        self.elements.append(elem)
        return Element(elem, x, y, elem["width"], elem["height"])

    def arrow_between(
        self,
        source: Element,
        target: Element,
        label: Optional[str] = None,
        color: str = "black",
        from_side: Literal["right", "bottom", "left", "top", "auto"] = "auto",
        to_side: Literal["left", "top", "right", "bottom", "auto"] = "auto",
        routing: Literal["auto", "straight", "orthogonal"] = "auto",
    ) -> None:
        """Draw an arrow between two elements.

        Args:
            routing: "straight" for direct line, "orthogonal" for right-angle routing,
                     "auto" to choose based on alignment
        """
        # Determine connection points
        if from_side == "auto" and to_side == "auto":
            # Auto-detect best sides based on relative position
            dx = target.center_x - source.center_x
            dy = target.center_y - source.center_y

            if abs(dx) > abs(dy):
                # Horizontal connection
                from_side = "right" if dx > 0 else "left"
                to_side = "left" if dx > 0 else "right"
            else:
                # Vertical connection
                from_side = "bottom" if dy > 0 else "top"
                to_side = "top" if dy > 0 else "bottom"

        # Get start point
        if from_side == "right":
            sx, sy = source.right, source.center_y
        elif from_side == "left":
            sx, sy = source.left, source.center_y
        elif from_side == "bottom":
            sx, sy = source.center_x, source.bottom
        else:  # top
            sx, sy = source.center_x, source.top

        # Get end point
        if to_side == "left":
            ex, ey = target.left, target.center_y
        elif to_side == "right":
            ex, ey = target.right, target.center_y
        elif to_side == "top":
            ex, ey = target.center_x, target.top
        else:  # bottom
            ex, ey = target.center_x, target.bottom

        dx = ex - sx
        dy = ey - sy

        # For orthogonal routing, build path that respects entry/exit directions
        threshold = self.routing.alignment_threshold
        use_orthogonal = routing == "orthogonal" or (
            routing == "auto" and abs(dx) > threshold and abs(dy) > threshold
        )

        if use_orthogonal:
            # Build path with perpendicular entry/exit
            points = self._build_orthogonal_path(sx, sy, ex, ey, from_side, to_side)
            self._draw_elbowed_arrow(sx, sy, points, color, label)
        else:
            # Straight line or nearly aligned
            elems = arrow(
                sx, sy, ex, ey, color=color, label=label, routing="straight",
                roughness=self.style.roughness,
                stroke_style=self.style.stroke_style,
                stroke_width=self.style.stroke_width,
            )
            self.elements.extend(elems)

    def _build_orthogonal_path(
        self,
        sx: float, sy: float,
        ex: float, ey: float,
        from_side: str, to_side: str,
        routing_margin: float = 50,
    ) -> List[List[float]]:
        """Build an orthogonal path that exits/enters perpendicular to box edges.

        The path always starts with a segment perpendicular to from_side
        and ends with a segment perpendicular to to_side.

        For same-side connections (left-left, right-right, top-top, bottom-bottom),
        the path routes around to avoid crossing through other elements.
        """
        dx = ex - sx
        dy = ey - sy

        # Determine exit and entry directions
        exit_horizontal = from_side in ("left", "right")
        entry_horizontal = to_side in ("left", "right")

        # Handle same-side routing (needs to go around)
        if from_side == to_side:
            if from_side == "left":
                # Exit left, enter left: go left, then vertical, then right
                offset_x = -routing_margin
                points = [
                    [0, 0],
                    [offset_x, 0],           # Go left
                    [offset_x, dy],          # Go vertical
                    [dx, dy],                # Go right to target
                ]
            elif from_side == "right":
                # Exit right, enter right: go right past target, then vertical, then left
                offset_x = max(dx, 0) + routing_margin
                points = [
                    [0, 0],
                    [offset_x, 0],           # Go right
                    [offset_x, dy],          # Go vertical
                    [dx, dy],                # Go left to target
                ]
            elif from_side == "top":
                # Exit top, enter top: go up, then horizontal, then down
                offset_y = min(dy, 0) - routing_margin
                points = [
                    [0, 0],
                    [0, offset_y],           # Go up
                    [dx, offset_y],          # Go horizontal
                    [dx, dy],                # Go down to target
                ]
            else:  # bottom
                # Exit bottom, enter bottom: go down past target, then horizontal, then up
                offset_y = max(dy, 0) + routing_margin
                points = [
                    [0, 0],
                    [0, offset_y],           # Go down
                    [dx, offset_y],          # Go horizontal
                    [dx, dy],                # Go up to target
                ]
        elif exit_horizontal and entry_horizontal:
            # Both horizontal but different sides: go horizontal, then vertical, then horizontal
            mid_x = dx / 2
            points = [
                [0, 0],
                [mid_x, 0],      # Horizontal from start
                [mid_x, dy],    # Vertical
                [dx, dy],       # Horizontal to end
            ]
        elif not exit_horizontal and not entry_horizontal:
            # Both vertical but different sides: go vertical, then horizontal, then vertical
            mid_y = dy / 2
            points = [
                [0, 0],
                [0, mid_y],     # Vertical from start
                [dx, mid_y],    # Horizontal
                [dx, dy],       # Vertical to end
            ]
        elif exit_horizontal and not entry_horizontal:
            # Exit horizontal, enter vertical: horizontal then vertical
            points = [
                [0, 0],
                [dx, 0],        # Horizontal to target x
                [dx, dy],       # Vertical to end
            ]
        else:
            # Exit vertical, enter horizontal: vertical then horizontal
            points = [
                [0, 0],
                [0, dy],        # Vertical to target y
                [dx, dy],       # Horizontal to end
            ]

        return points

    def _draw_elbowed_arrow(
        self,
        sx: float, sy: float,
        points: List[List[float]],
        color: str,
        label: Optional[str],
    ) -> None:
        """Draw an elbowed arrow with the given path points."""
        stroke = COLORS.get(color, "#1e1e1e")

        # Calculate bounds
        max_dx = max(abs(p[0]) for p in points)
        max_dy = max(abs(p[1]) for p in points)

        elem = _base_element(
            "arrow", sx, sy,
            max_dx, max_dy,
            stroke_color=stroke,
            bg_color="transparent",
            roughness=self.style.roughness,
            stroke_style=self.style.stroke_style,
            stroke_width=self.style.stroke_width,
        )
        elem.update({
            "points": points,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": True,
            "roundness": None,
            "fixedSegments": None,
            "startIsSpecial": None,
            "endIsSpecial": None,
        })
        self.elements.append(elem)

        # Add label at middle segment using routing config
        if label and len(points) > 2:
            mid_idx = len(points) // 2
            p1 = points[mid_idx - 1]
            p2 = points[mid_idx]
            label_x = sx + (p1[0] + p2[0]) / 2
            label_y = sy + (p1[1] + p2[1]) / 2
            # Offset based on segment direction
            if abs(p2[0] - p1[0]) > abs(p2[1] - p1[1]):
                label_y -= self.routing.label_offset_h  # Horizontal segment - label above
            else:
                label_x += self.routing.label_offset_v  # Vertical segment - label to right
            label_elem = text(label_x, label_y, label, font_size=self.routing.label_font_size,
                            font_family=self.box_style.font_family, color="black")
            self.elements.append(label_elem)

    def arrow_between_routed(
        self,
        source: Element,
        target: Element,
        label: Optional[str] = None,
        color: str = "black",
        obstacles: Optional[List[Element]] = None,
    ) -> None:
        """Draw an arrow between two elements using A* pathfinding.

        Routes the arrow around obstacles (other shapes) to avoid crossings.
        Best for architecture diagrams and non-hierarchical layouts.

        Args:
            source: Starting element
            target: Ending element
            label: Optional text label (bound to arrow)
            color: Arrow color
            obstacles: List of elements to route around. If None, uses all
                      shape elements currently in the diagram.
        """
        # Collect obstacles - all shape elements except arrows
        if obstacles is None:
            obstacles = [
                Element(data=e, x=e["x"], y=e["y"],
                       width=e["width"], height=e["height"])
                for e in self.elements
                if e.get("type") in ("rectangle", "ellipse", "diamond")
            ]

        if not obstacles:
            # No obstacles - fall back to regular arrow
            self.arrow_between(source, target, label=label, color=color)
            return

        # Build router
        router = GridRouter(shapes=obstacles, margin=20, bend_penalty=80)

        # Get connection points based on relative positions
        dx = target.center_x - source.center_x
        dy = target.center_y - source.center_y

        # Determine best connection points
        if abs(dx) > abs(dy):
            # Horizontal: exit/enter from sides
            start_pt = (source.right if dx > 0 else source.left, source.center_y)
            end_pt = (target.left if dx > 0 else target.right, target.center_y)
        else:
            # Vertical: exit/enter from top/bottom
            start_pt = (source.center_x, source.bottom if dy > 0 else source.top)
            end_pt = (target.center_x, target.top if dy > 0 else target.bottom)

        # Find optimal route
        waypoints = router.find_route(start_pt, end_pt)

        # Draw the routed arrow with bound label
        self._draw_routed_arrow_bound(waypoints, label=label, color=color)

    def _draw_routed_arrow_bound(
        self,
        waypoints: List[Tuple[float, float]],
        label: Optional[str] = None,
        color: str = "black",
    ) -> None:
        """Draw an arrow following waypoints with label bound to arrow."""
        if len(waypoints) < 2:
            return

        sx, sy = waypoints[0]
        ex, ey = waypoints[-1]

        # Convert waypoints to relative points
        points = [[0, 0]]
        for wx, wy in waypoints[1:]:
            points.append([wx - sx, wy - sy])

        stroke = COLORS.get(color, "#1e1e1e")
        arrow_id = _gen_id()
        elem = _base_element(
            "arrow", sx, sy,
            abs(ex - sx) or 1, abs(ey - sy) or 1,
            stroke_color=stroke,
            bg_color="transparent",
            roughness=self.style.roughness,
            stroke_style=self.style.stroke_style,
            stroke_width=self.style.stroke_width,
        )
        elem["id"] = arrow_id
        elem.update({
            "points": points,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": True,
            "roundness": None,
        })

        if label:
            # Find midpoint for label
            total_length = sum(
                abs(waypoints[i+1][0] - waypoints[i][0]) + abs(waypoints[i+1][1] - waypoints[i][1])
                for i in range(len(waypoints) - 1)
            )
            mid_length = total_length / 2
            accumulated = 0
            label_x, label_y = waypoints[0]

            for i in range(len(waypoints) - 1):
                p1, p2 = waypoints[i], waypoints[i + 1]
                seg_length = abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])
                if accumulated + seg_length >= mid_length:
                    t = (mid_length - accumulated) / seg_length if seg_length > 0 else 0
                    label_x = p1[0] + t * (p2[0] - p1[0])
                    label_y = p1[1] + t * (p2[1] - p1[1])
                    break
                accumulated += seg_length

            # Create bound text
            text_id = _gen_id()
            label_elem = text(
                label_x, label_y - 10, label,
                font_size=self.routing.label_font_size,
                font_family=self.box_style.font_family,
                color="black"
            )
            label_elem["id"] = text_id
            label_elem["containerId"] = arrow_id
            label_elem["textAlign"] = "center"
            elem["boundElements"] = [{"type": "text", "id": text_id}]

            self.elements.append(elem)
            self.elements.append(label_elem)
        else:
            self.elements.append(elem)

    def line_between(
        self,
        source: Element,
        target: Element,
        color: str = "black",
    ) -> None:
        """Draw a line between two elements."""
        elem = line(
            source.center_x, source.center_y,
            target.center_x, target.center_y,
            color=color,
            roughness=self.style.roughness,
            stroke_style=self.style.stroke_style,
            stroke_width=self.style.stroke_width,
        )
        self.elements.append(elem)

    def group(self, *elements: Element) -> str:
        """Group elements together. Returns group ID."""
        group_id = _gen_id()
        for elem in elements:
            if "groupIds" not in self.elements[self._find_element_index(elem.id)]:
                self.elements[self._find_element_index(elem.id)]["groupIds"] = []
            self.elements[self._find_element_index(elem.id)]["groupIds"].append(group_id)
        return group_id

    def _find_element_index(self, elem_id: str) -> int:
        for i, e in enumerate(self.elements):
            if e.get("id") == elem_id:
                return i
        return -1

    def to_dict(self) -> dict:
        """Export diagram as Excalidraw JSON dict."""
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {
                "gridSize": 20,
                "gridStep": 5,
                "gridModeEnabled": False,
                "viewBackgroundColor": self.background,
            },
            "files": {},
        }

    def to_json(self, indent: int = 2) -> str:
        """Export diagram as JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: Union[str, Path]) -> Path:
        """Save diagram to file."""
        path = Path(path)
        if not path.suffix:
            path = path.with_suffix(".excalidraw")
        path.write_text(self.to_json())
        return path

    def save_to_drive(self, name: str = None, folder_id: str = None,
                      share_public: bool = False, local_path: str = None) -> dict:
        """
        Save diagram to Google Drive.

        Args:
            name: Name for the file in Drive (defaults to 'diagram.excalidraw')
            folder_id: Optional Drive folder ID to upload to
            share_public: If True, make the file publicly accessible
            local_path: Optional local path to save first (temp file used if None)

        Returns:
            dict with status, file info, and edit_url for Excalidraw web

        Example:
            d = Diagram()
            d.box(100, 100, "Hello")
            result = d.save_to_drive("my_diagram.excalidraw", share_public=True)
            print(result["edit_url"])  # Opens in Excalidraw web
        """
        import tempfile
        import os

        try:
            from drive_helper import DriveUploader
        except ImportError:
            # Try with full path
            import sys
            script_dir = Path(__file__).parent
            if str(script_dir) not in sys.path:
                sys.path.insert(0, str(script_dir))
            from drive_helper import DriveUploader

        # Determine filename
        file_name = name or "diagram.excalidraw"
        if not file_name.endswith(".excalidraw"):
            file_name += ".excalidraw"

        # Save to local path or temp file
        if local_path:
            save_path = self.save(local_path)
            cleanup = False
        else:
            # Create temp file
            fd, temp_path = tempfile.mkstemp(suffix=".excalidraw")
            os.close(fd)
            save_path = self.save(temp_path)
            cleanup = True

        try:
            # Upload to Drive
            uploader = DriveUploader(folder_id=folder_id)
            result = uploader.upload(
                str(save_path),
                name=file_name,
                share_public=share_public
            )

            # Add local path info if saved locally
            if local_path:
                result["local_path"] = str(save_path)

            return result
        finally:
            # Clean up temp file if used
            if cleanup and save_path.exists():
                save_path.unlink()


# ============================================================================
# Flowchart Builder
# ============================================================================

class Flowchart(Diagram):
    """Specialized diagram for creating flowcharts."""

    def __init__(
        self,
        direction: Literal["horizontal", "vertical"] = "vertical",
        spacing: int = 80,
        flowchart_style: FlowchartStyle = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.direction = direction
        self.spacing = spacing
        self.flowchart_style = flowchart_style or FlowchartStyle()
        self._nodes: dict[str, Element] = {}
        self._next_x = 100
        self._next_y = 100

    def node(
        self,
        node_id: str,
        label: str,
        shape: Literal["rectangle", "ellipse", "diamond"] = "rectangle",
        color: str = "blue",
        width: float = None,
        height: float = None,
    ) -> Element:
        """Add a node to the flowchart.

        If width or height is not specified, they are auto-calculated based on
        the label text content.
        """
        elem = self.box(
            self._next_x, self._next_y,
            label, width, height, color, shape
        )
        self._nodes[node_id] = elem

        # Update position for next node using actual element dimensions
        if self.direction == "vertical":
            self._next_y += elem.height + self.spacing
        else:
            self._next_x += elem.width + self.spacing

        return elem

    def start(self, label: str = "Start", color: str = None) -> Element:
        """Add a start node (rounded rectangle)."""
        node_color = color or self.flowchart_style.start_color
        return self.node("__start__", label, shape="ellipse", color=node_color)

    def end(self, label: str = "End", color: str = None) -> Element:
        """Add an end node."""
        node_color = color or self.flowchart_style.end_color
        return self.node("__end__", label, shape="ellipse", color=node_color)

    def process(self, node_id: str, label: str, color: str = None) -> Element:
        """Add a process node (rectangle)."""
        node_color = color or self.flowchart_style.process_color
        return self.node(node_id, label, shape="rectangle", color=node_color)

    def decision(self, node_id: str, label: str, color: str = None) -> Element:
        """Add a decision node (diamond). Auto-sizes to fit label."""
        node_color = color or self.flowchart_style.decision_color
        return self.node(node_id, label, shape="diamond", color=node_color)

    def connect(
        self,
        from_id: str,
        to_id: str,
        label: Optional[str] = None,
        color: str = "black",
        from_side: Literal["right", "bottom", "left", "top", "auto"] = "auto",
        to_side: Literal["left", "top", "right", "bottom", "auto"] = "auto",
    ) -> None:
        """Connect two nodes with an arrow.

        Args:
            from_id: Source node ID
            to_id: Target node ID
            label: Optional label for the arrow
            color: Arrow color
            from_side: Which side to exit from (auto detects based on position)
            to_side: Which side to enter to (auto detects based on position)
        """
        source = self._nodes.get(from_id)
        target = self._nodes.get(to_id)
        if source and target:
            self.arrow_between(source, target, label=label, color=color,
                             from_side=from_side, to_side=to_side)

    def position_at(self, x: float, y: float) -> "Flowchart":
        """Set position for next node."""
        self._next_x = x
        self._next_y = y
        return self


# ============================================================================
# Architecture Diagram Builder
# ============================================================================

class ArchitectureDiagram(Diagram):
    """Specialized diagram for system architecture.

    Args:
        architecture_style: Style configuration for components
        use_astar_routing: If True, use A* pathfinding to route connections
                          around components (avoids crossings). Default: True
        **kwargs: Additional arguments passed to Diagram base class
    """

    def __init__(
        self,
        architecture_style: ArchitectureStyle = None,
        use_astar_routing: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.arch_style = architecture_style or ArchitectureStyle()
        self.use_astar_routing = use_astar_routing
        self._components: dict[str, Element] = {}

    def component(
        self,
        comp_id: str,
        label: str,
        x: float,
        y: float,
        width: float = None,
        height: float = None,
        color: str = None,
    ) -> Element:
        """Add a system component. Auto-sizes to fit label if dimensions not specified."""
        comp_color = color or self.arch_style.component_color
        elem = self.box(x, y, label, width, height, comp_color)
        self._components[comp_id] = elem
        return elem

    def database(
        self,
        db_id: str,
        label: str,
        x: float,
        y: float,
        color: str = None,
    ) -> Element:
        """Add a database component (ellipse). Auto-sizes to fit label."""
        db_color = color or self.arch_style.database_color
        elem = self.box(x, y, label, None, None, db_color, shape="ellipse")
        self._components[db_id] = elem
        return elem

    def service(
        self,
        svc_id: str,
        label: str,
        x: float,
        y: float,
        color: str = None,
    ) -> Element:
        """Add a service component. Auto-sizes to fit label."""
        svc_color = color or self.arch_style.service_color
        elem = self.box(x, y, label, None, None, svc_color)
        self._components[svc_id] = elem
        return elem

    def user(
        self,
        user_id: str,
        label: str = "User",
        x: float = 100,
        y: float = 100,
        color: str = None,
    ) -> Element:
        """Add a user/actor. Auto-sizes to fit label."""
        user_color = color or self.arch_style.user_color
        elem = self.box(x, y, label, None, None, user_color, shape="ellipse")
        self._components[user_id] = elem
        return elem

    def connect(
        self,
        from_id: str,
        to_id: str,
        label: Optional[str] = None,
        bidirectional: bool = False,
        color: str = "black",
    ) -> None:
        """Connect two components.

        If use_astar_routing is enabled (default), routes around other components.
        """
        source = self._components.get(from_id)
        target = self._components.get(to_id)
        if source and target:
            # Get list of obstacles (all components except source and target)
            obstacles = [c for c in self._components.values() if c not in (source, target)]

            if self.use_astar_routing and obstacles:
                self.arrow_between_routed(source, target, label=label, color=color, obstacles=obstacles)
                if bidirectional:
                    self.arrow_between_routed(target, source, color=color, obstacles=obstacles)
            else:
                self.arrow_between(source, target, label=label, color=color)
                if bidirectional:
                    self.arrow_between(target, source, color=color)


# ============================================================================
# Auto-Layout Flowchart Builder
# ============================================================================

class AutoLayoutFlowchart(Diagram):
    """
    Flowchart with automatic hierarchical layout.

    Uses the Sugiyama algorithm to automatically position nodes,
    minimizing edge crossings and producing clean flowcharts.

    Example:
        fc = AutoLayoutFlowchart()
        fc.add_node("start", "Start", shape="ellipse", color="green", node_type="terminal")
        fc.add_node("step1", "Process Data", color="blue", node_type="process")
        fc.add_node("decision", "Valid?", shape="diamond", color="yellow", node_type="decision")
        fc.add_node("end", "End", shape="ellipse", color="red", node_type="terminal")

        fc.add_edge("start", "step1")
        fc.add_edge("step1", "decision")
        fc.add_edge("decision", "end", label="Yes")

        fc.compute_layout()  # Auto-position all nodes
        fc.save("flowchart.excalidraw")
    """

    def __init__(
        self,
        horizontal_spacing: float = None,
        vertical_spacing: float = None,
        direction: str = None,
        layout_config: LayoutConfig = None,
        flowchart_style: FlowchartStyle = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Use layout config or individual parameters
        self.layout = layout_config or LayoutConfig()
        if horizontal_spacing is not None:
            self.layout.horizontal_spacing = horizontal_spacing
        if vertical_spacing is not None:
            self.layout.vertical_spacing = vertical_spacing
        if direction is not None:
            self.layout.direction = direction

        # Flowchart-specific styling
        self.flowchart_style = flowchart_style or FlowchartStyle()

        self._nodes: dict = {}  # id -> node info
        self._edges: list = []  # list of edge info
        self._elements_map: dict = {}  # id -> Element

    def add_node(
        self,
        node_id: str,
        label: str,
        shape: str = "rectangle",
        color: str = "blue",
        width: float = None,
        height: float = None,
        node_type: str = "process",  # process, decision, terminal, or custom
    ) -> None:
        """Add a node to the flowchart. Position will be computed later.

        Args:
            node_id: Unique identifier for the node
            label: Text label for the node
            shape: Visual shape (rectangle, ellipse, diamond)
            color: Fill color
            width/height: Optional explicit dimensions (auto-calculated if None)
            node_type: Semantic type - 'process', 'decision', 'terminal', or custom
                       Used for routing decisions (decision nodes get side exits)
        """
        self._nodes[node_id] = {
            "id": node_id,
            "label": label,
            "shape": shape,
            "color": color,
            "width": width,
            "height": height,
            "node_type": node_type,
        }

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        label: str = None,
        color: str = "black",
    ) -> None:
        """Add an edge between two nodes."""
        self._edges.append({
            "from": from_id,
            "to": to_id,
            "label": label,
            "color": color,
        })

    def compute_layout(
        self,
        start_x: float = 100,
        start_y: float = 100,
        max_width: float = None,
        max_height: float = None,
        routing: str = "auto",
        two_column: bool = False,
        target_aspect_ratio: float = 0.8,
        column_gap: float = 120,
        use_astar_routing: bool = False,
    ) -> dict:
        """
        Compute positions for all nodes using hierarchical layout,
        then create the visual elements.

        Args:
            start_x, start_y: Starting position offset
            max_width: Maximum width (will scale if exceeded)
            max_height: Maximum height (will scale if exceeded)
            routing: Arrow routing style ("auto", "straight", "orthogonal")
            two_column: If True, automatically split tall diagrams into two columns
            target_aspect_ratio: Target aspect ratio when splitting (default 0.8)
            column_gap: Gap between columns when splitting
            use_astar_routing: If True, use A* pathfinding for edge routing (experimental)

        Returns:
            Dict with layout metadata: width, height, aspect_ratio, layers, scale_factor, split
        """
        # Import layout engine
        import sys
        from pathlib import Path
        script_dir = Path(__file__).parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))

        from layout_engine import LayoutNode, LayoutEdge, auto_layout, split_to_columns

        # Create layout nodes with auto-sized dimensions
        layout_nodes = []
        for node_id, info in self._nodes.items():
            # Auto-calculate dimensions if not specified
            w, h = info["width"], info["height"]
            if w is None or h is None:
                auto_w, auto_h = measure_text_for_box(info["label"], font_size=18)
                w = w or auto_w
                h = h or auto_h

            layout_nodes.append(LayoutNode(
                id=node_id,
                label=info["label"],
                width=w,
                height=h,
                data=info
            ))

        # Create layout edges
        layout_edges = [
            LayoutEdge(source_id=e["from"], target_id=e["to"], label=e.get("label"))
            for e in self._edges
        ]

        # Compute layout
        result = auto_layout(
            layout_nodes,
            layout_edges,
            algorithm="hierarchical",
            horizontal_spacing=self.layout.horizontal_spacing,
            vertical_spacing=self.layout.vertical_spacing,
            direction=self.layout.direction
        )

        # Apply two-column split if requested and needed
        connector_info = None
        was_split = False
        if two_column:
            result, connector_info = split_to_columns(
                result,
                target_aspect_ratio=target_aspect_ratio,
                column_gap=column_gap
            )
            was_split = connector_info is not None

        # Store layout metadata
        self._layout_result = result

        # Calculate scale factor if max dimensions specified
        scale_factor = 1.0
        if max_width and result.width > max_width:
            scale_factor = min(scale_factor, max_width / result.width)
        if max_height and result.height > max_height:
            scale_factor = min(scale_factor, max_height / result.height)

        # Create visual elements at computed positions
        for node_id, node in result.nodes.items():
            info = self._nodes[node_id]
            # Layout engine uses centered coordinates, Excalidraw uses top-left
            # Convert from centered to top-left coordinates
            w = node.width * scale_factor
            h = node.height * scale_factor
            x = (node.x - node.width / 2) * scale_factor + start_x
            y = (node.y - node.height / 2) * scale_factor + start_y

            elem = self.box(
                x, y,
                info["label"],
                width=w,
                height=h,
                color=info["color"],
                shape=info["shape"]
            )
            self._elements_map[node_id] = elem

        # Track which edges to skip (we'll draw the connector specially)
        skip_edge = None
        gap_x = None
        if connector_info:
            skip_edge = (connector_info[0], connector_info[1])
            gap_x = connector_info[2] * scale_factor + start_x if len(connector_info) > 2 else None

        # Calculate diagram bounds for back-edge routing
        all_elements = list(self._elements_map.values())
        diagram_right = max(e.right for e in all_elements) if all_elements else 500
        diagram_left = min(e.left for e in all_elements) if all_elements else 0

        # Create A* router if enabled
        router = None
        if use_astar_routing and all_elements:
            router = GridRouter(shapes=all_elements, margin=20, bend_penalty=80)

        # Pre-compute exit sides for decision branches to ensure opposite sides
        # Group decision edges by source node
        decision_edges: dict[str, list] = {}
        for edge in self._edges:
            source_info = self._nodes.get(edge["from"], {})
            node_type = source_info.get("node_type", "process")
            is_decision = node_type == "decision" or source_info.get("shape") == "diamond"
            has_label = edge.get("label") is not None
            if is_decision and has_label:
                src = edge["from"]
                if src not in decision_edges:
                    decision_edges[src] = []
                decision_edges[src].append(edge)

        # Assign exit sides for each decision node's branches
        decision_exit_sides: dict[tuple[str, str], str] = {}  # (from, to) -> "left" or "right"
        for src, edges in decision_edges.items():
            if len(edges) == 2:
                # Two branches - force opposite sides
                e1, e2 = edges
                source = self._elements_map.get(src)
                t1 = self._elements_map.get(e1["to"])
                t2 = self._elements_map.get(e2["to"])
                if source and t1 and t2:
                    # Check if either branch is a back-edge (target above or at same level as source)
                    e1_is_back = t1.center_y <= source.center_y
                    e2_is_back = t2.center_y <= source.center_y

                    if e1_is_back and not e2_is_back:
                        # e1 is back-edge -> exits LEFT (conventional loop side)
                        decision_exit_sides[(e1["from"], e1["to"])] = "left"
                        decision_exit_sides[(e2["from"], e2["to"])] = "right"
                    elif e2_is_back and not e1_is_back:
                        # e2 is back-edge -> exits LEFT
                        decision_exit_sides[(e1["from"], e1["to"])] = "right"
                        decision_exit_sides[(e2["from"], e2["to"])] = "left"
                    else:
                        # Neither or both are back-edges - use x-position comparison
                        if t1.center_x < t2.center_x:
                            decision_exit_sides[(e1["from"], e1["to"])] = "left"
                            decision_exit_sides[(e2["from"], e2["to"])] = "right"
                        else:
                            decision_exit_sides[(e1["from"], e1["to"])] = "right"
                            decision_exit_sides[(e2["from"], e2["to"])] = "left"
            # For 1 or 3+ branches, let _draw_decision_branch decide

        # Create arrows with specified routing
        for edge in self._edges:
            source = self._elements_map.get(edge["from"])
            target = self._elements_map.get(edge["to"])
            if source and target:
                # Skip the connector edge - we'll draw it specially
                if skip_edge and edge["from"] == skip_edge[0] and edge["to"] == skip_edge[1]:
                    continue

                source_info = self._nodes.get(edge["from"], {})
                # Use node_type for routing decisions (falls back to shape for compatibility)
                node_type = source_info.get("node_type", "process")
                is_decision = node_type == "decision" or source_info.get("shape") == "diamond"
                has_label = edge.get("label") is not None
                is_back_edge = target.center_y <= source.center_y

                # Use A* routing if enabled
                if router is not None:
                    # For decision branches, use pre-computed exit side
                    forced_exit_side = None
                    if is_decision and has_label:
                        forced_exit_side = decision_exit_sides.get((edge["from"], edge["to"]))

                    # Get connection points
                    start_pt = self._get_connection_point(source, target, "exit", forced_exit_side)
                    end_pt = self._get_connection_point(target, source, "entry")
                    # Find optimal route
                    waypoints = router.find_route(start_pt, end_pt)
                    # Draw the routed arrow
                    self._draw_routed_arrow(
                        waypoints,
                        label=edge.get("label"),
                        color=edge.get("color", "black"),
                    )
                elif is_decision and has_label:
                    # Decision branch: start from left/right side of diamond
                    # Use pre-computed exit side if available
                    exit_side = decision_exit_sides.get((edge["from"], edge["to"]))
                    self._draw_decision_branch(
                        source, target,
                        label=edge.get("label"),
                        color=edge.get("color", "black"),
                        diagram_right=diagram_right,
                        diagram_left=diagram_left,
                        exit_side=exit_side,
                    )
                elif is_back_edge:
                    # Back-edge: route through whitespace
                    self._draw_back_edge(
                        source, target,
                        label=edge.get("label"),
                        color=edge.get("color", "black"),
                        diagram_right=diagram_right,
                        diagram_left=diagram_left,
                    )
                else:
                    # Normal forward edge
                    self.arrow_between(
                        source, target,
                        label=edge.get("label"),
                        color=edge.get("color", "black"),
                        routing=routing,
                    )

        # Draw the connector edge with special routing through the gap
        if connector_info:
            source = self._elements_map.get(connector_info[0])
            target = self._elements_map.get(connector_info[1])
            if source and target:
                # Find the edge label
                edge_label = None
                for e in self._edges:
                    if e["from"] == connector_info[0] and e["to"] == connector_info[1]:
                        edge_label = e.get("label")
                        break
                # Draw elbowed connector through the gap between columns
                self._draw_column_connector(source, target, edge_label, scale_factor, gap_x)

        return {
            "width": result.width * scale_factor,
            "height": result.height * scale_factor,
            "aspect_ratio": result.aspect_ratio,
            "layers": result.layers,
            "scale_factor": scale_factor,
            "split": was_split,
        }

    def _draw_column_connector(
        self,
        source: "Element",
        target: "Element",
        label: Optional[str],
        scale_factor: float,
        gap_x: Optional[float] = None,
    ) -> None:
        """Draw an elbowed arrow connecting two columns through the gap.

        Route: right edge of source -> right to gap -> down in gap -> right to target -> top of target
        All segments are horizontal or vertical (90-degree elbows).
        """
        # Start from right side of source (to go toward the gap)
        sx = source.right
        sy = source.center_y

        # End at top of target
        ex = target.center_x
        ey = target.top

        # If no gap_x provided, calculate midpoint between source and target
        if gap_x is None:
            gap_x = (source.right + target.left) / 2

        # Create path with 90-degree turns:
        # 1. Right from source to gap
        # 2. Down in the gap
        # 3. Right from gap to above target
        # 4. Down to target top
        clearance = self.flowchart_style.column_connector_clearance

        points = [
            [0, 0],                              # Start (at source right edge)
            [gap_x - sx, 0],                     # Right to gap (horizontal)
            [gap_x - sx, ey - sy - clearance],   # Down in gap (vertical) - stop above target
            [ex - sx, ey - sy - clearance],      # Right to above target (horizontal)
            [ex - sx, ey - sy],                  # Down to target (vertical)
        ]

        stroke = COLORS.get("black", "#1e1e1e")
        elem = _base_element(
            "arrow", sx, sy,
            abs(ex - sx), abs(ey - sy),
            stroke_color=stroke,
            bg_color="transparent",
            roughness=self.style.roughness,
            stroke_style=self.style.stroke_style,
            stroke_width=self.style.stroke_width,
        )
        elem.update({
            "points": points,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": True,  # Sharp 90-degree corners
            "roundness": None,  # Disable roundness for sharp elbows
            "fixedSegments": None,
            "startIsSpecial": None,
            "endIsSpecial": None,
        })
        self.elements.append(elem)

        # Add label in the gap area (on the vertical segment)
        if label:
            label_x = gap_x + self.flowchart_style.column_connector_label_offset
            label_y = sy + (ey - sy) / 2
            label_elem = text(label_x, label_y, label, font_size=self.routing.label_font_size,
                            font_family=self.box_style.font_family, color="black")
            self.elements.append(label_elem)

    def _get_connection_point(
        self,
        shape: "Element",
        other: "Element",
        mode: str = "auto",
        forced_side: Optional[str] = None,
    ) -> Tuple[float, float]:
        """Determine where to connect to/from a shape.

        Args:
            shape: The shape to connect to/from
            other: The other shape in the connection
            mode: "exit" (leaving shape), "entry" (entering shape), or "auto"
            forced_side: If provided ("left" or "right"), force exit from this side

        Returns:
            (x, y) connection point on the shape's edge
        """
        dx = other.center_x - shape.center_x
        dy = other.center_y - shape.center_y

        # Check element type from the data dict
        element_type = shape.data.get("type", "rectangle")

        # For diamonds (decision nodes):
        # - EXIT: prefer left/right sides (flowchart convention for Yes/No branches)
        # - ENTRY: prefer top (coming from above) or use side if horizontal
        if element_type == "diamond":
            if mode == "exit":
                # Use forced side if provided (ensures opposite sides for decision branches)
                if forced_side == "left":
                    return (shape.left, shape.center_y)
                elif forced_side == "right":
                    return (shape.right, shape.center_y)
                # Default: choose side based on target's horizontal position
                return (shape.right if dx >= 0 else shape.left, shape.center_y)
            elif mode == "entry":
                # Entering a diamond - prefer top if coming from above, else side
                if dy < 0:  # other is above, enter from top
                    return (shape.center_x, shape.top)
                elif abs(dx) > abs(dy):
                    return (shape.right if dx > 0 else shape.left, shape.center_y)
                else:
                    return (shape.center_x, shape.bottom if dy > 0 else shape.top)
            else:  # auto
                if abs(dx) > abs(dy):
                    return (shape.right if dx > 0 else shape.left, shape.center_y)
                else:
                    return (shape.center_x, shape.bottom if dy > 0 else shape.top)

        # For rectangles/ellipses
        # Special case for back-edges (entering from below): prefer side entry
        if mode == "entry" and dy > 0:
            # Source (other) is below target (shape) - this is a back-edge
            # Enter from the side (left or right based on source position)
            return (shape.right if dx > 0 else shape.left, shape.center_y)

        # Normal case: connect to the side closest to other shape
        if abs(dx) > abs(dy):
            # Horizontal connection
            return (shape.right if dx > 0 else shape.left, shape.center_y)
        else:
            # Vertical connection
            return (shape.center_x, shape.bottom if dy > 0 else shape.top)

    def _draw_routed_arrow(
        self,
        waypoints: List[Tuple[float, float]],
        label: Optional[str] = None,
        color: str = "black",
    ) -> None:
        """Draw an arrow following a series of waypoints.

        Creates an orthogonal arrow with elbow turns at each waypoint.
        Labels are bound to the arrow (not separate text boxes).

        Args:
            waypoints: List of (x, y) points the arrow passes through
            label: Optional text label for the arrow
            color: Arrow color
        """
        if len(waypoints) < 2:
            return

        # Start point
        sx, sy = waypoints[0]
        # End point
        ex, ey = waypoints[-1]

        # Convert waypoints to relative points for Excalidraw
        points = [[0, 0]]  # Start at origin
        for wx, wy in waypoints[1:]:
            points.append([wx - sx, wy - sy])

        stroke = COLORS.get(color, "#1e1e1e")
        arrow_id = _gen_id()
        elem = _base_element(
            "arrow", sx, sy,
            abs(ex - sx) or 1, abs(ey - sy) or 1,
            stroke_color=stroke,
            bg_color="transparent",
            roughness=self.style.roughness,
            stroke_style=self.style.stroke_style,
            stroke_width=self.style.stroke_width,
        )
        elem["id"] = arrow_id
        elem.update({
            "points": points,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": True,
            "roundness": None,
        })

        # Add bound label if provided
        if label:
            # Find midpoint along the path for label positioning
            total_length = 0
            for i in range(len(waypoints) - 1):
                p1, p2 = waypoints[i], waypoints[i + 1]
                total_length += abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])

            mid_length = total_length / 2
            accumulated = 0
            label_x, label_y = waypoints[0]

            for i in range(len(waypoints) - 1):
                p1, p2 = waypoints[i], waypoints[i + 1]
                seg_length = abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])
                if accumulated + seg_length >= mid_length:
                    # Label goes on this segment
                    t = (mid_length - accumulated) / seg_length if seg_length > 0 else 0
                    label_x = p1[0] + t * (p2[0] - p1[0])
                    label_y = p1[1] + t * (p2[1] - p1[1])
                    break
                accumulated += seg_length

            # Create bound text element
            text_id = _gen_id()
            label_elem = text(
                label_x, label_y - 10, label,
                font_size=self.routing.label_font_size,
                font_family=self.box_style.font_family,
                color="black"
            )
            label_elem["id"] = text_id
            label_elem["containerId"] = arrow_id
            label_elem["textAlign"] = "center"

            # Bind text to arrow
            elem["boundElements"] = [{"type": "text", "id": text_id}]

            self.elements.append(elem)
            self.elements.append(label_elem)
        else:
            self.elements.append(elem)

    def _draw_decision_branch(
        self,
        source: "Element",
        target: "Element",
        label: Optional[str],
        color: str,
        diagram_right: float,
        diagram_left: float,
        exit_side: Optional[str] = None,
    ) -> None:
        """Draw an arrow from a decision diamond's left or right point.

        The arrow starts horizontally from the diamond's side, then elbows
        to reach the target. Ensures arrow never crosses through the source box.

        Args:
            exit_side: If provided ("left" or "right"), forces which side to exit from.
                       This is used when multiple branches need to exit opposite sides.
        """
        # Determine which side to exit from
        target_is_below = target.center_y > source.center_y

        if exit_side is not None:
            # Use pre-computed exit side (ensures opposite sides for 2-branch decisions)
            target_is_left = (exit_side == "left")
        elif target_is_below:
            # Target is below - use RIGHT unless target is far left
            target_is_left = target.center_x < source.center_x - 80
        else:
            # Target at same level or above - exit toward target
            target_is_left = target.center_x < source.center_x

        if target_is_left:
            # Exit from left side of diamond
            sx = source.left
            sy = source.center_y
        else:
            # Exit from right side of diamond
            sx = source.right
            sy = source.center_y

        # Determine target connection point
        if target_is_below:
            # Target is below - connect to top
            ex = target.center_x
            ey = target.top
        else:
            # Target is at same level or above (back-edge)
            # Enter from the SAME side we're routing on
            if target_is_left:
                # Routing on left side -> enter from left
                ex = target.left
                ey = target.center_y
            else:
                # Routing on right side -> enter from right
                ex = target.right
                ey = target.center_y

        # Build path with elbow at start level
        if target_is_below:
            # Check if going directly to target.center_x would cross the source box
            # This happens when we exit right but target is to the left (or vice versa)
            would_cross_source = (not target_is_left and ex < sx) or (target_is_left and ex > sx)

            if would_cross_source:
                # Route around: go out in exit direction first, then across above target, then down
                horizontal_extent = self.flowchart_style.decision_branch_extent
                if target_is_left:
                    mid_x = sx - horizontal_extent  # Go left first
                else:
                    mid_x = sx + horizontal_extent  # Go right first
                # Add clearance above target for vertical entry
                clearance = 20
                points = [
                    [0, 0],                            # Start at diamond side
                    [mid_x - sx, 0],                   # Horizontal away from diamond
                    [mid_x - sx, ey - sy - clearance], # Down to above target
                    [ex - sx, ey - sy - clearance],    # Horizontal to above target center
                    [ex - sx, ey - sy],                # Down vertically into target top
                ]
            else:
                # Direct path: horizontal to above target, then down
                points = [
                    [0, 0],                    # Start at diamond side
                    [ex - sx, 0],              # Horizontal to above target
                    [ex - sx, ey - sy],        # Down to target top
                ]
        else:
            # Back-edge: route through whitespace on left or right side
            # Calculate routing margin similar to _draw_back_edge
            fc_style = self.flowchart_style
            base_margin = fc_style.back_edge_margin
            vertical_span = abs(target.center_y - sy)
            span_offset = vertical_span * fc_style.back_edge_span_multiplier

            if target_is_left:
                # Route through whitespace on the LEFT
                route_x = min(diagram_left - base_margin - span_offset,
                              sx - base_margin,
                              target.left - base_margin)
            else:
                # Route through whitespace on the RIGHT
                route_x = max(diagram_right + base_margin + span_offset,
                              sx + base_margin,
                              target.right + base_margin)

            points = [
                [0, 0],                    # Start at diamond side
                [route_x - sx, 0],         # Horizontal to routing margin
                [route_x - sx, ey - sy],   # Vertical to target level
                [ex - sx, ey - sy],        # Horizontal to target
            ]

        stroke = COLORS.get(color, "#1e1e1e")
        elem = _base_element(
            "arrow", sx, sy,
            abs(ex - sx), abs(ey - sy),
            stroke_color=stroke,
            bg_color="transparent",
            roughness=self.style.roughness,
            stroke_style=self.style.stroke_style,
            stroke_width=self.style.stroke_width,
        )
        elem.update({
            "points": points,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": True,
            "roundness": None,
            "fixedSegments": None,
            "startIsSpecial": None,
            "endIsSpecial": None,
        })
        self.elements.append(elem)

        # Add label on the horizontal segment
        if label:
            fc_style = self.flowchart_style
            if target_is_below:
                # Place label along the horizontal segment, away from center to avoid overlap
                if target_is_left:
                    # Left branch going down - place label to the left
                    label_x = sx - 60 - len(label) * 5
                else:
                    # Right branch going down - place label to the right
                    label_x = sx + 20
                label_y = sy + fc_style.decision_label_offset_y
            else:
                # Horizontal branch - place label at start
                label_offset = fc_style.decision_label_offset_left if target_is_left else fc_style.decision_label_offset_right
                label_x = sx + label_offset
                label_y = sy + fc_style.decision_label_offset_y
            label_elem = text(label_x, label_y, label, font_size=self.routing.label_font_size,
                            font_family=self.box_style.font_family, color="black")
            self.elements.append(label_elem)

    def _draw_back_edge(
        self,
        source: "Element",
        target: "Element",
        label: Optional[str],
        color: str,
        diagram_right: float,
        diagram_left: float = 0,
    ) -> None:
        """Draw a back-edge that routes through whitespace.

        For edges going to a previous (higher) node in the flow, route through
        whitespace on the appropriate side based on target position:
        - If target is to the LEFT: route on left side, enter from left
        - If target is to the RIGHT or centered: route on right side, enter from top/right

        Entry point depends on vertical distance:
        - Significant vertical span: enter from top of target (cleaner U-turn)
        - Small vertical span: enter from side of target
        """
        # Determine routing side based on source position relative to diagram center
        # Route on the same side as the source to minimize crossings
        diagram_center = (diagram_left + diagram_right) / 2
        source_is_on_right = source.center_x > diagram_center

        if source_is_on_right:
            # Source is on right side of diagram - route on RIGHT to avoid crossing
            sx = source.right
            sy = source.center_y
            route_on_left = False
        else:
            # Source is on left/center of diagram - route on LEFT (conventional)
            sx = source.left
            sy = source.center_y
            route_on_left = True

        # Calculate vertical span of this back-edge
        vertical_span = abs(target.center_y - sy)

        # Base margin from diagram edge
        fc_style = self.flowchart_style
        base_margin = fc_style.back_edge_margin

        # Additional offset based on vertical span - longer edges route further out
        span_offset = vertical_span * fc_style.back_edge_span_multiplier

        # Decide entry point: top entry for significant upward movement
        enter_from_top = vertical_span > 100 and target.center_y < sy

        if route_on_left:
            # Route through whitespace on the LEFT
            route_x = min(diagram_left - base_margin - span_offset,
                          sx - base_margin,
                          target.left - base_margin)

            if enter_from_top:
                ex = target.center_x
                ey = target.top
                clearance = 20
                points = [
                    [0, 0],
                    [route_x - sx, 0],
                    [route_x - sx, ey - sy - clearance],
                    [ex - sx, ey - sy - clearance],
                    [ex - sx, ey - sy],
                ]
            else:
                ex = target.left
                ey = target.center_y
                points = [
                    [0, 0],
                    [route_x - sx, 0],
                    [route_x - sx, ey - sy],
                    [ex - sx, ey - sy],
                ]
        else:
            # Route through whitespace on the RIGHT
            route_x = max(diagram_right + base_margin + span_offset,
                          sx + base_margin,
                          target.right + base_margin)

            if enter_from_top:
                ex = target.center_x
                ey = target.top
                clearance = 20
                points = [
                    [0, 0],
                    [route_x - sx, 0],
                    [route_x - sx, ey - sy - clearance],
                    [ex - sx, ey - sy - clearance],
                    [ex - sx, ey - sy],
                ]
            else:
                ex = target.right
                ey = target.center_y
                points = [
                    [0, 0],
                    [route_x - sx, 0],
                    [route_x - sx, ey - sy],
                    [ex - sx, ey - sy],
                ]

        stroke = COLORS.get(color, "#1e1e1e")
        elem = _base_element(
            "arrow", sx, sy,
            abs(route_x - sx), abs(ey - sy),
            stroke_color=stroke,
            bg_color="transparent",
            roughness=self.style.roughness,
            stroke_style=self.style.stroke_style,
            stroke_width=self.style.stroke_width,
        )
        elem.update({
            "points": points,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": True,
            "roundness": None,
            "fixedSegments": None,
            "startIsSpecial": None,
            "endIsSpecial": None,
        })
        self.elements.append(elem)

        # Add label on the vertical segment in whitespace
        if label:
            if route_on_left:
                # Label to the left of the route line
                label_x = route_x - fc_style.back_edge_label_offset - len(label) * 6
            else:
                # Label to the right of the route line
                label_x = route_x + fc_style.back_edge_label_offset
            label_y = sy + (ey - sy) / 2
            label_elem = text(label_x, label_y, label, font_size=self.routing.label_font_size,
                            font_family=self.box_style.font_family, color="black")
            self.elements.append(label_elem)


# Import measure_text_for_box for the AutoLayoutFlowchart
def _import_measure_text():
    """Make measure_text_for_box available at module level."""
    pass  # Already defined in this module


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: excalidraw_generator.py <output_file>")
        print("\nExample diagram will be created.")

        # Create example diagram
        d = Diagram()
        box1 = d.box(100, 100, "Frontend", color="blue")
        box2 = d.box(350, 100, "Backend", color="green")
        box3 = d.box(600, 100, "Database", color="orange")

        d.arrow_between(box1, box2, "REST API")
        d.arrow_between(box2, box3, "SQL")

        output = Path("example.excalidraw")
        d.save(output)
        print(f"Created: {output}")
        return

    output_path = sys.argv[1]

    # Read JSON from stdin if available
    if not sys.stdin.isatty():
        data = json.load(sys.stdin)
        d = Diagram()
        # Process simple node/edge format
        nodes = {}
        for node in data.get("nodes", []):
            elem = d.box(
                node.get("x", 100),
                node.get("y", 100),
                node.get("label", "Node"),
                color=node.get("color", "blue"),
                shape=node.get("shape", "rectangle"),
            )
            nodes[node.get("id", node.get("label"))] = elem

        for edge in data.get("edges", []):
            source = nodes.get(edge.get("from"))
            target = nodes.get(edge.get("to"))
            if source and target:
                d.arrow_between(source, target, label=edge.get("label"))

        d.save(output_path)
        print(f"Created: {output_path}")
    else:
        print("Provide JSON input via stdin")
        print('Example: echo \'{"nodes":[{"id":"a","label":"A","x":100,"y":100}]}\' | python excalidraw_generator.py out.excalidraw')


if __name__ == "__main__":
    main()
