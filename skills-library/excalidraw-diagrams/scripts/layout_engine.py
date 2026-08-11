#!/usr/bin/env python3
"""
Layout Engine for Excalidraw Diagrams

Uses grandalf for hierarchical (Sugiyama) graph layout, which is ideal for
flowcharts, process diagrams, and directed graphs.

Install grandalf: pip install grandalf
"""

import subprocess
import sys
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


def ensure_grandalf():
    """Ensure grandalf is installed, install if not."""
    try:
        import grandalf
        return True
    except ImportError:
        print("Installing grandalf for graph layout...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "grandalf", "-q"])
        return True


@dataclass
class LayoutNode:
    """A node in the layout graph."""
    id: str
    label: str
    width: float = 150
    height: float = 60
    data: Any = None

    # Computed by layout
    x: float = 0
    y: float = 0


@dataclass
class LayoutEdge:
    """An edge in the layout graph."""
    source_id: str
    target_id: str
    label: Optional[str] = None


@dataclass
class LayoutResult:
    """Result of layout computation."""
    nodes: Dict[str, LayoutNode]
    edges: List[LayoutEdge]
    width: float = 0
    height: float = 0
    layers: List[List[str]] = field(default_factory=list)  # Node IDs grouped by layer
    aspect_ratio: float = 1.0


class HierarchicalLayout:
    """
    Hierarchical (Sugiyama) layout for directed graphs.

    This layout arranges nodes in layers from top to bottom,
    minimizing edge crossings. Perfect for flowcharts and process diagrams.
    """

    def __init__(
        self,
        horizontal_spacing: float = 80,
        vertical_spacing: float = 100,
        direction: str = "TB"  # TB (top-bottom), LR (left-right)
    ):
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing
        self.direction = direction

    def layout(
        self,
        nodes: List[LayoutNode],
        edges: List[LayoutEdge]
    ) -> LayoutResult:
        """
        Compute layout for the given nodes and edges.

        Returns LayoutResult with positioned nodes.
        """
        ensure_grandalf()
        from grandalf.graphs import Vertex, Edge, Graph
        from grandalf.layouts import SugiyamaLayout

        if not nodes:
            return LayoutResult(nodes={}, edges=edges)

        # Create grandalf vertices
        vertices = {}
        for node in nodes:
            v = Vertex(node.id)
            v.data = node
            # Create view with dimensions
            v.view = _NodeView(node.width, node.height)
            vertices[node.id] = v

        # Create grandalf edges
        g_edges = []
        for edge in edges:
            if edge.source_id in vertices and edge.target_id in vertices:
                e = Edge(vertices[edge.source_id], vertices[edge.target_id])
                g_edges.append(e)

        # Create graph
        g = Graph(list(vertices.values()), g_edges)

        # Handle disconnected components
        result_nodes = {}
        total_width = 0
        max_height = 0
        layers = []

        for i, component in enumerate(g.C):
            # Apply Sugiyama layout to each component
            sug = SugiyamaLayout(component)

            # Configure layout
            sug.xspace = self.horizontal_spacing
            sug.yspace = self.vertical_spacing

            # Run layout
            sug.init_all()
            sug.draw()

            # Extract positions and group by layer (y-coordinate)
            layer_nodes = {}  # y -> list of (node, x)
            component_min_x = float('inf')
            component_max_x = 0
            component_max_y = 0

            for v in component.sV:
                x, y = v.view.xy
                # Adjust for component offset
                x += total_width
                node = v.data

                # Round y to avoid floating point issues when grouping
                layer_y = round(y, 1)
                if layer_y not in layer_nodes:
                    layer_nodes[layer_y] = []
                layer_nodes[layer_y].append((node, x))

                # Track bounds
                component_min_x = min(component_min_x, x - node.width/2)
                component_max_x = max(component_max_x, x + node.width/2)
                component_max_y = max(component_max_y, y + node.height/2)

            # Build parent-child relationships from edges
            parents = {}  # node_id -> list of parent node_ids
            children = {}  # node_id -> list of child node_ids
            node_by_id = {n.id: n for n, _ in sum(layer_nodes.values(), [])}

            for edge in edges:
                if edge.source_id in node_by_id and edge.target_id in node_by_id:
                    if edge.target_id not in parents:
                        parents[edge.target_id] = []
                    parents[edge.target_id].append(edge.source_id)
                    if edge.source_id not in children:
                        children[edge.source_id] = []
                    children[edge.source_id].append(edge.target_id)

            # Initial placement: center within diagram
            diagram_center_x = (component_min_x + component_max_x) / 2
            for layer_y, nodes_in_layer in layer_nodes.items():
                if len(nodes_in_layer) == 1:
                    node, _ = nodes_in_layer[0]
                    node.x = diagram_center_x
                    node.y = layer_y
                else:
                    nodes_in_layer.sort(key=lambda x: x[1])
                    layer_width = sum(n.width for n, _ in nodes_in_layer) + \
                                  self.horizontal_spacing * (len(nodes_in_layer) - 1)
                    start_x = diagram_center_x - layer_width / 2
                    current_x = start_x
                    for node, _ in nodes_in_layer:
                        node.x = current_x + node.width / 2
                        node.y = layer_y
                        current_x += node.width + self.horizontal_spacing

            # Post-process: center nodes below their single parent
            # Process layers from top to bottom, propagating alignment
            sorted_layers = sorted(layer_nodes.keys())
            for layer_y in sorted_layers:
                for node, _ in layer_nodes[layer_y]:
                    parent_ids = parents.get(node.id, [])
                    if len(parent_ids) == 1:
                        # Single parent - center below it
                        parent = node_by_id.get(parent_ids[0])
                        if parent:
                            parent_children = children.get(parent.id, [])
                            if len(parent_children) == 1:
                                # Direct 1:1 connection - align exactly
                                node.x = parent.x
                            elif len(parent_children) == 2:
                                # Decision node with 2 branches - center decision below parent
                                # Only if this node is not part of a horizontal spread
                                node_children = children.get(node.id, [])
                                if len(node_children) >= 2:
                                    # This is a decision node - center it
                                    node.x = parent.x

                    # Add to result
                    result_nodes[node.id] = node

            # Track layers for potential splitting
            for layer_y in sorted(layer_nodes.keys()):
                layers.append([n.id for n, _ in layer_nodes[layer_y]])

            # Offset next component
            if component_max_x > component_min_x:
                total_width = component_max_x + self.horizontal_spacing * 2
            max_height = max(max_height, component_max_y)

        # Handle direction (rotate if LR)
        if self.direction == "LR":
            for node in result_nodes.values():
                node.x, node.y = node.y, node.x
                node.width, node.height = node.height, node.width
            total_width, max_height = max_height, total_width

        # Calculate aspect ratio
        aspect_ratio = total_width / max_height if max_height > 0 else 1.0

        return LayoutResult(
            nodes=result_nodes,
            edges=edges,
            width=total_width,
            height=max_height,
            layers=layers,
            aspect_ratio=aspect_ratio
        )


class _NodeView:
    """View object for grandalf layout."""
    def __init__(self, w: float, h: float):
        self.w = w
        self.h = h
        self.xy = (0, 0)


class ForceDirectedLayout:
    """
    Force-directed layout using spring model.

    Nodes repel each other while edges act as springs.
    Good for general graphs without clear hierarchy.
    """

    def __init__(
        self,
        iterations: int = 100,
        repulsion: float = 10000,
        attraction: float = 0.1,
        damping: float = 0.9
    ):
        self.iterations = iterations
        self.repulsion = repulsion
        self.attraction = attraction
        self.damping = damping

    def layout(
        self,
        nodes: List[LayoutNode],
        edges: List[LayoutEdge]
    ) -> LayoutResult:
        """
        Compute force-directed layout.
        """
        import math
        import random

        if not nodes:
            return LayoutResult(nodes={}, edges=edges)

        # Initialize positions randomly
        node_dict = {n.id: n for n in nodes}
        positions = {}
        velocities = {}

        for node in nodes:
            positions[node.id] = [random.uniform(0, 500), random.uniform(0, 500)]
            velocities[node.id] = [0, 0]

        # Build adjacency
        adjacency = {n.id: set() for n in nodes}
        for edge in edges:
            if edge.source_id in adjacency and edge.target_id in adjacency:
                adjacency[edge.source_id].add(edge.target_id)
                adjacency[edge.target_id].add(edge.source_id)

        # Iterate
        for _ in range(self.iterations):
            forces = {n.id: [0, 0] for n in nodes}

            # Repulsion between all pairs
            node_ids = list(positions.keys())
            for i, id1 in enumerate(node_ids):
                for id2 in node_ids[i+1:]:
                    dx = positions[id1][0] - positions[id2][0]
                    dy = positions[id1][1] - positions[id2][1]
                    dist = math.sqrt(dx*dx + dy*dy) + 0.01

                    force = self.repulsion / (dist * dist)
                    fx = force * dx / dist
                    fy = force * dy / dist

                    forces[id1][0] += fx
                    forces[id1][1] += fy
                    forces[id2][0] -= fx
                    forces[id2][1] -= fy

            # Attraction along edges
            for edge in edges:
                if edge.source_id in positions and edge.target_id in positions:
                    dx = positions[edge.target_id][0] - positions[edge.source_id][0]
                    dy = positions[edge.target_id][1] - positions[edge.source_id][1]
                    dist = math.sqrt(dx*dx + dy*dy) + 0.01

                    force = self.attraction * dist
                    fx = force * dx / dist
                    fy = force * dy / dist

                    forces[edge.source_id][0] += fx
                    forces[edge.source_id][1] += fy
                    forces[edge.target_id][0] -= fx
                    forces[edge.target_id][1] -= fy

            # Update positions
            for node_id in positions:
                velocities[node_id][0] = (velocities[node_id][0] + forces[node_id][0]) * self.damping
                velocities[node_id][1] = (velocities[node_id][1] + forces[node_id][1]) * self.damping
                positions[node_id][0] += velocities[node_id][0]
                positions[node_id][1] += velocities[node_id][1]

        # Normalize to positive coordinates with margin
        min_x = min(p[0] for p in positions.values())
        min_y = min(p[1] for p in positions.values())

        result_nodes = {}
        max_x = 0
        max_y = 0

        for node in nodes:
            node.x = positions[node.id][0] - min_x + 100
            node.y = positions[node.id][1] - min_y + 100
            result_nodes[node.id] = node
            max_x = max(max_x, node.x + node.width/2)
            max_y = max(max_y, node.y + node.height/2)

        return LayoutResult(
            nodes=result_nodes,
            edges=edges,
            width=max_x,
            height=max_y
        )


def auto_layout(
    nodes: List[LayoutNode],
    edges: List[LayoutEdge],
    algorithm: str = "hierarchical",
    **kwargs
) -> LayoutResult:
    """
    Automatically layout nodes and edges.

    Args:
        nodes: List of LayoutNode objects
        edges: List of LayoutEdge objects
        algorithm: "hierarchical" (default) or "force"
        **kwargs: Additional arguments passed to layout engine

    Returns:
        LayoutResult with positioned nodes
    """
    if algorithm == "hierarchical":
        engine = HierarchicalLayout(**kwargs)
    elif algorithm == "force":
        engine = ForceDirectedLayout(**kwargs)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    return engine.layout(nodes, edges)


def split_to_columns(
    result: LayoutResult,
    target_aspect_ratio: float = 1.0,
    column_gap: float = 150,
) -> Tuple[LayoutResult, Optional[Tuple[str, str, float]]]:
    """
    Split a tall layout into two columns side-by-side.

    Args:
        result: The original LayoutResult from auto_layout
        target_aspect_ratio: Target width/height ratio (default 1.0 = square)
        column_gap: Horizontal gap between columns

    Returns:
        Tuple of (new LayoutResult, connector_info) where connector_info is
        (from_node_id, to_node_id, gap_x_position) for the edge connecting the columns,
        or None if no split was needed.
    """
    if not result.layers or len(result.layers) < 4:
        # Not enough layers to split meaningfully
        return result, None

    if result.aspect_ratio >= target_aspect_ratio * 0.7:
        # Aspect ratio is acceptable, no split needed
        return result, None

    # Find the split point - approximately half the layers
    split_index = len(result.layers) // 2

    # Identify nodes in each column
    left_node_ids = set()
    for layer in result.layers[:split_index]:
        left_node_ids.update(layer)

    right_node_ids = set()
    for layer in result.layers[split_index:]:
        right_node_ids.update(layer)

    # Calculate bounds of left column
    left_min_x = float('inf')
    left_max_x = 0
    left_min_y = float('inf')
    left_max_y = 0
    for node_id in left_node_ids:
        node = result.nodes[node_id]
        left_min_x = min(left_min_x, node.x - node.width / 2)
        left_max_x = max(left_max_x, node.x + node.width / 2)
        left_min_y = min(left_min_y, node.y - node.height / 2)
        left_max_y = max(left_max_y, node.y + node.height / 2)

    # Calculate bounds of right column (before moving)
    right_min_x = float('inf')
    right_max_x = 0
    right_min_y = float('inf')
    right_max_y = 0
    for node_id in right_node_ids:
        node = result.nodes[node_id]
        right_min_x = min(right_min_x, node.x - node.width / 2)
        right_max_x = max(right_max_x, node.x + node.width / 2)
        right_min_y = min(right_min_y, node.y - node.height / 2)
        right_max_y = max(right_max_y, node.y + node.height / 2)

    # Calculate the x position of the gap (center of whitespace between columns)
    gap_x = left_max_x + column_gap / 2

    # Move right column nodes: shift right and up
    x_offset = left_max_x + column_gap - right_min_x  # Align right column's left edge
    y_offset = left_min_y - right_min_y  # Align tops of both columns

    for node_id in right_node_ids:
        node = result.nodes[node_id]
        node.x += x_offset
        node.y += y_offset

    # Recalculate right column bounds after moving
    new_right_max_x = 0
    new_right_max_y = 0
    for node_id in right_node_ids:
        node = result.nodes[node_id]
        new_right_max_x = max(new_right_max_x, node.x + node.width / 2)
        new_right_max_y = max(new_right_max_y, node.y + node.height / 2)

    # Find the connector nodes (last in left column, first in right column)
    last_left_layer = result.layers[split_index - 1]
    first_right_layer = result.layers[split_index]

    # Find the node in the last left layer that connects to the first right layer
    connector_from = None
    connector_to = None
    for edge in result.edges:
        if edge.source_id in last_left_layer and edge.target_id in first_right_layer:
            connector_from = edge.source_id
            connector_to = edge.target_id
            break

    # If no direct connection found, use the main flow nodes at boundary
    if not connector_from:
        # Find nodes that have edges crossing the boundary
        for edge in result.edges:
            if edge.source_id in left_node_ids and edge.target_id in right_node_ids:
                connector_from = edge.source_id
                connector_to = edge.target_id
                break

    # Update result metrics
    new_width = new_right_max_x
    new_height = max(left_max_y, new_right_max_y)
    new_aspect_ratio = new_width / new_height if new_height > 0 else 1.0

    new_result = LayoutResult(
        nodes=result.nodes,
        edges=result.edges,
        width=new_width,
        height=new_height,
        layers=result.layers,
        aspect_ratio=new_aspect_ratio
    )

    # Return connector info including the gap x position for routing
    connector = (connector_from, connector_to, gap_x) if connector_from and connector_to else None
    return new_result, connector


# Convenience function for simple use
def layout_flowchart(
    nodes: Dict[str, str],  # id -> label
    edges: List[Tuple[str, str, Optional[str]]],  # (from, to, label?)
    node_sizes: Optional[Dict[str, Tuple[float, float]]] = None,  # id -> (w, h)
    **kwargs
) -> Dict[str, Tuple[float, float]]:
    """
    Simple interface for laying out a flowchart.

    Args:
        nodes: Dictionary mapping node ID to label
        edges: List of (source_id, target_id, optional_label) tuples
        node_sizes: Optional dict of node ID to (width, height)
        **kwargs: Passed to HierarchicalLayout

    Returns:
        Dictionary mapping node ID to (x, y) position
    """
    layout_nodes = []
    for node_id, label in nodes.items():
        w, h = 150, 60
        if node_sizes and node_id in node_sizes:
            w, h = node_sizes[node_id]
        layout_nodes.append(LayoutNode(id=node_id, label=label, width=w, height=h))

    layout_edges = []
    for edge in edges:
        src, tgt = edge[0], edge[1]
        lbl = edge[2] if len(edge) > 2 else None
        layout_edges.append(LayoutEdge(source_id=src, target_id=tgt, label=lbl))

    result = auto_layout(layout_nodes, layout_edges, algorithm="hierarchical", **kwargs)

    return {node_id: (node.x, node.y) for node_id, node in result.nodes.items()}


if __name__ == "__main__":
    # Test the layout
    print("Testing hierarchical layout...")

    nodes = {
        "start": "Start",
        "step1": "Step 1",
        "decision": "Decision?",
        "step2a": "Step 2A",
        "step2b": "Step 2B",
        "end": "End"
    }

    edges = [
        ("start", "step1"),
        ("step1", "decision"),
        ("decision", "step2a", "Yes"),
        ("decision", "step2b", "No"),
        ("step2a", "end"),
        ("step2b", "end")
    ]

    positions = layout_flowchart(nodes, edges)

    print("\nNode positions:")
    for node_id, (x, y) in sorted(positions.items(), key=lambda p: p[1][1]):
        print(f"  {node_id}: ({x:.0f}, {y:.0f})")
