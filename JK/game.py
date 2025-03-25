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

    # Initialize default player position
    playerx = 300
    playery = 500
    camera_offset = 0

    # Constants for drawing
    PLAYER_WIDTH = 30
    PLAYER_HEIGHT = 30
    PLAYER_COLOR = (255, 0, 255)

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update camera
        target_offset = playery - screen.get_height() / 2
        camera_offset = lerp(camera_offset, target_offset, 0.1)

        # Draw
        screen.fill((0, 0, 0))
        
        # Draw level elements
        for elem in elements:
            color = (255, 255, 255)
            if "type" in elem and elem["type"] == "wall":
                color = (0, 0, 255)
            pygame.draw.rect(screen, color,
                           (elem["x"], elem["y"] - camera_offset, elem["width"], elem["height"]))
        
        # Draw player
        for agent_state in shared_data.agent_states.values():
            pygame.draw.rect(screen, agent_state['color'], 
                            (agent_state['x'], 
                             agent_state['y'] - camera_offset,
                             PLAYER_WIDTH, PLAYER_HEIGHT))        
        pygame.display.flip()

    pygame.quit()
