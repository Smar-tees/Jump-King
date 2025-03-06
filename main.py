import pygame
import json
import os
import math
import threading
import keyboard
from JK import game, shared_data, level_loader
from Agent import run_agent
from flask import Flask, jsonify, send_from_directory


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

if __name__ == "__main__":
    # Start the Flask server in a background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    agent_thread = threading.Thread(target=run_agent)
    agent_thread.daemon = True
    agent_thread.start()

    level = level_loader.load_level()

    # Start the game loop
    game.game_loop(shared_data, level)