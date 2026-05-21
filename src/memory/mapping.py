import json

import numpy as np

from src.paths import resolve


def first_map(initial_event):
    objects_locations = []
    for obj in initial_event.metadata["objects"]:
        obj_info = {
            "objectType": obj["objectType"],
            "position": obj["position"],
            "objectId": obj["objectId"],
        }
        objects_locations.append(obj_info)

    out = resolve("memory/objects_locations1.json")
    with open(out, "w") as f:
        json.dump(objects_locations, f, indent=4)

    print("Saved object locations to memory/objects_locations1.json")


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

    out = resolve("memory/objects_locations.json")
    with open(out, "w") as f:
        json.dump(objects_locations, f, indent=4)

    print("Saved object locations to memory/objects_locations.json")


def second_map(event):
    objects_locations = []
    for obj in event.metadata["objects"]:
        obj_info = {
            "objectType": obj["objectType"],
            "position": obj["position"],
            "objectId": obj["objectId"],
        }
        objects_locations.append(obj_info)

    out = resolve("memory/objects_locations2.json")
    with open(out, "w") as f:
        json.dump(objects_locations, f, indent=4)

    print("Saved object locations to memory/objects_locations2.json")
