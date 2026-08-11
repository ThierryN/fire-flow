#!/usr/bin/env python3
"""Tests for the Excalidraw diagram generator."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from excalidraw_generator import (
    Diagram,
    Flowchart,
    ArchitectureDiagram,
    rectangle,
    ellipse,
    diamond,
    text,
    arrow,
    line,
    COLORS,
    FONT_FAMILY,
)


class TestElementCreation:
    """Tests for individual element creation functions."""

    def test_rectangle_basic(self):
        elem = rectangle(100, 200, 150, 60)
        assert elem["type"] == "rectangle"
        assert elem["x"] == 100
        assert elem["y"] == 200
        assert elem["width"] == 150
        assert elem["height"] == 60
        assert elem["isDeleted"] is False
        assert "id" in elem
        assert "seed" in elem

    def test_rectangle_with_color(self):
        elem = rectangle(0, 0, 100, 100, color="blue", fill=True)
        assert elem["strokeColor"] == COLORS["blue"]
        assert elem["backgroundColor"] == COLORS["blue_bg"]

    def test_rectangle_no_fill(self):
        elem = rectangle(0, 0, 100, 100, color="red", fill=False)
        assert elem["strokeColor"] == COLORS["red"]
        assert elem["backgroundColor"] == "transparent"

    def test_rectangle_rounded(self):
        elem = rectangle(0, 0, 100, 100, rounded=True)
        assert elem["roundness"] is not None
        assert elem["roundness"]["type"] == 3

    def test_rectangle_sharp(self):
        elem = rectangle(0, 0, 100, 100, rounded=False)
        assert elem["roundness"] is None

    def test_ellipse_basic(self):
        elem = ellipse(50, 50, 100, 80)
        assert elem["type"] == "ellipse"
        assert elem["x"] == 50
        assert elem["y"] == 50

    def test_diamond_basic(self):
        elem = diamond(0, 0, 120, 80)
        assert elem["type"] == "diamond"

    def test_text_basic(self):
        elem = text(100, 100, "Hello World")
        assert elem["type"] == "text"
        assert elem["text"] == "Hello World"
        assert elem["originalText"] == "Hello World"
        assert elem["fontSize"] == 20
        assert elem["fontFamily"] == FONT_FAMILY["hand"]

    def test_text_with_options(self):
        elem = text(0, 0, "Code", font_size=16, font_family="code", color="violet")
        assert elem["fontSize"] == 16
        assert elem["fontFamily"] == FONT_FAMILY["code"]
        assert elem["strokeColor"] == COLORS["violet"]

    def test_text_multiline(self):
        elem = text(0, 0, "Line 1\nLine 2\nLine 3")
        assert elem["text"] == "Line 1\nLine 2\nLine 3"
        # Height should account for multiple lines
        assert elem["height"] > elem["fontSize"]

    def test_arrow_basic(self):
        elems = arrow(0, 0, 100, 50)
        assert len(elems) >= 1
        arrow_elem = elems[0]
        assert arrow_elem["type"] == "arrow"
        # Arrow may use orthogonal routing for diagonal paths
        assert len(arrow_elem["points"]) >= 2
        assert arrow_elem["points"][0] == [0, 0]  # Start point
        assert arrow_elem["points"][-1][0] == 100  # End x
        assert arrow_elem["points"][-1][1] == 50   # End y
        assert arrow_elem["endArrowhead"] == "arrow"
        assert arrow_elem["startArrowhead"] is None

    def test_arrow_with_label(self):
        elems = arrow(0, 0, 100, 0, label="connects")
        assert len(elems) == 2
        assert elems[0]["type"] == "arrow"
        assert elems[1]["type"] == "text"
        assert elems[1]["text"] == "connects"

    def test_arrow_bidirectional(self):
        elems = arrow(0, 0, 100, 0, start_head="arrow", end_head="arrow")
        arrow_elem = elems[0]
        assert arrow_elem["startArrowhead"] == "arrow"
        assert arrow_elem["endArrowhead"] == "arrow"

    def test_line_basic(self):
        elem = line(0, 0, 200, 100)
        assert elem["type"] == "line"
        assert elem["points"] == [[0, 0], [200, 100]]
        assert elem["startArrowhead"] is None
        assert elem["endArrowhead"] is None


class TestDiagram:
    """Tests for the Diagram class."""

    def test_diagram_creation(self):
        d = Diagram()
        assert d.elements == []
        assert d.background == "#ffffff"

    def test_diagram_custom_background(self):
        d = Diagram(background="#f0f0f0")
        assert d.background == "#f0f0f0"

    def test_diagram_box(self):
        d = Diagram()
        elem = d.box(100, 100, "Test Box")
        assert elem.x == 100
        assert elem.y == 100
        # Box dimensions are now auto-calculated from text
        assert elem.width >= 80  # Minimum width from BoxStyle
        assert elem.height >= 40  # Minimum height from BoxStyle
        # Should create rectangle + text
        assert len(d.elements) == 2
        assert d.elements[0]["type"] == "rectangle"
        assert d.elements[1]["type"] == "text"

    def test_diagram_box_shapes(self):
        d = Diagram()
        d.box(0, 0, "Rect", shape="rectangle")
        d.box(0, 100, "Ellipse", shape="ellipse")
        d.box(0, 200, "Diamond", shape="diamond")
        assert d.elements[0]["type"] == "rectangle"
        assert d.elements[2]["type"] == "ellipse"
        assert d.elements[4]["type"] == "diamond"

    def test_diagram_text_box(self):
        d = Diagram()
        elem = d.text_box(50, 50, "Standalone Text")
        assert len(d.elements) == 1
        assert d.elements[0]["type"] == "text"
        assert d.elements[0]["text"] == "Standalone Text"

    def test_diagram_arrow_between(self):
        d = Diagram()
        box1 = d.box(0, 0, "A")
        box2 = d.box(300, 0, "B")
        d.arrow_between(box1, box2)
        # 2 boxes (rect+text each) + arrow = 5 elements
        assert len(d.elements) == 5
        assert d.elements[4]["type"] == "arrow"

    def test_diagram_arrow_between_with_label(self):
        d = Diagram()
        box1 = d.box(0, 0, "A")
        box2 = d.box(300, 0, "B")
        d.arrow_between(box1, box2, label="connects")
        # 2 boxes + arrow + label = 6 elements
        assert len(d.elements) == 6

    def test_diagram_to_dict(self):
        d = Diagram()
        d.box(0, 0, "Test")
        result = d.to_dict()
        assert result["type"] == "excalidraw"
        assert result["version"] == 2
        assert "elements" in result
        assert "appState" in result
        assert "files" in result
        assert result["appState"]["viewBackgroundColor"] == "#ffffff"

    def test_diagram_to_json(self):
        d = Diagram()
        d.box(0, 0, "Test")
        json_str = d.to_json()
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["type"] == "excalidraw"

    def test_diagram_save(self):
        d = Diagram()
        d.box(0, 0, "Test")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "test"))
            assert path.suffix == ".excalidraw"
            assert path.exists()
            # Verify content
            with open(path) as f:
                data = json.load(f)
            assert data["type"] == "excalidraw"


class TestFlowchart:
    """Tests for the Flowchart class."""

    def test_flowchart_vertical(self):
        fc = Flowchart(direction="vertical", spacing=100)
        fc.start("Start")
        fc.process("p1", "Process")
        fc.end("End")
        # Nodes should be vertically arranged
        nodes = [fc._nodes["__start__"], fc._nodes["p1"], fc._nodes["__end__"]]
        assert nodes[0].y < nodes[1].y < nodes[2].y
        # X should be same
        assert nodes[0].x == nodes[1].x == nodes[2].x

    def test_flowchart_horizontal(self):
        fc = Flowchart(direction="horizontal", spacing=100)
        fc.start("Start")
        fc.process("p1", "Process")
        fc.end("End")
        nodes = [fc._nodes["__start__"], fc._nodes["p1"], fc._nodes["__end__"]]
        assert nodes[0].x < nodes[1].x < nodes[2].x
        # Y should be same
        assert nodes[0].y == nodes[1].y == nodes[2].y

    def test_flowchart_decision(self):
        fc = Flowchart()
        fc.decision("d1", "Yes or No?")
        # Should create a diamond
        diamond_elem = None
        for elem in fc.elements:
            if elem["type"] == "diamond":
                diamond_elem = elem
                break
        assert diamond_elem is not None

    def test_flowchart_connect(self):
        fc = Flowchart()
        fc.start("Start")
        fc.process("p1", "Process")
        fc.connect("__start__", "p1")
        # Should have arrow connecting them
        arrows = [e for e in fc.elements if e["type"] == "arrow"]
        assert len(arrows) == 1

    def test_flowchart_connect_with_label(self):
        fc = Flowchart()
        fc.start("Start")
        fc.decision("d1", "OK?")
        fc.connect("__start__", "d1", label="check")
        # Should have arrow + label text
        arrows = [e for e in fc.elements if e["type"] == "arrow"]
        assert len(arrows) == 1

    def test_flowchart_position_at(self):
        fc = Flowchart()
        fc.position_at(500, 300)
        fc.process("p1", "Positioned")
        assert fc._nodes["p1"].x == 500
        assert fc._nodes["p1"].y == 300


class TestArchitectureDiagram:
    """Tests for the ArchitectureDiagram class."""

    def test_architecture_component(self):
        arch = ArchitectureDiagram()
        elem = arch.component("api", "API Server", x=100, y=100)
        assert elem.x == 100
        assert elem.y == 100
        assert "api" in arch._components

    def test_architecture_database(self):
        arch = ArchitectureDiagram()
        elem = arch.database("db", "PostgreSQL", x=200, y=200)
        assert "db" in arch._components
        # Database should be an ellipse
        db_elem = None
        for e in arch.elements:
            if e["type"] == "ellipse":
                db_elem = e
                break
        assert db_elem is not None

    def test_architecture_service(self):
        arch = ArchitectureDiagram()
        arch.service("svc", "Auth Service", x=100, y=100)
        assert "svc" in arch._components

    def test_architecture_user(self):
        arch = ArchitectureDiagram()
        arch.user("user", "End User", x=50, y=50)
        assert "user" in arch._components

    def test_architecture_connect(self):
        arch = ArchitectureDiagram()
        arch.component("a", "Service A", x=0, y=0)
        arch.component("b", "Service B", x=300, y=0)
        arch.connect("a", "b", label="REST")
        arrows = [e for e in arch.elements if e["type"] == "arrow"]
        assert len(arrows) == 1

    def test_architecture_connect_bidirectional(self):
        arch = ArchitectureDiagram()
        arch.component("a", "Service A", x=0, y=0)
        arch.component("b", "Service B", x=300, y=0)
        arch.connect("a", "b", bidirectional=True)
        arrows = [e for e in arch.elements if e["type"] == "arrow"]
        assert len(arrows) == 2


class TestExcalidrawFormat:
    """Tests for Excalidraw format compliance."""

    def test_valid_excalidraw_structure(self):
        d = Diagram()
        d.box(0, 0, "Test")
        data = d.to_dict()
        # Required top-level fields
        assert data["type"] == "excalidraw"
        assert data["version"] == 2
        assert "source" in data
        assert isinstance(data["elements"], list)
        assert isinstance(data["appState"], dict)
        assert isinstance(data["files"], dict)

    def test_element_required_fields(self):
        d = Diagram()
        d.box(0, 0, "Test")
        elem = d.elements[0]
        required_fields = [
            "id", "type", "x", "y", "width", "height",
            "strokeColor", "backgroundColor", "fillStyle",
            "strokeWidth", "strokeStyle", "roughness", "opacity",
            "seed", "version", "versionNonce", "isDeleted", "groupIds"
        ]
        for field in required_fields:
            assert field in elem, f"Missing required field: {field}"

    def test_unique_ids(self):
        d = Diagram()
        for i in range(10):
            d.box(i * 100, 0, f"Box {i}")
        ids = [e["id"] for e in d.elements]
        assert len(ids) == len(set(ids)), "Element IDs must be unique"

    def test_colors_are_valid_hex(self):
        import re
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$|^transparent$')
        for name, color in COLORS.items():
            assert hex_pattern.match(color), f"Invalid color format for {name}: {color}"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_diagram(self):
        d = Diagram()
        data = d.to_dict()
        assert data["elements"] == []

    def test_special_characters_in_text(self):
        d = Diagram()
        d.box(0, 0, "Test & <script>alert('xss')</script>")
        # Should not raise
        json_str = d.to_json()
        assert "<script>" in json_str  # Text preserved as-is

    def test_unicode_text(self):
        d = Diagram()
        d.box(0, 0, "日本語テスト")
        d.box(0, 100, "Émojis: 🎨📊")
        json_str = d.to_json()
        assert "日本語テスト" in json_str
        assert "🎨" in json_str

    def test_negative_coordinates(self):
        d = Diagram()
        elem = d.box(-100, -200, "Negative")
        assert elem.x == -100
        assert elem.y == -200

    def test_very_large_coordinates(self):
        d = Diagram()
        elem = d.box(10000, 10000, "Far away")
        assert elem.x == 10000

    def test_zero_dimensions(self):
        elem = rectangle(0, 0, 0, 0)
        assert elem["width"] == 0
        assert elem["height"] == 0


def run_tests():
    """Run all tests and report results."""
    import traceback

    test_classes = [
        TestElementCreation,
        TestDiagram,
        TestFlowchart,
        TestArchitectureDiagram,
        TestExcalidrawFormat,
        TestEdgeCases,
    ]

    total = 0
    passed = 0
    failed = 0
    errors = []

    for test_class in test_classes:
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total += 1
                try:
                    getattr(instance, method_name)()
                    passed += 1
                    print(f"  ✓ {test_class.__name__}.{method_name}")
                except AssertionError as e:
                    failed += 1
                    errors.append((test_class.__name__, method_name, str(e), traceback.format_exc()))
                    print(f"  ✗ {test_class.__name__}.{method_name}: {e}")
                except Exception as e:
                    failed += 1
                    errors.append((test_class.__name__, method_name, str(e), traceback.format_exc()))
                    print(f"  ✗ {test_class.__name__}.{method_name}: ERROR - {e}")

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")

    if errors:
        print(f"\nFailures:")
        for cls, method, msg, tb in errors:
            print(f"\n{cls}.{method}:")
            print(f"  {msg}")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
