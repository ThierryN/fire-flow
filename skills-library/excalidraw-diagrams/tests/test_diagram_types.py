#!/usr/bin/env python3
"""Tests for diagram types and configuration classes.

This module tests:
- Configuration classes (DiagramStyle, BoxStyle, FlowchartStyle, etc.)
- AutoLayoutFlowchart with various node types
- UML Structural diagrams (Class, Component, Deployment, Composite Structure)
- UML Behavioral diagrams (Use Case, Activity, State Machine, Sequence, Communication)
"""

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
    AutoLayoutFlowchart,
    DiagramStyle,
    BoxStyle,
    RoutingConfig,
    FlowchartStyle,
    LayoutConfig,
    ArchitectureStyle,
    COLOR_SCHEMES,
    get_scheme_color,
    FONT_METRICS,
    measure_text_for_box,
)


# ============================================================================
# Configuration Class Tests
# ============================================================================

class TestDiagramStyle:
    """Tests for DiagramStyle configuration."""

    def test_default_values(self):
        style = DiagramStyle()
        assert style.roughness == 1
        assert style.stroke_style == "solid"
        assert style.stroke_width == 2
        assert style.color_scheme == "default"

    def test_custom_values(self):
        style = DiagramStyle(
            roughness=0,
            stroke_style="dashed",
            stroke_width=3,
            color_scheme="corporate"
        )
        assert style.roughness == 0
        assert style.stroke_style == "dashed"
        assert style.stroke_width == 3
        assert style.color_scheme == "corporate"

    def test_diagram_uses_style(self):
        style = DiagramStyle(roughness=0, stroke_width=1)
        d = Diagram(diagram_style=style)
        assert d.style.roughness == 0
        assert d.style.stroke_width == 1

    def test_style_applied_to_elements(self):
        style = DiagramStyle(roughness=0, stroke_width=1)
        d = Diagram(diagram_style=style)
        d.box(100, 100, "Test")
        # Check the rectangle element has the style applied
        rect = d.elements[0]
        assert rect["roughness"] == 0
        assert rect["strokeWidth"] == 1


class TestBoxStyle:
    """Tests for BoxStyle configuration."""

    def test_default_values(self):
        style = BoxStyle()
        assert style.h_padding == 40
        assert style.v_padding == 24
        assert style.min_width == 80
        assert style.min_height == 40
        assert style.font_size == 18
        assert style.font_family == "hand"

    def test_custom_padding(self):
        style = BoxStyle(h_padding=60, v_padding=40)
        d = Diagram(box_style=style)
        # Box dimensions should reflect the padding
        elem = d.box(0, 0, "X")  # Single char
        # With larger padding, width should be larger
        assert elem.width >= style.min_width


class TestFlowchartStyle:
    """Tests for FlowchartStyle configuration."""

    def test_default_colors(self):
        style = FlowchartStyle()
        assert style.start_color == "green"
        assert style.end_color == "red"
        assert style.process_color == "blue"
        assert style.decision_color == "yellow"

    def test_custom_colors(self):
        style = FlowchartStyle(
            start_color="cyan",
            decision_color="orange"
        )
        assert style.start_color == "cyan"
        assert style.decision_color == "orange"

    def test_flowchart_uses_style(self):
        style = FlowchartStyle(start_color="violet", process_color="teal")
        fc = Flowchart(flowchart_style=style)
        assert fc.flowchart_style.start_color == "violet"
        assert fc.flowchart_style.process_color == "teal"


class TestLayoutConfig:
    """Tests for LayoutConfig configuration."""

    def test_default_values(self):
        config = LayoutConfig()
        assert config.horizontal_spacing == 80
        assert config.vertical_spacing == 100
        assert config.direction == "TB"
        assert config.column_gap == 150

    def test_custom_spacing(self):
        config = LayoutConfig(
            horizontal_spacing=120,
            vertical_spacing=150
        )
        assert config.horizontal_spacing == 120
        assert config.vertical_spacing == 150


class TestArchitectureStyle:
    """Tests for ArchitectureStyle configuration."""

    def test_default_colors(self):
        style = ArchitectureStyle()
        assert style.component_color == "blue"
        assert style.database_color == "green"
        assert style.service_color == "violet"
        assert style.user_color == "gray"

    def test_architecture_uses_style(self):
        style = ArchitectureStyle(component_color="orange")
        arch = ArchitectureDiagram(architecture_style=style)
        assert arch.arch_style.component_color == "orange"


class TestColorSchemes:
    """Tests for color scheme functionality."""

    def test_all_schemes_exist(self):
        expected = ["default", "monochrome", "corporate", "vibrant", "earth"]
        for scheme in expected:
            assert scheme in COLOR_SCHEMES

    def test_scheme_has_required_roles(self):
        required_roles = ["primary", "secondary", "accent", "warning", "danger", "neutral"]
        for scheme_name, scheme in COLOR_SCHEMES.items():
            for role in required_roles:
                assert role in scheme, f"Scheme '{scheme_name}' missing role '{role}'"

    def test_get_scheme_color(self):
        assert get_scheme_color("default", "primary") == "blue"
        assert get_scheme_color("monochrome", "primary") == "black"
        assert get_scheme_color("corporate", "accent") == "violet"

    def test_diagram_scheme_color_method(self):
        d = Diagram(diagram_style=DiagramStyle(color_scheme="vibrant"))
        assert d.scheme_color("primary") == "violet"
        assert d.scheme_color("secondary") == "cyan"


class TestMeasureTextForBox:
    """Tests for text measurement function."""

    def test_single_line(self):
        width, height = measure_text_for_box("Hello")
        assert width >= 80  # Minimum width
        assert height >= 40  # Minimum height

    def test_multiline(self):
        single_w, single_h = measure_text_for_box("Line 1")
        multi_w, multi_h = measure_text_for_box("Line 1\nLine 2\nLine 3")
        # Multiline should be taller
        assert multi_h > single_h

    def test_long_text(self):
        short_w, _ = measure_text_for_box("Hi")
        long_w, _ = measure_text_for_box("This is a much longer label")
        assert long_w > short_w


# ============================================================================
# AutoLayoutFlowchart Tests
# ============================================================================

class TestAutoLayoutFlowchart:
    """Tests for AutoLayoutFlowchart class."""

    def test_creation(self):
        fc = AutoLayoutFlowchart()
        assert fc._nodes == {}
        assert fc._edges == []

    def test_add_node(self):
        fc = AutoLayoutFlowchart()
        fc.add_node("start", "Start", shape="ellipse", color="green", node_type="terminal")
        assert "start" in fc._nodes
        assert fc._nodes["start"]["node_type"] == "terminal"
        assert fc._nodes["start"]["shape"] == "ellipse"

    def test_add_edge(self):
        fc = AutoLayoutFlowchart()
        fc.add_node("a", "A")
        fc.add_node("b", "B")
        fc.add_edge("a", "b", label="connects")
        assert len(fc._edges) == 1
        assert fc._edges[0]["from"] == "a"
        assert fc._edges[0]["to"] == "b"
        assert fc._edges[0]["label"] == "connects"

    def test_node_types(self):
        fc = AutoLayoutFlowchart()
        fc.add_node("t1", "Start", node_type="terminal")
        fc.add_node("p1", "Process", node_type="process")
        fc.add_node("d1", "Decision?", node_type="decision")
        assert fc._nodes["t1"]["node_type"] == "terminal"
        assert fc._nodes["p1"]["node_type"] == "process"
        assert fc._nodes["d1"]["node_type"] == "decision"

    def test_with_diagram_style(self):
        style = DiagramStyle(roughness=0, color_scheme="corporate")
        fc = AutoLayoutFlowchart(diagram_style=style)
        assert fc.style.roughness == 0
        assert fc.style.color_scheme == "corporate"

    def test_with_layout_config(self):
        config = LayoutConfig(vertical_spacing=120)
        fc = AutoLayoutFlowchart(layout_config=config)
        assert fc.layout.vertical_spacing == 120


# ============================================================================
# UML Structural Diagram Tests
# ============================================================================

class TestClassDiagram:
    """Tests for Class Diagram generation."""

    def test_simple_class(self):
        """Test creating a single class box."""
        d = Diagram()
        # Class with name, attributes, and methods
        class_text = "<<class>>\nPerson\n---------\n- name: string\n- age: int\n---------\n+ getName()\n+ setAge()"
        d.box(100, 100, class_text, color="blue", width=150, height=120)
        assert len(d.elements) == 2  # rect + text
        assert d.elements[0]["type"] == "rectangle"

    def test_class_inheritance(self):
        """Test class inheritance relationship."""
        d = Diagram()
        parent = d.box(200, 50, "Animal\n---------\n+ speak()", color="blue")
        child1 = d.box(100, 200, "Dog\n---------\n+ bark()", color="blue")
        child2 = d.box(300, 200, "Cat\n---------\n+ meow()", color="blue")

        # Inheritance arrows (hollow triangle head) - using regular arrows for now
        d.arrow_between(child1, parent, from_side="top", to_side="bottom")
        d.arrow_between(child2, parent, from_side="top", to_side="bottom")

        # Should have 3 classes + 2 arrows
        arrows = [e for e in d.elements if e["type"] == "arrow"]
        assert len(arrows) == 2

    def test_class_association(self):
        """Test class association relationship."""
        d = Diagram()
        class1 = d.box(100, 100, "Order", color="blue")
        class2 = d.box(350, 100, "Product", color="blue")
        d.arrow_between(class1, class2, label="contains *")

        assert len([e for e in d.elements if e["type"] == "arrow"]) == 1


class TestComponentDiagram:
    """Tests for Component Diagram generation."""

    def test_simple_component(self):
        """Test creating component boxes."""
        arch = ArchitectureDiagram()
        arch.component("api", "<<component>>\nAPI Gateway", x=100, y=100)
        arch.component("auth", "<<component>>\nAuth Service", x=300, y=100)
        arch.connect("api", "auth", "authenticates")

        assert "api" in arch._components
        assert "auth" in arch._components

    def test_component_with_interfaces(self):
        """Test component with provided/required interfaces."""
        d = Diagram()
        # Component box
        comp = d.box(100, 100, "<<component>>\nPayment Service", color="blue", width=180)
        # Provided interface (lollipop) - simplified as small ellipse
        interface = d.box(280, 130, "IPayment", shape="ellipse", color="blue", width=60, height=30)
        d.line_between(comp, interface)

        assert len(d.elements) >= 4  # 2 boxes (each = rect+text) + line


class TestDeploymentDiagram:
    """Tests for Deployment Diagram generation."""

    def test_node_with_artifacts(self):
        """Test deployment node containing artifacts."""
        d = Diagram()
        # Deployment node (3D box effect using multiple rectangles)
        d.box(50, 50, "<<device>>\nWeb Server", color="gray", width=250, height=200)
        # Artifacts inside
        d.box(70, 100, "<<artifact>>\nnginx.conf", color="blue", width=100, height=50)
        d.box(180, 100, "<<artifact>>\napp.war", color="blue", width=100, height=50)

        rects = [e for e in d.elements if e["type"] == "rectangle"]
        assert len(rects) == 3

    def test_deployment_connection(self):
        """Test connection between deployment nodes."""
        d = Diagram()
        server1 = d.box(50, 100, "<<device>>\nApp Server", color="gray")
        server2 = d.box(300, 100, "<<device>>\nDB Server", color="gray")
        d.arrow_between(server1, server2, label="<<TCP/IP>>")

        arrows = [e for e in d.elements if e["type"] == "arrow"]
        assert len(arrows) == 1


class TestCompositeStructureDiagram:
    """Tests for Composite Structure Diagram generation."""

    def test_composite_with_parts(self):
        """Test composite structure with internal parts."""
        d = Diagram()
        # Outer composite
        d.box(50, 50, "<<composite>>\nCar", color="gray", width=350, height=200)
        # Internal parts
        d.box(70, 100, "Engine", color="blue", width=100, height=60)
        d.box(190, 100, "Transmission", color="blue", width=100, height=60)

        # Internal connection
        engine = d.box(70, 100, "", width=100, height=60)
        trans = d.box(190, 100, "", width=100, height=60)

        rects = [e for e in d.elements if e["type"] == "rectangle"]
        assert len(rects) >= 3


# ============================================================================
# UML Behavioral Diagram Tests
# ============================================================================

class TestUseCaseDiagram:
    """Tests for Use Case Diagram generation."""

    def test_actor_and_use_case(self):
        """Test actor and use case elements."""
        d = Diagram()
        # Actor (stick figure simplified as ellipse with label)
        actor = d.box(50, 150, "Customer", shape="ellipse", color="gray", width=80, height=40)
        # Use case (ellipse)
        usecase = d.box(200, 100, "Place Order", shape="ellipse", color="blue", width=120, height=60)
        # Association
        d.line_between(actor, usecase)

        ellipses = [e for e in d.elements if e["type"] == "ellipse"]
        assert len(ellipses) == 2

    def test_use_case_extend(self):
        """Test extend relationship between use cases."""
        d = Diagram()
        base = d.box(100, 100, "Checkout", shape="ellipse", color="blue")
        extension = d.box(100, 250, "Apply Coupon", shape="ellipse", color="blue")
        d.arrow_between(extension, base, label="<<extend>>", routing="straight")

        arrows = [e for e in d.elements if e["type"] == "arrow"]
        assert len(arrows) == 1

    def test_use_case_include(self):
        """Test include relationship between use cases."""
        d = Diagram()
        base = d.box(100, 100, "Login", shape="ellipse", color="blue")
        included = d.box(300, 100, "Validate Password", shape="ellipse", color="blue")
        d.arrow_between(base, included, label="<<include>>")

        arrows = [e for e in d.elements if e["type"] == "arrow"]
        assert len(arrows) == 1


class TestActivityDiagram:
    """Tests for Activity Diagram generation."""

    def test_activity_flow(self):
        """Test basic activity flow."""
        fc = Flowchart(direction="vertical")
        # Initial node (filled circle)
        fc.start("●")
        fc.process("act1", "Receive Order")
        fc.decision("check", "In Stock?")
        fc.process("act2", "Ship Order")
        fc.process("act3", "Back Order")
        fc.end("◉")  # Final node

        fc.connect("__start__", "act1")
        fc.connect("act1", "check")
        fc.connect("check", "act2", label="Yes")
        fc.connect("check", "act3", label="No")
        fc.connect("act2", "__end__")
        fc.connect("act3", "__end__")

        arrows = [e for e in fc.elements if e["type"] == "arrow"]
        assert len(arrows) == 6

    def test_activity_swimlanes(self):
        """Test activity diagram with swimlanes (represented as columns)."""
        d = Diagram()
        # Swimlane headers
        d.box(50, 20, "Customer", color="gray", width=200)
        d.box(270, 20, "System", color="gray", width=200)

        # Activities in swimlanes
        d.box(100, 100, "Browse", color="blue")
        d.box(320, 100, "Display Items", color="blue")

        rects = [e for e in d.elements if e["type"] == "rectangle"]
        assert len(rects) == 4


class TestStateMachineDiagram:
    """Tests for State Machine Diagram generation."""

    def test_simple_state_machine(self):
        """Test basic state machine."""
        fc = Flowchart(direction="vertical")
        fc.start("●")  # Initial pseudo-state
        fc.process("idle", "Idle", color="blue")
        fc.process("processing", "Processing", color="blue")
        fc.process("complete", "Complete", color="green")
        fc.end("◉")  # Final state

        fc.connect("__start__", "idle")
        fc.connect("idle", "processing", label="start")
        fc.connect("processing", "complete", label="done")
        fc.connect("complete", "__end__")

        states = [e for e in fc.elements if e["type"] == "rectangle"]
        assert len(states) == 3

    def test_state_with_internal_actions(self):
        """Test state with entry/do/exit actions."""
        d = Diagram()
        state_text = "Processing\n─────────\nentry / startTimer\ndo / process\nexit / stopTimer"
        d.box(100, 100, state_text, color="blue", width=150, height=100)

        assert len(d.elements) == 2  # rect + text


class TestSequenceDiagram:
    """Tests for Sequence Diagram generation."""

    def test_lifelines(self):
        """Test sequence diagram lifelines."""
        d = Diagram()
        # Participants (boxes at top)
        p1 = d.box(50, 50, "Client", color="blue", width=80)
        p2 = d.box(200, 50, "Server", color="blue", width=80)
        p3 = d.box(350, 50, "Database", color="blue", width=80)

        # Lifelines (dashed vertical lines) - represented as regular lines
        d.line_between(p1, d.box(50 + 40, 300, "", width=1, height=1))
        d.line_between(p2, d.box(200 + 40, 300, "", width=1, height=1))
        d.line_between(p3, d.box(350 + 40, 300, "", width=1, height=1))

        lines = [e for e in d.elements if e["type"] == "line"]
        assert len(lines) == 3

    def test_messages(self):
        """Test sequence diagram messages."""
        d = Diagram()
        # Simplified: messages as horizontal arrows
        # Sync message (solid line, filled arrow)
        d.box(50, 50, "Client", color="blue")
        d.box(200, 50, "Server", color="blue")

        # Messages at different y positions
        msg1_start = d.box(90, 120, "", width=1, height=1)
        msg1_end = d.box(200, 120, "", width=1, height=1)
        d.arrow_between(msg1_start, msg1_end, label="request()")

        arrows = [e for e in d.elements if e["type"] == "arrow"]
        assert len(arrows) >= 1

    def test_activation_bars(self):
        """Test activation bars on lifelines."""
        d = Diagram()
        # Participant
        d.box(100, 50, "Service", color="blue", width=80)
        # Activation bar (narrow rectangle on lifeline)
        d.box(135, 100, "", color="gray", width=10, height=80)

        rects = [e for e in d.elements if e["type"] == "rectangle"]
        assert len(rects) == 2


class TestCommunicationDiagram:
    """Tests for Communication Diagram generation."""

    def test_objects_and_links(self):
        """Test communication diagram with objects and links."""
        d = Diagram()
        # Objects
        obj1 = d.box(50, 100, ":OrderController", color="blue")
        obj2 = d.box(250, 100, ":Order", color="blue")
        obj3 = d.box(450, 100, ":Customer", color="blue")

        # Links with numbered messages
        d.arrow_between(obj1, obj2, label="1: create()")
        d.arrow_between(obj2, obj3, label="2: validate()")

        arrows = [e for e in d.elements if e["type"] == "arrow"]
        assert len(arrows) == 2

    def test_self_message(self):
        """Test self-message (recursive call)."""
        d = Diagram()
        obj = d.box(100, 100, ":Calculator", color="blue")
        # Self-loop represented as arrow that curves back
        # Simplified: just test object creation
        assert len([e for e in d.elements if e["type"] == "rectangle"]) == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestDiagramSaveAndLoad:
    """Tests for saving and loading diagrams."""

    def test_save_flowchart(self):
        """Test saving a flowchart."""
        fc = Flowchart()
        fc.start("Start")
        fc.process("p1", "Process")
        fc.end("End")
        fc.connect("__start__", "p1")
        fc.connect("p1", "__end__")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = fc.save(os.path.join(tmpdir, "flowchart"))
            assert path.exists()
            with open(path) as f:
                data = json.load(f)
            assert data["type"] == "excalidraw"
            assert len(data["elements"]) > 0

    def test_save_architecture_diagram(self):
        """Test saving an architecture diagram."""
        arch = ArchitectureDiagram()
        arch.user("user", "User", x=50, y=100)
        arch.component("api", "API", x=200, y=100)
        arch.database("db", "Database", x=350, y=100)
        arch.connect("user", "api")
        arch.connect("api", "db")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = arch.save(os.path.join(tmpdir, "arch"))
            assert path.exists()

    def test_valid_excalidraw_format(self):
        """Test that generated diagrams are valid Excalidraw format."""
        d = Diagram(diagram_style=DiagramStyle(roughness=0))
        d.box(100, 100, "Test", color="blue")
        d.box(300, 100, "Test2", color="green")

        data = d.to_dict()

        # Required fields
        assert data["type"] == "excalidraw"
        assert data["version"] == 2
        assert "elements" in data
        assert "appState" in data
        assert "files" in data

        # All elements should have required fields
        for elem in data["elements"]:
            assert "id" in elem
            assert "type" in elem
            assert "x" in elem
            assert "y" in elem


# ============================================================================
# Test Runner
# ============================================================================

def run_tests():
    """Run all tests and report results."""
    import traceback

    test_classes = [
        # Configuration tests
        TestDiagramStyle,
        TestBoxStyle,
        TestFlowchartStyle,
        TestLayoutConfig,
        TestArchitectureStyle,
        TestColorSchemes,
        TestMeasureTextForBox,
        # AutoLayoutFlowchart tests
        TestAutoLayoutFlowchart,
        # UML Structural diagrams
        TestClassDiagram,
        TestComponentDiagram,
        TestDeploymentDiagram,
        TestCompositeStructureDiagram,
        # UML Behavioral diagrams
        TestUseCaseDiagram,
        TestActivityDiagram,
        TestStateMachineDiagram,
        TestSequenceDiagram,
        TestCommunicationDiagram,
        # Integration tests
        TestDiagramSaveAndLoad,
    ]

    total = 0
    passed = 0
    failed = 0
    errors = []

    print("Running diagram type tests...\n")

    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total += 1
                try:
                    getattr(instance, method_name)()
                    passed += 1
                    print(f"  ✓ {method_name}")
                except AssertionError as e:
                    failed += 1
                    errors.append((test_class.__name__, method_name, str(e), traceback.format_exc()))
                    print(f"  ✗ {method_name}: {e}")
                except Exception as e:
                    failed += 1
                    errors.append((test_class.__name__, method_name, str(e), traceback.format_exc()))
                    print(f"  ✗ {method_name}: ERROR - {e}")

    print(f"\n{'='*60}")
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
