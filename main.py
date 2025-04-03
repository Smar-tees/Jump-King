import pygame
import random
import time
import os
import threading
import keyboard
import game
import shared_data
import level_loader
from flask import Flask, jsonify, send_from_directory
from Reward import reward


pygame.init()

def lerp(a, b, t):
    return a + (b - a) * t

# Create a Flask app instance
app = Flask(__name__)

@app.route("/")
def serve_dashboard():
    return send_from_directory(os.path.dirname(__file__), "JK/training_dashboard.html")

@app.route("/player")
def serve_player_state():
    return jsonify(shared_data.player1_state)

def run_server():
    app.run(port=5000, debug=False, use_reloader=False)

def move_king():
    """Move the king by simulating random key presses"""
    keys = ['a', 'd', 'w']  # movement keys
    if random.random() < 0.5:  # 2% chance to move each frame
        key = random.choice(keys)
        # Simulate key press and release
        keyboard.press(key)
        time.sleep(0.1)  # Hold key briefly
        keyboard.release(key)

def Agent_loop():
    while True:
        move_king()

if __name__ == "__main__":
    # Start the Flask server in a background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # king_thread = threading.Thread(target=Agent_loop)
    # king_thread.daemon = True
    # king_thread.start()

    reward_thread = threading.Thread(target=reward)
    reward_thread.daemon = True
    reward_thread.start()

    # Start the game loop
    level = level_loader.load_level()
    game.game_loop(shared_data, level)