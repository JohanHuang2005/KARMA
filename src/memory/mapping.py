import json

import numpy as np

from src.paths import MEMORY_DIR


def first_map(initial_event):
    # Collect objectType, position, and objectId for every scene object
    objects_locations = []
    for obj in initial_event.metadata["objects"]:
        obj_info = {
            "objectType": obj["objectType"],
            "position": obj["position"],
            "objectId": obj["objectId"],
        }
        objects_locations.append(obj_info)

    with open(str(MEMORY_DIR / "objects_locations1.json"), "w") as f:
        json.dump(objects_locations, f, indent=4)

    print("Saved object locations to objects_locations1.json")


def first_map_for_next_time(initial_event):
    objects_locations = []
    for obj in initial_event.metadata["objects"]:
        obj_info = {
            "objectType": obj["objectType"],
            "position": obj["position"],
            "objectId": obj["objectId"],
            "axisAlignedBoundingBox": obj["axisAlignedBoundingBox"],
        }
        objects_locations.append(obj_info)

    with open(str(MEMORY_DIR / "objects_locations.json"), "w") as f:
        json.dump(objects_locations, f, indent=4)

    print("Saved object locations and bounding boxes to objects_locations.json")


# Call after AI2-THOR init and an event step.
def second_map(event):
    objects_locations = []
    for obj in event.metadata["objects"]:
        obj_info = {
            "objectType": obj["objectType"],
            "position": obj["position"],
            "objectId": obj["objectId"],
        }
        objects_locations.append(obj_info)

    with open(str(MEMORY_DIR / "objects_locations2.json"), "w") as f:
        json.dump(objects_locations, f, indent=4)

    print("Saved object locations to objects_locations2.json")
