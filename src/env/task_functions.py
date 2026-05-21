"""Generated task functions — LLM appends new defs below the marker."""
from src.env.executor import (
    BreakObject,
    CleanObject,
    CloseObject,
    Explore,
    ExploreObject,
    GoToObject,
    OpenObject,
    PickupObject,
    PutObject,
    SliceObject,
    SwitchOff,
    SwitchOn,
)

# --- LLM-generated task functions below ---

def pick_up_mug(robot):
    # SubTask: Pick up a mug. (Skills Required: Explore, PickupObject)
    # Since the location of the mug is not provided in memory, we must explore.
    # Based on typical kitchen layouts and the provided center points, mugs are often found on CounterTop or in Cabinet/Drawer.
    # We prioritize checking CounterTop first as it's a common place for mugs.

    # 0: Explore potential locations for the Mug
    # Prioritizing CounterTop (-1.0, 0.00, -1.5) and nearby areas like StoveBurner or Drawer if not found.
    available_positions = [
        (-1.0, 0.00, -1.5),   # Center point with CounterTop
        (-0.25, 0.00, -1.5),  # Center point with CounterTop
        (-1.0, 0.00, 0.0),    # Center point with CounterTop
        (-1.0, 0.00, -1.75),  # Nearby to CounterTop
        (-1.0, 0.00, -1.25),  # Nearby to CounterTop
        (-1.0, 0.00, -1.0),   # Nearby to CounterTop
        (-1.0, 0.00, -2.0),   # Farther away
        (-1.0, 0.00, -2.5)    # Very far
    ]
    
    # 1: Find the Mug
    Explore(robot, 'Mug', available_positions)
    
    # 2: Pick up the Mug
    PickupObject(robot, 'Mug')
