import json
import math
from collections import deque


def read_json_file(file_path):
    """Load and return JSON file contents."""
    with open(file_path, "r") as file:
        return json.load(file)


def calculate_distance(position1, position2):
    """Euclidean distance between two 3D positions."""
    return math.sqrt(
        (position1["x"] - position2["x"]) ** 2
        + (position1["y"] - position2["y"]) ** 2
        + (position1["z"] - position2["z"]) ** 2
    )


def compare_objects_location(
    objects_locations1, objects_locations2, output_file, threshold=0.3, max_objects=100
):
    """Compare two scene snapshots; append moved objects to the STM file."""
    data1 = read_json_file(objects_locations1)
    data2 = read_json_file(objects_locations2)

    objects_data1 = {item["objectId"]: item for item in data1}
    objects_data2 = {item["objectId"]: item for item in data2}

    differences = []

    for object_id in objects_data1:
        if object_id in objects_data2:
            position1 = objects_data1[object_id]["position"]
            position2 = objects_data2[object_id]["position"]
            if calculate_distance(position1, position2) > threshold:
                differences.append(objects_data2[object_id])

    try:
        with open(output_file, "r") as file:
            output_data = json.load(file)
    except FileNotFoundError:
        output_data = []
    merged_data = output_data + differences

    unique_objects = {}

    for obj in merged_data:
        obj_id = obj["objectId"]
        unique_objects[obj_id] = obj

    if len(unique_objects) > max_objects:
        sorted_objects = sorted(
            unique_objects.items(), key=lambda x: x[1]["timestamp"], reverse=True
        )
        unique_objects = dict(sorted_objects[:max_objects])

    with open(output_file, "w") as file:
        json.dump(list(unique_objects.values()), file, indent=4)
