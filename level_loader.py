import json
import os

def load_level(filename="levels/level1.json"):
    if not os.path.exists(filename):
        print("Level file not found.")
        return []
    with open(filename, "r") as f:
        data = json.load(f)
        # Check for either key
        if "platforms" in data:
            return data["platforms"]
        elif "elements" in data:
            return data["elements"]
        else:
            print("Level file is missing expected keys.")
            return []
