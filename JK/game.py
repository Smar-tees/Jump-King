import pygame
import json
import os
import math
import threading
from flask import Flask, jsonify, send_from_directory

pygame.init()

def lerp(a, b, t):
    return a + (b - a) * t

# Example Player class

def game_loop(shared_data, level_data):
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Jump King AI - Level Game")
    clock = pygame.time.Clock()

    # Load level data
    if isinstance(level_data, dict) and "elements" in level_data:
        elements = level_data["elements"]
    else:
        elements = level_data  # fallback if load_level returns a list

    # Create the player
    player = Player(300, 500, (0, 255, 0))
    player2 = Player(200, 100, (255, 0, 0))

    # Track time elapsed (in seconds)
    time_elapsed = 0.0

    # Initialize camera offset to center on the player
    camera_offset = player.y - screen.get_height() / 2

    running = True
    while running:
        dt = clock.tick(60)  # dt in milliseconds at ~60 FPS
        time_elapsed += dt / 1000.0  # convert to seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        player2.handle_input()
        player2.apply_physics(elements)

        player.handle_input()
        player.apply_physics(elements)

        # Update the global in-memory player state
        shared_data.player1_state = {
            "x": player.x,
            "y": player.y,
            "vx": player.vx,
            "vy": player.vy,
            "time_elapsed": round(time_elapsed, 2),
            "jumps_made": player.jumps_made,
            "distance_traveled": round(player.distance_traveled, 2)
        }

        shared_data.player2_state = {
            "x": player2.x,
            "y": player2.y,
            "vx": player2.vx,
            "vy": player2.vy,
            "time_elapsed": round(time_elapsed, 2),
            "jumps_made": player2.jumps_made,
            "distance_traveled": round(player2.distance_traveled, 2)
        }

        target_offset = player.y - screen.get_height() / 2
        camera_offset = lerp(camera_offset, target_offset, 0.1)

        screen.fill((0, 0, 0))
        for elem in elements:
            color = (255, 255, 255)
            if "type" in elem and elem["type"] == "wall":
                color = (0, 0, 255)
            pygame.draw.rect(screen, color,
                             (elem["x"], elem["y"] - camera_offset, elem["width"], elem["height"]))
        player.draw(screen, camera_offset)
        player2.draw(screen, camera_offset)
        pygame.display.flip()

    pygame.quit()

# if __name__ == "__main__":
#     # Start the Flask server in a background thread
#     server_thread = threading.Thread(target=run_server)
#     server_thread.daemon = True
#     server_thread.start()

#     # Start the game loop
#     game_loop()
