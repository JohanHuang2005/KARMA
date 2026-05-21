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

def wash_apple(robot):
    GoToObject(robot, 'Apple')
    PickupObject(robot, 'Apple')
    available_positions = [
        (-1.0, 0.00, -1.5),
        (-0.25, 0.00, -1.5),
        (-2, 0.00, 2.0),
        (1.25, 0.00, -1.75),
        (1.5, 0.00, -0.25),
        (0.5, 0.00, 1.5),
        (-1, 0.00, 0.0),
        (1.5, 0.00, 1.0),
    ]
    Explore(robot, 'Sink', available_positions)
    GoToObject(robot, 'Sink')
    CleanObject(robot, 'Apple')
