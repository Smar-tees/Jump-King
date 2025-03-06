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
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        # Additional attributes
        self.jumps_made = 0
        self.prev_y = y  # Only tracking vertical movement now
        self.distance_traveled = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.vx = -5
        elif keys[pygame.K_RIGHT]:
            self.vx = 5
        else:
            self.vx = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = -10
            self.on_ground = False
            self.jumps_made += 1  # increment jump counter

    def apply_physics(self, elements):
        gravity = 0.5
        self.vy += gravity

        # Move horizontally and check collisions
        self.x += self.vx
        self.check_horizontal_collision(elements)

        # Move vertically and check collisions
        self.y += self.vy
        self.check_vertical_collision(elements)

        # Zero out very small vertical velocity to avoid micro drifts
        if abs(self.vy) < 0.001:
            self.vy = 0

        # If on ground, snap Y to an integer to eliminate sub-pixel drift
        if self.on_ground:
            self.y = int(self.y)

        # Calculate change in Y and update distance traveled (only Y axis)
        dy = abs(self.y - self.prev_y)
        if not (self.on_ground and self.vy == 0):
            if dy > 0.5:  # Only add significant vertical movement
                self.distance_traveled += dy
        self.prev_y = self.y

        # If the player falls below the screen, subtract an offset from y
        if self.y > 600:
            fall_offset = 600  # adjust as needed
            self.y -= fall_offset
            self.prev_y = self.y  # Reset prev_y so no extra distance is added

    def check_horizontal_collision(self, elements):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for elem in elements:
            elem_rect = pygame.Rect(elem["x"], elem["y"], elem["width"], elem["height"])
            if player_rect.colliderect(elem_rect):
                if self.vx > 0:
                    self.x = elem_rect.left - self.width
                elif self.vx < 0:
                    self.x = elem_rect.right
                self.vx = 0
                player_rect.x = self.x

    def check_vertical_collision(self, elements):
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for elem in elements:
            elem_rect = pygame.Rect(elem["x"], elem["y"], elem["width"], elem["height"])
            if player_rect.colliderect(elem_rect):
                if self.vy > 0:
                    self.y = elem_rect.top - self.height
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = elem_rect.bottom
                self.vy = 0
                player_rect.y = self.y

    def draw(self, screen, camera_offset):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - camera_offset, self.width, self.height))

def game_loop(shared_data, level, screen, clock):
    pygame.display.set_caption("Jump King AI - Level Game")

    # Load level data
    if isinstance(level, dict) and "elements" in level:
        elements = level["elements"]
    else:
        elements = level  # fallback if load_level returns a list

    # Create the player
    player = Player(300, 500)

    # Track time elapsed (in seconds)
    time_elapsed = 0.0

    # Initialize camera offset to center on the player
    camera_offset = player.y - screen.get_height() / 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
        
        dt = clock.tick(60)  # dt in milliseconds at ~60 FPS
        time_elapsed += dt / 1000.0  # convert to seconds

        player.handle_input()
        player.apply_physics(elements)

        # Update the global in-memory player state
        shared_data.player_state = {
            "x": player.x,
            "y": player.y,
            "vx": player.vx,
            "vy": player.vy,
            "time_elapsed": round(time_elapsed, 2),
            "jumps_made": player.jumps_made,
            "distance_traveled": round(player.distance_traveled, 2)
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
        pygame.display.flip()

# if __name__ == "__main__":
#     # Start the Flask server in a background thread
#     server_thread = threading.Thread(target=run_server)
#     server_thread.daemon = True
#     server_thread.start()

#     # Start the game loop
#     game_loop()
