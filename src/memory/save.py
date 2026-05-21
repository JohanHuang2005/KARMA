import json
import math
import time

from src.memory.replacement import apply_replacement


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
    objects_locations1,
    objects_locations2,
    output_file,
    threshold=0.3,
    max_objects=100,
    policy="fifo",
    image_path=None,
):
    """Compare scene snapshots; append moved objects to STM with replacement policy."""
    data1 = read_json_file(objects_locations1)
    data2 = read_json_file(objects_locations2)

    objects_data1 = {item["objectId"]: item for item in data1}
    objects_data2 = {item["objectId"]: item for item in data2}

    differences = []
    now = time.time()

    for object_id in objects_data1:
        if object_id in objects_data2:
            position1 = objects_data1[object_id]["position"]
            position2 = objects_data2[object_id]["position"]
            if calculate_distance(position1, position2) > threshold:
                entry = dict(objects_data2[object_id])
                entry["timestamp"] = now
                if image_path:
                    entry["image"] = image_path
                differences.append(entry)

    try:
        output_data = read_json_file(output_file)
    except FileNotFoundError:
        output_data = []

    merged = apply_replacement(output_data, differences, policy=policy, max_objects=max_objects)

    with open(output_file, "w") as file:
        json.dump(merged, file, indent=4)
