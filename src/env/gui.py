"""Tkinter GUI entry for interactive KARMA tasks."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import messagebox

from src.paths import HISTORY_DIR, LOGS_DIR, MEMORY_DIR, PROMPTS_DIR
from src.env import executor

HISTORY_FILE = HISTORY_DIR / "task_history.json"
SIMILARITY_FLAG = LOGS_DIR / "similarity_flag.json"
TASK_DESC = LOGS_DIR / "task_description.json"
STM_FILE = MEMORY_DIR / "memory3.json"

ROBOTS = [
    {
        "name": "robot1",
        "skills": [
            "GoToObject",
            "OpenObject",
            "CloseObject",
            "BreakObject",
            "SliceObject",
            "SwitchOn",
            "SwitchOff",
            "PickupObject",
            "PutObject",
            "DropHandObject",
            "ThrowObject",
            "PushObject",
            "PullObject",
        ],
    }
]

OBJECTS_LIST = [
    "AlarmClock", "AluminumFoil", "Apple", "AppleSliced", "BaseballBat", "BasketBall",
    "Bathtub", "BathtubBasin", "Bed", "Blinds", "book", "boots", "bottle", "bowl", "box",
    "Bread", "BreadSliced", "ButterKnife", "Candle", "CD", "CellPhone", "Cloth",
    "CoffeeMachine", "CreditCard", "cup", "curtains", "DeskLamp", "DishSponge", "DogBed",
    "Drawer", "Dresser", "Dumbbell", "egg", "EggCracked", "FloorLamp", "Footstool", "fork",
    "GarbageBag", "HandTowel", "HandTowelHolder", "HousePlant", "Kettle", "KeyChain",
    "Knife", "Ladle", "Laptop", "LaundryHamper", "Lettuce", "LettuceSliced", "LightSwitch",
    "Microwave", "Mirror", "Mug", "Newspaper", "Ottoman", "Painting", "Pan", "PaperTowelRoll",
    "pen", "Pencil", "PepperShaker", "Pillow", "Plate", "Plunger", "Poster", "Pot", "Potato",
    "PotatoSliced", "RemoteControl", "RoomDecor", "Safe", "SaltShaker", "ScrubBrush", "Shelf",
    "ShelvingUnit", "ShowerCurtain", "ShowerDoor", "ShowerGlass", "ShowerHead", "Sink",
    "SinkBasin", "SoapBar", "SoapBottle", "Sofa", "Spatula", "Spoon", "SprayBottle", "Statue",
    "Stool", "StoveBurner", "StoveKnob", "TableTopDecor", "TargetCircle", "TeddyBear",
    "Television", "TennisRacket", "TissueBox", "Toaster", "Toilet", "ToiletPaper",
    "ToiletPaperHanger", "Tomato", "TomatoSliced", "Towel", "TowelHolder", "TVStand",
    "VacuumCleaner", "Vase", "Watch", "WateringCan", "Window", "WineBottle",
]


def check_task_similarity(new_task: str, task_history: list, objects_list: list) -> tuple[list, bool]:
    new_task_words = set(new_task.lower().split())
    similarity_report = []
    for task in task_history:
        task_words = set(task.lower().split())
        for word in new_task_words & task_words:
            if any(obj.lower() == word for obj in objects_list):
                similarity_report.append(f"Memory: {word}")
    similarity_flag = bool(similarity_report)
    with open(SIMILARITY_FLAG, "w", encoding="utf-8") as f:
        json.dump({"similarity_flag": similarity_flag}, f)
    return similarity_report, similarity_flag


def format_memory_data(memory_data: list) -> str:
    lines = []
    for item in memory_data:
        pos = item["position"]
        lines.append(f"Object Type: {item['objectType']}")
        lines.append(f"Position: x={pos['x']}, y={pos['y']}, z={pos['z']}")
        lines.append(f"Object ID: {item['objectId']}\n")
    return "\n".join(lines)


def launch_gui() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    def load_task_history():
        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def load_short_term_memory():
        try:
            with open(STM_FILE, encoding="utf-8") as f:
                memory_text.delete("1.0", tk.END)
                memory_text.insert(tk.END, format_memory_data(json.load(f)))
        except FileNotFoundError:
            memory_text.delete("1.0", tk.END)
            memory_text.insert(tk.END, "No short-term memory found.")

    def save_task():
        task = task_entry.get().strip()
        if not task:
            messagebox.showwarning("Input Error", "Please enter a task.")
            return

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_with_time = f"{task} ({current_time})"
        content = (
            f"Please help me decompose the following tasks: {task}. "
            "Please output only the generated code."
        )
        (PROMPTS_DIR / "instruction.txt").write_text(content, encoding="utf-8")

        task_history = load_task_history()
        similarity_report, _ = check_task_similarity(task, task_history, OBJECTS_LIST)
        similarity_text.set("\n".join(similarity_report) if similarity_report else "No similar tasks found.")

        task_history.append(task_with_time)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(task_history, f, ensure_ascii=False, indent=4)
        with open(TASK_DESC, "w", encoding="utf-8") as f:
            json.dump({"task_description": task}, f, ensure_ascii=False, indent=4)

        task_listbox.insert(tk.END, task_with_time)
        messagebox.showinfo("Success", "Start the task!")
        executor.run_scripts()
        executor.parse_and_execute_task(ROBOTS[0])

    def clear_task_history():
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        task_listbox.delete(0, tk.END)
        similarity_text.set("")
        messagebox.showinfo("Success", "Task history has been cleared!")

    def exit_application():
        executor.task_queue.put(None)
        executor.task_executor_thread.join()
        messagebox.showinfo("Info", "All tasks have been executed.")
        root.destroy()

    root = tk.Tk()
    root.title("KARMA Task Input")
    root.geometry("900x600")
    large_font = ("Helvetica", 16)

    tk.Label(root, text="Enter the task for the embodied agent:", font=large_font).pack(pady=20)
    task_entry = tk.Entry(root, width=100, font=large_font)
    task_entry.pack(pady=20)
    tk.Button(root, text="Start the task", font=large_font, command=save_task).pack(pady=20)

    tk.Label(root, text="Previously executed tasks:", font=large_font).pack(pady=10)
    task_listbox = tk.Listbox(root, width=100, height=10, font=large_font)
    task_listbox.pack(pady=10)
    for task in load_task_history():
        task_listbox.insert(tk.END, task.strip())

    similarity_text = tk.StringVar()
    tk.Label(root, textvariable=similarity_text, font=large_font, fg="red").pack(pady=10)

    tk.Button(root, text="Clear Task History", font=large_font, command=clear_task_history).pack(pady=20)
    tk.Button(root, text="Exit", font=large_font, command=exit_application).pack(pady=20)

    tk.Label(root, text="Short-term Memory:", font=large_font).pack(pady=10)
    memory_text = tk.Text(root, width=100, height=10, font=large_font)
    memory_text.pack(pady=10)
    load_short_term_memory()

    root.mainloop()
