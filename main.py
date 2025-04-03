import pygame
import os
import time
import threading
import game
from shared_data import king_state
from Agent import agent
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
    return jsonify(king_state)

def run_server():
    app.run(port=5000, debug=False, use_reloader=False)

def start_agent(id):
    print('inside start_agent func')
    player = agent(id)
    while not stop_agent:
        player.pick_move()
        if king_state['vy'] == 0:
            player.update_heights(king_state)

    print('agent loop stopped')
    player.calc_reward(king_state['y'])
    player.save_pattern()

if __name__ == "__main__":
    # Start the Flask server in a background thread
    stop_agent = False

    level = level_loader.load_level()

    game_thread = threading.Thread(target=game.game_loop, args=(king_state, level))
    game_thread.daemon = True
    game_thread.start()

    king_thread = threading.Thread(target=start_agent, args=('Prof Ellis',))
    king_thread.daemon = True
    king_thread.start()
    time.sleep(5)
    stop_agent = True
    king_thread.join()

    # Here I want the code to start the agent loop, but stop it after 5 seconds, so the loop will start the thread, and join the thread after 15 seconds