"""Long-term memory as a 3D scene graph (3DSG) per KARMA paper Sec. IV-A."""
from __future__ import annotations

import json
from typing import Any

import numpy as np

from src.paths import resolve


def get_divided_positions(controller, grid_size: float = 0.25, divisions: int = 3) -> list[tuple[float, float, float]]:
    event = controller.step("GetReachablePositions")
    reachable_positions = event.metadata["actionReturn"]

    min_x = min(pos["x"] for pos in reachable_positions)
    max_x = max(pos["x"] for pos in reachable_positions)
    min_z = min(pos["z"] for pos in reachable_positions)
    max_z = max(pos["z"] for pos in reachable_positions)

    x_interval = (max_x - min_x) / divisions
    z_interval = (max_z - min_z) / divisions

    centers: list[tuple[float, float, float]] = []
    for i in range(divisions):
        for j in range(divisions):
            center_x = min_x + (i + 0.5) * x_interval
            center_z = min_z + (j + 0.5) * z_interval
            centers.append((center_x, 0.0, center_z))
    return centers


def get_static_objects_in_regions(controller, centers, grid_size: float = 0.25) -> dict:
    regions = {center: [] for center in centers}
    for obj in controller.last_event.metadata["objects"]:
        if not obj["pickupable"]:
            obj_pos = obj["position"]
            min_distance = float("inf")
            closest_center = None
            for center in centers:
                dist = np.linalg.norm([obj_pos["x"] - center[0], obj_pos["z"] - center[2]])
                if dist < min_distance:
                    min_distance = dist
                    closest_center = center
            if closest_center is not None:
                regions[closest_center].append(obj)
    return regions


def _assign_positions_to_areas(
    reachable: list[dict[str, float]], centers: list[tuple[float, float, float]]
) -> list[int]:
    """Map each reachable point to nearest area index."""
    assignments: list[int] = []
    for pos in reachable:
        dists = [
            (center[0] - pos["x"]) ** 2 + (center[2] - pos["z"]) ** 2 for center in centers
        ]
        assignments.append(int(np.argmin(dists)))
    return assignments


def _compute_adjacency(centers: list[tuple[float, float, float]], reachable: list[dict]) -> dict[int, list[int]]:
    """Area nodes are adjacent if reachable regions share a grid neighbor."""
    if not reachable:
        return {i: [] for i in range(len(centers))}

    assignments = _assign_positions_to_areas(reachable, centers)
    grid: dict[tuple[int, int], set[int]] = {}
    for idx, pos in enumerate(reachable):
        key = (round(pos["x"] / 0.25), round(pos["z"] / 0.25))
        grid.setdefault(key, set()).add(assignments[idx])

    adjacent: dict[int, set[int]] = {i: set() for i in range(len(centers))}
    for cells in grid.values():
        for a in cells:
            adjacent[a].update(cells)
    for i in adjacent:
        adjacent[i].discard(i)
    return {i: sorted(adjacent[i]) for i in adjacent}


def build_scene_graph(controller, floor_id: int = 1, divisions: int = 3) -> dict[str, Any]:
    """Build hierarchical 3DSG: floor -> area nodes (with edges) -> static objects."""
    event = controller.step("GetReachablePositions")
    reachable = event.metadata["actionReturn"]
    centers = get_divided_positions(controller, divisions=divisions)
    regions = get_static_objects_in_regions(controller, centers)
    adjacency = _compute_adjacency(centers, reachable)

    areas: list[dict[str, Any]] = []
    for idx, center in enumerate(centers):
        objects = regions.get(center, [])
        contains = sorted({obj["objectType"] for obj in objects})
        obj_nodes = [
            {
                "objectType": obj["objectType"],
                "objectId": obj["objectId"],
                "position": obj["position"],
                "pickupable": obj.get("pickupable", False),
            }
            for obj in objects
        ]
        areas.append(
            {
                "name": f"node {idx + 1}",
                "type": "Area",
                "position": [round(center[0], 2), round(center[1], 2), round(center[2], 2)],
                "contains": contains,
                "adjacent_nodes": [f"node {j + 1}" for j in adjacency.get(idx, [])],
                "objects": obj_nodes,
            }
        )

    return {
        "floor": {
            "name": f"floor {floor_id}",
            "type": "Floor",
            "scene": controller.last_event.metadata.get("sceneName", ""),
            "areas": areas,
        }
    }


def serialize_graph_for_prompt(graph: dict[str, Any]) -> str:
    """Serialize 3DSG to LLM-readable text (paper Fig. 2 format)."""
    lines: list[str] = []
    floor = graph["floor"]
    lines.append(f"Floor: {floor['name']}, scene: {floor.get('scene', '')}")
    for area in floor["areas"]:
        pos = area["position"]
        contains = ", ".join(area["contains"]) if area["contains"] else "none"
        adjacent = ", ".join(area["adjacent_nodes"]) if area["adjacent_nodes"] else "none"
        lines.append(
            "{"
            f"name: {area['name']}, type: Area, "
            f"contains: [{contains}], "
            f"adjacent nodes: [{adjacent}], "
            f"position: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]"
            "}"
        )
    lines.append(
        "When using Explore(), rank the eight area positions by likelihood of finding the target object."
    )
    return "\n".join(lines)


def save_ltm_from_controller(controller, floor_id: int = 1, divisions: int = 3) -> str:
    """Persist 3DSG JSON and refresh planner prompt file."""
    graph = build_scene_graph(controller, floor_id=floor_id, divisions=divisions)
    json_path = resolve("memory/ltm_scene_graph.json")
    prompt_path = resolve("prompts/long_term_memory.txt")
    legacy_path = resolve("memory/longterm_memory.json")

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    # Legacy regional JSON for backward-compatible helpers
    legacy: dict[str, list] = {}
    for area in graph["floor"]["areas"]:
        key = f"({area['position'][0]:.2f}, {area['position'][1]:.2f}, {area['position'][2]:.2f})"
        legacy[key] = [{"objectType": o["objectType"], "position": o["position"]} for o in area["objects"]]
    legacy_path.write_text(json.dumps(legacy, indent=4), encoding="utf-8")

    prompt_text = serialize_graph_for_prompt(graph)
    prompt_path.write_text(prompt_text, encoding="utf-8")
    return prompt_text


def extract_regions_from_json(filename: str = "memory/longterm_memory.json") -> list[str]:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    sentences = []
    for center, objects in data.items():
        object_types = [obj["objectType"] for obj in objects]
        sentence = f"center {center} has {{{', '.join(object_types)}}}"
        sentences.append(sentence)
    return sentences
