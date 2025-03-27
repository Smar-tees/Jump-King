import pygame
from king import spawn_kings
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
    camera_offset = 0

    kings = spawn_kings(6)

    # Constants for drawing
    PLAYER_WIDTH = 30
    PLAYER_HEIGHT = 30

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update camera
        highest_player_y = float('inf')
        for king_state in shared_data.king_states.values():
            highest_player_y = min(highest_player_y, king_state['y'])

        target_offset = highest_player_y - screen.get_height() / 2
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
        for king in kings:
            king.update(elements)
        
            # Draw the king
            pygame.draw.rect(screen, king.color, (king.x, king.y - camera_offset, king.width, king.height))   
        pygame.display.flip()

    pygame.quit()
