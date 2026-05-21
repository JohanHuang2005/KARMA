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

def slice_tomato(robot):
    # 0: SubTask 1: Slice the Tomato
    # 1: Explore the Knife.
    # The knife is likely on a CounterTop or near the Stove/Prep area based on kitchen layout.
    available_positions = [
        (-0.25, 0, -1.5),  # Near stove/countertop
        (1.25, 0, -1.75),  # Shelf/Shelving unit area
        (-1.0, 0, 0),      # Drawer/CoffeeMachine area (knives often in drawers)
        (-1.0, 0, -1.5),   # Center counter
        (1.5, 0, -0.25),   # LightSwitch area (less likely for knife)
        (1.5, 0, 1.0),     # Empty area
        (1.25, 0, 1.75),   # Extrapolated shelf area if needed
        (-2.0, 0, 2.0)     # Fridge/GarbageCan area
    ]
    Explore(robot, 'Knife', available_positions)
    
    # 2: Pick up the Knife.
    PickupObject(robot, 'Knife')
    
    # 3: Explore the Tomato.
    # Tomatoes are usually found on a CounterTop or in the Fridge. Given the center points, CounterTop is most likely.
    available_positions = [
        (-0.25, 0, -1.5),  # Main counter
        (-1.0, 0, -1.5),   # Center counter
        (1.25, 0, -1.75),  # Shelf area (maybe fruit bowl?)
        (-1.0, 0, 0),      # CounterTop near CoffeeMachine
        (1.5, 0, -0.25),   # Unlikely
        (1.5, 0, 1.0),     # Empty
        (-2.0, 0, 2.0),    # Inside Fridge (if not on counter)
        (1.25, 0, 1.75)    # Extra shelf
    ]
    Explore(robot, 'Tomato', available_positions)
    
    # 4: Slice the Tomato.
    SliceObject(robot, 'Tomato')
    
    # 5: Explore the CounterTop.
    # To put the knife back, we need to find a clean CounterTop.
    available_positions = [
        (-0.25, 0, -1.5),
        (-1.0, 0, -1.5),
        (-1.0, 0, 0),
        (1.25, 0, -1.75),
        (1.5, 0, -0.25),
        (1.5, 0, 1.0),
        (-2.0, 0, 2.0),
        (1.25, 0, 1.75)
    ]
    Explore(robot, 'CounterTop', available_positions)
    
    # 6: Put the Knife back on the CounterTop.
    PutObject(robot, 'Knife', 'CounterTop')
