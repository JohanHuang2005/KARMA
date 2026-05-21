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
    # Since the location of the mug is not explicitly given in memory, we must explore.
    # Mugs are typically found on CounterTop or in Cabinet/Drawer.
    # Based on provided centers, CounterTop is at (-1.0, 0.00, -1.5) and (-0.25, 0.00, -1.5).
    # We will prioritize exploring these high-probability locations first.

    # 0: SubTask: Pick up a mug
    # 1: Explore for Mug starting with likely locations (CounterTop).
    # Prioritize centers with CounterTop first: (-1.0, 0.00, -1.5) then (-0.25, 0.00, -1.5)
    available_positions = [
        (-1.0, 0.00, -1.5),      # High likelihood (CounterTop present)
        (-0.25, 0.00, -1.5),     # High likelihood (CounterTop present)
        (-1.0, 0.00, 0.0),       # Medium likelihood (Drawer/Cabinet might contain mug)
        (-2.0, 0.00, 2.0),       # Low likelihood (Fridge/GarbageCan)
        (1.25, 0.00, -1.75),     # Low likelihood (ShelvingUnit)
        (1.5, 0.00, -0.25),      # Very low (LightSwitch only)
        (1.5, 0.00, 1.0),        # Empty
        (0.5, 0.00, 1.5)         # Empty
    ]
    Explore(robot, 'Mug', available_positions)
    
    # 2: Pick up the Mug.
    PickupObject(robot, 'Mug')
