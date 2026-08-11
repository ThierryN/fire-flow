#!/usr/bin/env python3
"""Tests for generating diagrams from natural language prompts.

These tests verify that the diagram generator can handle various
diagram requests similar to what a user might ask Claude to create.

Each test simulates a prompt scenario and verifies the output is valid.
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
    FlowchartStyle,
    LayoutConfig,
    ArchitectureStyle,
)


def validate_excalidraw(path: Path) -> dict:
    """Validate an excalidraw file and return its data."""
    assert path.exists(), f"File not found: {path}"
    with open(path) as f:
        data = json.load(f)
    assert data["type"] == "excalidraw"
    assert data["version"] == 2
    assert len(data["elements"]) > 0, "Diagram should have elements"
    return data


# ============================================================================
# Flowchart Prompt Tests
# ============================================================================

class TestFlowchartPrompts:
    """Test generating flowcharts from various prompt scenarios."""

    def test_simple_process_flow(self):
        """
        Prompt: "Create a flowchart showing: Start -> Process Data -> End"
        """
        fc = Flowchart(direction="vertical", spacing=80)
        fc.start("Start")
        fc.process("process", "Process Data")
        fc.end("End")
        fc.connect("__start__", "process")
        fc.connect("process", "__end__")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = fc.save(os.path.join(tmpdir, "simple_flow"))
            data = validate_excalidraw(path)
            # Should have: 2 ellipses (start/end) + 1 rect + 3 texts + 2 arrows
            assert len([e for e in data["elements"] if e["type"] == "arrow"]) == 2

    def test_decision_flowchart(self):
        """
        Prompt: "Create a flowchart with a decision:
                 Start -> Check Input -> Valid?
                 If Yes: Process -> End
                 If No: Show Error -> End"
        """
        fc = Flowchart(direction="vertical", spacing=80)
        fc.start("Start")
        fc.process("check", "Check Input")
        fc.decision("valid", "Valid?")
        fc.position_at(300, 280)
        fc.process("process", "Process")
        fc.position_at(100, 280)
        fc.process("error", "Show Error")
        fc.end("End")

        fc.connect("__start__", "check")
        fc.connect("check", "valid")
        fc.connect("valid", "process", label="Yes")
        fc.connect("valid", "error", label="No")
        fc.connect("process", "__end__")
        fc.connect("error", "__end__")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = fc.save(os.path.join(tmpdir, "decision_flow"))
            data = validate_excalidraw(path)
            diamonds = [e for e in data["elements"] if e["type"] == "diamond"]
            assert len(diamonds) == 1

    def test_login_flow(self):
        """
        Prompt: "Create a user login flowchart:
                 1. User enters credentials
                 2. System validates
                 3. If valid, show dashboard
                 4. If invalid, show error and retry"
        """
        fc = Flowchart(direction="vertical")
        fc.start("User Opens App")
        fc.process("enter", "Enter Credentials")
        fc.decision("validate", "Valid?")
        fc.process("dashboard", "Show Dashboard")
        fc.process("error", "Show Error")
        fc.end("End")

        fc.connect("__start__", "enter")
        fc.connect("enter", "validate")
        fc.connect("validate", "dashboard", label="Yes")
        fc.connect("validate", "error", label="No")
        fc.connect("error", "enter")  # Retry loop
        fc.connect("dashboard", "__end__")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = fc.save(os.path.join(tmpdir, "login_flow"))
            data = validate_excalidraw(path)
            arrows = [e for e in data["elements"] if e["type"] == "arrow"]
            assert len(arrows) >= 5

    def test_order_processing_flow(self):
        """
        Prompt: "Create an e-commerce order processing flowchart:
                 Receive Order -> Check Inventory -> In Stock?
                 Yes: Process Payment -> Payment OK? -> Ship Order -> Complete
                 No: Notify Customer -> End"
        """
        fc = Flowchart(direction="vertical", spacing=70)
        fc.start("Receive Order")
        fc.process("inventory", "Check Inventory")
        fc.decision("in_stock", "In Stock?")
        fc.process("payment", "Process Payment")
        fc.decision("payment_ok", "Payment OK?")
        fc.process("ship", "Ship Order")
        fc.process("notify", "Notify Customer")
        fc.end("Complete")

        fc.connect("__start__", "inventory")
        fc.connect("inventory", "in_stock")
        fc.connect("in_stock", "payment", label="Yes")
        fc.connect("in_stock", "notify", label="No")
        fc.connect("payment", "payment_ok")
        fc.connect("payment_ok", "ship", label="Yes")
        fc.connect("payment_ok", "notify", label="No")
        fc.connect("ship", "__end__")
        fc.connect("notify", "__end__")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = fc.save(os.path.join(tmpdir, "order_flow"))
            data = validate_excalidraw(path)
            assert len(data["elements"]) > 10


# ============================================================================
# Architecture Diagram Prompt Tests
# ============================================================================

class TestArchitecturePrompts:
    """Test generating architecture diagrams from various prompt scenarios."""

    def test_simple_web_architecture(self):
        """
        Prompt: "Create an architecture diagram showing:
                 User -> Web Server -> Database"
        """
        arch = ArchitectureDiagram()
        arch.user("user", "User", x=50, y=100)
        arch.component("web", "Web Server", x=200, y=100)
        arch.database("db", "Database", x=400, y=100)
        arch.connect("user", "web", "HTTP")
        arch.connect("web", "db", "SQL")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = arch.save(os.path.join(tmpdir, "web_arch"))
            data = validate_excalidraw(path)
            assert len([e for e in data["elements"] if e["type"] == "ellipse"]) >= 2

    def test_microservices_architecture(self):
        """
        Prompt: "Create a microservices architecture with:
                 - API Gateway
                 - Auth Service
                 - User Service
                 - Order Service
                 - Each service has its own database
                 - Message queue for async communication"
        """
        arch = ArchitectureDiagram()

        # Gateway
        arch.service("gateway", "API Gateway", x=300, y=50, color="violet")

        # Services
        arch.service("auth", "Auth Service", x=100, y=200, color="blue")
        arch.service("users", "User Service", x=300, y=200, color="blue")
        arch.service("orders", "Order Service", x=500, y=200, color="blue")

        # Databases
        arch.database("auth_db", "Auth DB", x=100, y=350, color="green")
        arch.database("user_db", "User DB", x=300, y=350, color="green")
        arch.database("order_db", "Order DB", x=500, y=350, color="green")

        # Message Queue
        arch.component("mq", "Message Queue", x=300, y=450, color="orange")

        # Connections
        arch.connect("gateway", "auth")
        arch.connect("gateway", "users")
        arch.connect("gateway", "orders")
        arch.connect("auth", "auth_db")
        arch.connect("users", "user_db")
        arch.connect("orders", "order_db")
        arch.connect("orders", "mq", "publish")
        arch.connect("mq", "users", "subscribe")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = arch.save(os.path.join(tmpdir, "microservices"))
            data = validate_excalidraw(path)
            components = [e for e in data["elements"] if e["type"] in ("rectangle", "ellipse")]
            assert len(components) >= 7

    def test_cloud_architecture(self):
        """
        Prompt: "Create a cloud architecture diagram showing:
                 - Load Balancer
                 - Multiple app servers (auto-scaling)
                 - Cache layer (Redis)
                 - Primary database with read replica"
        """
        arch = ArchitectureDiagram()

        # Entry
        arch.component("lb", "Load Balancer", x=300, y=50, color="violet")

        # App servers
        arch.component("app1", "App Server 1", x=150, y=180)
        arch.component("app2", "App Server 2", x=350, y=180)
        arch.component("app3", "App Server N", x=550, y=180)

        # Cache
        arch.component("cache", "Redis Cache", x=350, y=320, color="orange")

        # Databases
        arch.database("primary", "Primary DB", x=200, y=450)
        arch.database("replica", "Read Replica", x=450, y=450)

        # Connections
        arch.connect("lb", "app1")
        arch.connect("lb", "app2")
        arch.connect("lb", "app3")
        arch.connect("app1", "cache")
        arch.connect("app2", "cache")
        arch.connect("app3", "cache")
        arch.connect("cache", "primary")
        arch.connect("primary", "replica", "replication")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = arch.save(os.path.join(tmpdir, "cloud_arch"))
            data = validate_excalidraw(path)
            arrows = [e for e in data["elements"] if e["type"] == "arrow"]
            assert len(arrows) >= 7


# ============================================================================
# UML Diagram Prompt Tests
# ============================================================================

class TestUMLPrompts:
    """Test generating UML diagrams from various prompt scenarios."""

    def test_class_diagram_inheritance(self):
        """
        Prompt: "Create a class diagram showing:
                 - Base class: Shape with area() method
                 - Subclasses: Circle, Rectangle, Triangle"
        """
        d = Diagram(diagram_style=DiagramStyle(roughness=0))

        # Base class
        base = d.box(250, 50, "<<abstract>>\nShape\n─────────\n+ area(): float",
                     color="blue", width=160, height=80)

        # Subclasses
        circle = d.box(50, 200, "Circle\n─────────\n- radius: float\n+ area(): float",
                       color="blue", width=140, height=80)
        rect = d.box(250, 200, "Rectangle\n─────────\n- width: float\n- height: float\n+ area(): float",
                     color="blue", width=140, height=100)
        tri = d.box(450, 200, "Triangle\n─────────\n- base: float\n- height: float\n+ area(): float",
                    color="blue", width=140, height=100)

        # Inheritance arrows
        d.arrow_between(circle, base, from_side="top", to_side="bottom")
        d.arrow_between(rect, base, from_side="top", to_side="bottom")
        d.arrow_between(tri, base, from_side="top", to_side="bottom")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "class_inheritance"))
            data = validate_excalidraw(path)
            rects = [e for e in data["elements"] if e["type"] == "rectangle"]
            assert len(rects) == 4

    def test_use_case_diagram(self):
        """
        Prompt: "Create a use case diagram for an online shopping system:
                 Actors: Customer, Admin
                 Use cases: Browse Products, Add to Cart, Checkout, Manage Inventory"
        """
        d = Diagram()

        # System boundary
        d.box(150, 50, "Online Shopping System", color="gray", width=400, height=350)

        # Actors
        customer = d.box(30, 150, "Customer", shape="ellipse", color="gray", width=80)
        admin = d.box(600, 150, "Admin", shape="ellipse", color="gray", width=80)

        # Use cases
        browse = d.box(250, 100, "Browse Products", shape="ellipse", color="blue", width=140)
        cart = d.box(400, 100, "Add to Cart", shape="ellipse", color="blue", width=120)
        checkout = d.box(250, 220, "Checkout", shape="ellipse", color="blue", width=100)
        inventory = d.box(400, 220, "Manage Inventory", shape="ellipse", color="blue", width=140)

        # Associations
        d.line_between(customer, browse)
        d.line_between(customer, cart)
        d.line_between(customer, checkout)
        d.line_between(admin, inventory)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "use_case"))
            data = validate_excalidraw(path)
            ellipses = [e for e in data["elements"] if e["type"] == "ellipse"]
            assert len(ellipses) == 6

    def test_sequence_diagram(self):
        """
        Prompt: "Create a sequence diagram for user authentication:
                 1. User sends login request to AuthController
                 2. AuthController calls UserService to validate
                 3. UserService queries Database
                 4. Response flows back"
        """
        d = Diagram(diagram_style=DiagramStyle(roughness=0))

        # Participants
        user = d.box(50, 50, "User", color="gray", width=80)
        auth = d.box(200, 50, "AuthController", color="blue", width=120)
        svc = d.box(380, 50, "UserService", color="blue", width=100)
        db = d.box(540, 50, "Database", color="green", width=80)

        # Lifelines (vertical dashed lines) - simplified as messages
        # Messages
        y = 120
        msg1_s = d.box(90, y, "", width=1, height=1)
        msg1_e = d.box(200, y, "", width=1, height=1)
        d.arrow_between(msg1_s, msg1_e, label="1: login()")

        y = 160
        msg2_s = d.box(260, y, "", width=1, height=1)
        msg2_e = d.box(380, y, "", width=1, height=1)
        d.arrow_between(msg2_s, msg2_e, label="2: validate()")

        y = 200
        msg3_s = d.box(430, y, "", width=1, height=1)
        msg3_e = d.box(540, y, "", width=1, height=1)
        d.arrow_between(msg3_s, msg3_e, label="3: query()")

        y = 240
        msg4_s = d.box(540, y, "", width=1, height=1)
        msg4_e = d.box(200, y, "", width=1, height=1)
        d.arrow_between(msg4_s, msg4_e, label="4: result")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "sequence"))
            data = validate_excalidraw(path)
            arrows = [e for e in data["elements"] if e["type"] == "arrow"]
            assert len(arrows) >= 4

    def test_state_machine_diagram(self):
        """
        Prompt: "Create a state machine for an order:
                 States: Pending, Processing, Shipped, Delivered, Cancelled
                 Transitions: confirm, ship, deliver, cancel"
        """
        d = Diagram(diagram_style=DiagramStyle(roughness=0))

        # Initial state
        initial = d.box(50, 150, "●", shape="ellipse", color="black", width=20, height=20)

        # States
        pending = d.box(120, 130, "Pending", color="blue", width=100)
        processing = d.box(270, 130, "Processing", color="blue", width=100)
        shipped = d.box(420, 130, "Shipped", color="blue", width=100)
        delivered = d.box(570, 130, "Delivered", color="green", width=100)
        cancelled = d.box(270, 250, "Cancelled", color="red", width=100)

        # Final state
        final = d.box(700, 150, "◉", shape="ellipse", color="black", width=20, height=20)

        # Transitions
        d.arrow_between(initial, pending)
        d.arrow_between(pending, processing, label="confirm")
        d.arrow_between(processing, shipped, label="ship")
        d.arrow_between(shipped, delivered, label="deliver")
        d.arrow_between(delivered, final)
        d.arrow_between(pending, cancelled, label="cancel")
        d.arrow_between(processing, cancelled, label="cancel")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "state_machine"))
            data = validate_excalidraw(path)
            arrows = [e for e in data["elements"] if e["type"] == "arrow"]
            assert len(arrows) >= 6


# ============================================================================
# Complex/Real-World Prompt Tests
# ============================================================================

class TestComplexPrompts:
    """Test generating complex real-world diagrams."""

    def test_ci_cd_pipeline(self):
        """
        Prompt: "Create a CI/CD pipeline diagram showing:
                 Code Commit -> Build -> Test -> Security Scan ->
                 Deploy to Staging -> Approval -> Deploy to Production"
        """
        fc = Flowchart(
            direction="horizontal",
            spacing=60,
            flowchart_style=FlowchartStyle(process_color="blue")
        )
        fc.start("Commit")
        fc.process("build", "Build")
        fc.process("test", "Test")
        fc.process("scan", "Security\nScan")
        fc.process("staging", "Deploy\nStaging")
        fc.decision("approve", "Approved?")
        fc.process("prod", "Deploy\nProduction")
        fc.end("Done")

        fc.connect("__start__", "build")
        fc.connect("build", "test")
        fc.connect("test", "scan")
        fc.connect("scan", "staging")
        fc.connect("staging", "approve")
        fc.connect("approve", "prod", label="Yes")
        fc.connect("prod", "__end__")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = fc.save(os.path.join(tmpdir, "cicd"))
            data = validate_excalidraw(path)
            assert len(data["elements"]) > 10

    def test_data_flow_diagram(self):
        """
        Prompt: "Create a data flow diagram for a payment system:
                 Customer submits payment -> Payment Gateway validates ->
                 Bank processes -> Merchant receives confirmation"
        """
        d = Diagram()

        # External entities (rectangles)
        customer = d.box(50, 150, "Customer", color="gray")
        merchant = d.box(650, 150, "Merchant", color="gray")

        # Processes (circles/ellipses)
        gateway = d.box(220, 140, "Payment\nGateway", shape="ellipse", color="blue", width=100, height=80)
        bank = d.box(420, 140, "Bank\nProcessor", shape="ellipse", color="blue", width=100, height=80)

        # Data store
        d.box(320, 280, "Transaction Log", color="green", width=120)

        # Data flows
        d.arrow_between(customer, gateway, label="Payment Data")
        d.arrow_between(gateway, bank, label="Auth Request")
        d.arrow_between(bank, gateway, label="Auth Response")
        d.arrow_between(gateway, merchant, label="Confirmation")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "data_flow"))
            data = validate_excalidraw(path)
            assert len([e for e in data["elements"] if e["type"] == "arrow"]) >= 4

    def test_network_topology(self):
        """
        Prompt: "Create a network diagram showing:
                 Internet -> Firewall -> DMZ (Web Servers) ->
                 Internal Firewall -> Internal Network (App Servers, DB)"
        """
        d = Diagram()

        # Internet
        internet = d.box(50, 200, "Internet", shape="ellipse", color="gray")

        # Firewalls
        fw1 = d.box(180, 190, "Firewall", color="red", width=80, height=60)
        fw2 = d.box(450, 190, "Internal\nFirewall", color="red", width=80, height=60)

        # DMZ
        d.box(280, 100, "DMZ", color="orange", width=150, height=200)
        web1 = d.box(300, 130, "Web 1", color="blue", width=70, height=40)
        web2 = d.box(300, 200, "Web 2", color="blue", width=70, height=40)

        # Internal
        d.box(550, 100, "Internal", color="green", width=200, height=200)
        app = d.box(580, 130, "App Server", color="blue", width=90, height=40)
        db = d.box(580, 200, "Database", shape="ellipse", color="green", width=90, height=50)

        # Connections
        d.arrow_between(internet, fw1)
        d.arrow_between(fw1, web1)
        d.arrow_between(web1, fw2)
        d.arrow_between(fw2, app)
        d.arrow_between(app, db)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "network"))
            data = validate_excalidraw(path)
            rects = [e for e in data["elements"] if e["type"] == "rectangle"]
            assert len(rects) >= 6


# ============================================================================
# Style/Customization Prompt Tests
# ============================================================================

class TestStylePrompts:
    """Test generating diagrams with specific style requirements."""

    def test_clean_professional_style(self):
        """
        Prompt: "Create a clean, professional diagram with no hand-drawn effect"
        """
        d = Diagram(diagram_style=DiagramStyle(
            roughness=0,
            stroke_width=1,
            color_scheme="corporate"
        ))
        d.box(100, 100, "Component A", color=d.scheme_color("primary"))
        d.box(300, 100, "Component B", color=d.scheme_color("secondary"))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "professional"))
            data = validate_excalidraw(path)
            # Check roughness is 0 on elements
            for elem in data["elements"]:
                if elem["type"] == "rectangle":
                    assert elem["roughness"] == 0

    def test_sketchy_whiteboard_style(self):
        """
        Prompt: "Create a diagram that looks hand-drawn, like on a whiteboard"
        """
        d = Diagram(diagram_style=DiagramStyle(
            roughness=2,
            stroke_width=2
        ))
        d.box(100, 100, "Idea 1", color="blue")
        d.box(300, 100, "Idea 2", color="green")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "sketchy"))
            data = validate_excalidraw(path)
            for elem in data["elements"]:
                if elem["type"] == "rectangle":
                    assert elem["roughness"] == 2

    def test_monochrome_style(self):
        """
        Prompt: "Create a black and white diagram for printing"
        """
        d = Diagram(diagram_style=DiagramStyle(color_scheme="monochrome"))
        d.box(100, 100, "Box 1", color=d.scheme_color("primary"))
        d.box(300, 100, "Box 2", color=d.scheme_color("secondary"))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = d.save(os.path.join(tmpdir, "monochrome"))
            data = validate_excalidraw(path)
            assert len(data["elements"]) > 0


# ============================================================================
# Test Runner
# ============================================================================

def run_tests():
    """Run all tests and report results."""
    import traceback

    test_classes = [
        TestFlowchartPrompts,
        TestArchitecturePrompts,
        TestUMLPrompts,
        TestComplexPrompts,
        TestStylePrompts,
    ]

    total = 0
    passed = 0
    failed = 0
    errors = []

    print("Running prompt generation tests...\n")

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
