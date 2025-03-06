import pygame
import json
import os
import math
import threading
import keyboard
import time
from JK import game, shared_data, level_loader
from flask import Flask, jsonify, send_from_directory


pygame.init()

def lerp(a, b, t):
    return a + (b - a) * t

# Create a Flask app instance
app = Flask(__name__)

@app.route("/")
def serve_dashboard():
    return send_from_directory(os.path.dirname(__file__), "training_dashboard.html")

@app.route("/player")
def serve_player_state():
    return jsonify(shared_data.player_state)

def run_server():
    app.run(port=5000, debug=False, use_reloader=False)

def run_game(shared_data, level):
    # Initialize pygame display here
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()
    
    game.game_loop(shared_data, level, screen, clock)

if __name__ == "__main__":
    # Start the Flask server in a background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Start the game loop in a separate thread
    level = level_loader.load_level()
    game_thread = threading.Thread(target=run_game, args=(shared_data, level))
    game_thread.daemon = True
    game_thread.start()

    # Keep the main thread alive
    try:
        while True:
            # Check if any thread has crashed
            if not server_thread.is_alive() or not game_thread.is_alive():
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down...")