import keyboard
import time
import pygame

class Agent:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.color = color
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
        pygame.draw.rect(screen, self.color, (self.x, self.y - camera_offset, self.width, self.height))


def run_agent():
    agent = agent(300, 500, (255, 0, 255))
    