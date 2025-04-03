import pygame
import time
import threading
import shared_data
from level_loader import load_level

class King:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.color = color
        self.jumps_made = 0
        self.prev_y = y
        self.distance_traveled = 0
        self.clock = pygame.time.Clock()
        self.time_elapsed = 0.0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.vx = -5
        elif keys[pygame.K_d]:
            self.vx = 5
        else:
            self.vx = 0

        if keys[pygame.K_w] and self.on_ground:
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

        # Zero out very small vertical velocity
        if abs(self.vy) < 0.001:
            self.vy = 0

        # If on ground, snap Y to integer
        if self.on_ground:
            self.y = int(self.y)

        # Calculate vertical distance traveled
        dy = abs(self.y - self.prev_y)
        if not (self.on_ground and self.vy == 0):
            if dy > 0.5:
                self.distance_traveled += dy
        self.prev_y = self.y

        # Reset if fallen too far
        if self.y > 600:
            self.y -= 600
            self.prev_y = self.y

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
        pygame.draw.rect(screen, self.color, (self.x, self.y - camera_offset, self.width, self.height))
    
    def update(self, elements):
        dt = self.clock.tick(60)
        self.time_elapsed += dt / 1000.0
        
        self.handle_input()
        self.apply_physics(elements)

        # Update shared data
        shared_data.king_state.update({
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "time_elapsed": round(self.time_elapsed, 2),
            "jumps_made": self.jumps_made,
            "distance_traveled": round(self.distance_traveled, 2)
        })