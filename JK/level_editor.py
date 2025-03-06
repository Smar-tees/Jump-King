import pygame
import json
import os

# Constants
WIDTH, HEIGHT = 800, 600
LEFT_PANEL_WIDTH = 150
RIGHT_PANEL_WIDTH = 150
GRID_SIZE = 20
SCROLL_SPEED = 10

# Original sizes for floor and wall
FLOOR_WIDTH = 200
FLOOR_HEIGHT = 20
WALL_WIDTH = 20
WALL_HEIGHT = 200

# New platform size (a third of the floor's length, same thickness)
PLATFORM_WIDTH = 67   # Approximately 200/3
PLATFORM_HEIGHT = FLOOR_HEIGHT  # 20

# Colors
DARK_GRAY  = (50, 50, 50)   # For panels
GRAY       = (100, 100, 100)
WHITE      = (255, 255, 255)
RED        = (255, 0, 0)     # Floor (red)
BLUE       = (0, 0, 255)     # Wall (blue)
CYAN       = (0, 255, 255)   # Selected wall (cyan)
BLACK      = (0, 0, 0)
FONT_COLOR = (200, 200, 200)
PREVIEW_COLOR = (200, 200, 200, 128)  # Semi-transparent

# World boundaries for grid drawing
WORLD_MIN_Y = -2000
WORLD_MAX_Y = 2000

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Editor with Two Side Panels")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

def screen_to_game_coords(screen_x, screen_y, screen_width):
    """
    Convert raw screen coordinates into game coordinates for the playable area.
    The playable area is between LEFT_PANEL_WIDTH and screen_width - RIGHT_PANEL_WIDTH.
    Returns (None, None) if outside that area.
    """
    if screen_x < LEFT_PANEL_WIDTH or screen_x > screen_width - RIGHT_PANEL_WIDTH:
        return None, None
    return screen_x - LEFT_PANEL_WIDTH, screen_y

# UI Button Class
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        label = font.render(self.text, True, FONT_COLOR)
        surface.blit(label, (self.rect.x + 5, self.rect.y + 5))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Floor class (the original horizontal element)
class Floor:
    def __init__(self, x, y, w, h):
        # x,y stored in game coordinates
        self.x, self.y = x, y
        self.width, self.height = w, h
        self.selected = False

    def draw(self, surface, offset_y):
        color = RED if not self.selected else WHITE
        # Convert game x to screen x by adding LEFT_PANEL_WIDTH
        pygame.draw.rect(surface, color, (self.x + LEFT_PANEL_WIDTH, self.y - offset_y, self.width, self.height))
        if self.selected:
            handle_rect = pygame.Rect(self.x + LEFT_PANEL_WIDTH + self.width - 5, self.y - offset_y, 10, 10)
            pygame.draw.rect(surface, WHITE, handle_rect)

    def collides_with(self, game_x, game_y, offset_y):
        if self.x <= game_x <= self.x + self.width and (game_y + offset_y) >= self.y and (game_y + offset_y) <= self.y + self.height:
            return "move"
        if (self.x + self.width - 5 <= game_x <= self.x + self.width + 5 and
            (game_y + offset_y) >= self.y and (game_y + offset_y) <= self.y + 10):
            return "resize"
        return None

# Wall class (vertical)
class Wall:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.width, self.height = w, h
        self.selected = False

    def draw(self, surface, offset_y):
        color = BLUE if not self.selected else CYAN
        pygame.draw.rect(surface, color, (self.x + LEFT_PANEL_WIDTH, self.y - offset_y, self.width, self.height))
        if self.selected:
            handle_rect = pygame.Rect(self.x + LEFT_PANEL_WIDTH + self.width - 5, self.y - offset_y, 10, 10)
            pygame.draw.rect(surface, WHITE, handle_rect)

    def collides_with(self, game_x, game_y, offset_y):
        if self.x <= game_x <= self.x + self.width and (game_y + offset_y) >= self.y and (game_y + offset_y) <= self.y + self.height:
            return "move"
        if (self.x + self.width - 5 <= game_x <= self.x + self.width + 5 and
            (game_y + offset_y) >= self.y and (game_y + offset_y) <= self.y + 10):
            return "resize"
        return None

# PlatformSmall class (the new, smaller platform)
class PlatformSmall:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.width, self.height = w, h
        self.selected = False

    def draw(self, surface, offset_y):
        # Draw small platforms in a distinct color (lighter red)
        color = (255, 100, 100) if not self.selected else WHITE
        pygame.draw.rect(surface, color, (self.x + LEFT_PANEL_WIDTH, self.y - offset_y, self.width, self.height))
        if self.selected:
            handle_rect = pygame.Rect(self.x + LEFT_PANEL_WIDTH + self.width - 5, self.y - offset_y, 10, 10)
            pygame.draw.rect(surface, WHITE, handle_rect)

    def collides_with(self, game_x, game_y, offset_y):
        if self.x <= game_x <= self.x + self.width and (game_y + offset_y) >= self.y and (game_y + offset_y) <= self.y + self.height:
            return "move"
        if (self.x + self.width - 5 <= game_x <= self.x + self.width + 5 and
            (game_y + offset_y) >= self.y and (game_y + offset_y) <= self.y + 10):
            return "resize"
        return None

# Level Editor Class
class LevelEditor:
    def __init__(self):
        self.elements = []  # List of elements (Floor, Wall, or PlatformSmall), stored in game coordinates
        self.selected_element = None
        self.dragging = False
        self.offset_y = 0  # Vertical scroll offset
        self.preview_x = None  # In game coordinates
        self.preview_y = None
        # UI buttons for the left panel (absolute screen coordinates)
        self.save_btn = Button(10, 10, LEFT_PANEL_WIDTH - 20, 30, "Save")
        self.load_btn = Button(10, 50, LEFT_PANEL_WIDTH - 20, 30, "Load")
        self.clear_btn = Button(10, 90, LEFT_PANEL_WIDTH - 20, 30, "Clear")
        # Toggle button cycles through three modes: Floor, Wall, Platform
        self.toggle_btn = Button(10, 130, LEFT_PANEL_WIDTH - 20, 30, "Floor")
        self.modes = ["floor", "wall", "platform"]
        self.mode_index = 0
        self.current_mode = self.modes[self.mode_index]

    def update_preview(self, screen_x, screen_y, screen_width):
        coords = screen_to_game_coords(screen_x, screen_y, screen_width)
        if coords[0] is None:
            self.preview_x = None
            self.preview_y = None
        else:
            game_x, game_y = coords
            self.preview_x = (game_x // GRID_SIZE) * GRID_SIZE
            self.preview_y = ((game_y + self.offset_y) // GRID_SIZE) * GRID_SIZE

    def add_element(self):
        if self.preview_x is not None and self.preview_y is not None:
            if self.current_mode == "floor":
                self.elements.append(Floor(self.preview_x, self.preview_y, FLOOR_WIDTH, FLOOR_HEIGHT))
            elif self.current_mode == "wall":
                self.elements.append(Wall(self.preview_x, self.preview_y, WALL_WIDTH, WALL_HEIGHT))
            elif self.current_mode == "platform":
                self.elements.append(PlatformSmall(self.preview_x, self.preview_y, PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.preview_x = None
            self.preview_y = None

    def select_element(self, screen_x, screen_y, screen_width):
        coords = screen_to_game_coords(screen_x, screen_y, screen_width)
        if coords[0] is None:
            self.selected_element = None
            return
        game_x, game_y = coords
        # Check topmost first
        for elem in reversed(self.elements):
            action = elem.collides_with(game_x, game_y, self.offset_y)
            if action in ("move", "resize"):
                self.selected_element = elem
                elem.selected = True
                self.dragging = True  # For simplicity, treat both as dragging
                return
        self.selected_element = None

    def move_element(self, screen_x, screen_y, screen_width):
        if not self.selected_element or not self.dragging:
            return
        coords = screen_to_game_coords(screen_x, screen_y, screen_width)
        if coords[0] is None:
            return
        game_x, game_y = coords
        self.selected_element.x = (game_x // GRID_SIZE) * GRID_SIZE
        self.selected_element.y = ((game_y + self.offset_y) // GRID_SIZE) * GRID_SIZE

    def delete_selected(self):
        if self.selected_element in self.elements:
            self.elements.remove(self.selected_element)
        self.selected_element = None

    def clear_level(self):
        self.elements = []
        self.selected_element = None

    def save_level(self, filename="levels/level1.json"):
        data = {"elements": []}
        for e in self.elements:
            # Determine type based on class
            if isinstance(e, Floor):
                etype = "floor"
            elif isinstance(e, Wall):
                etype = "wall"
            elif isinstance(e, PlatformSmall):
                etype = "platform"
            else:
                etype = "unknown"
            # When saving, convert game_x to absolute screen coordinates by adding LEFT_PANEL_WIDTH.
            data["elements"].append({
                "type": etype,
                "x": e.x + LEFT_PANEL_WIDTH,
                "y": e.y,
                "width": e.width,
                "height": e.height
            })
        os.makedirs("levels", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved to {filename}")

    def load_level(self, filename="levels/level1.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.elements = []
                for elem in data["elements"]:
                    # When loading, subtract LEFT_PANEL_WIDTH to convert to game coordinates.
                    x = elem["x"] - LEFT_PANEL_WIDTH
                    y = elem["y"]
                    if elem["type"] == "floor":
                        self.elements.append(Floor(x, y, elem["width"], elem["height"]))
                    elif elem["type"] == "wall":
                        self.elements.append(Wall(x, y, elem["width"], elem["height"]))
                    elif elem["type"] == "platform":
                        self.elements.append(PlatformSmall(x, y, elem["width"], elem["height"]))
            print(f"Loaded from {filename}")
        except FileNotFoundError:
            print(f"No such file: {filename}")

    def toggle_mode(self):
        self.mode_index = (self.mode_index + 1) % len(self.modes)
        self.current_mode = self.modes[self.mode_index]
        # Update the toggle button text (capitalized)
        self.toggle_btn.text = self.current_mode.capitalize()

    def scroll(self, direction):
        if direction == "up":
            self.offset_y -= SCROLL_SPEED
        elif direction == "down":
            self.offset_y += SCROLL_SPEED

    def draw_elements(self, surface):
        for e in self.elements:
            e.draw(surface, self.offset_y)

# For clarity, rename the original Platform class to Floor.
Floor = Floor  # Using the Floor class directly; no aliasing needed.

editor = LevelEditor()

running = True
while running:
    screen.fill(BLACK)

    # Draw left panel
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, LEFT_PANEL_WIDTH, screen.get_height()))
    # Draw right panel
    pygame.draw.rect(screen, DARK_GRAY, (screen.get_width() - RIGHT_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, screen.get_height()))

    # Draw UI buttons in left panel
    editor.save_btn.draw(screen)
    editor.load_btn.draw(screen)
    editor.clear_btn.draw(screen)
    editor.toggle_btn.draw(screen)

    # Define playable area boundaries
    playable_left = LEFT_PANEL_WIDTH
    playable_right = screen.get_width() - RIGHT_PANEL_WIDTH

    # Draw grid in playable area
    for x in range(playable_left, playable_right, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, screen.get_height()))
    for y in range(WORLD_MIN_Y, WORLD_MAX_Y, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (playable_left, y - editor.offset_y),
                         (playable_right, y - editor.offset_y))

    # Draw existing elements (their draw methods add LEFT_PANEL_WIDTH)
    editor.draw_elements(screen)

    # Draw preview element if applicable (shift preview by LEFT_PANEL_WIDTH)
    if editor.preview_x is not None and editor.preview_y is not None and not editor.dragging:
        if editor.current_mode == "floor":
            w, h = FLOOR_WIDTH, FLOOR_HEIGHT
        elif editor.current_mode == "wall":
            w, h = WALL_WIDTH, WALL_HEIGHT
        else:  # "platform" mode
            w, h = PLATFORM_WIDTH, PLATFORM_HEIGHT
        preview_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        preview_surf.fill(PREVIEW_COLOR)
        screen.blit(preview_surf, (editor.preview_x + LEFT_PANEL_WIDTH, editor.preview_y - editor.offset_y))

    # Draw instructions in left panel
    instructions = [
        f"Mode: {editor.current_mode.capitalize()}",
        "Left click: Add/select",
        "Right click: Delete",
        "Drag: Move",
        "Up/Down: Scroll"
    ]
    y_off = 180
    for line in instructions:
        txt = font.render(line, True, FONT_COLOR)
        screen.blit(txt, (10, y_off))
        y_off += 26

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # If click in left panel
            if mx < LEFT_PANEL_WIDTH:
                if editor.save_btn.is_clicked((mx, my)):
                    editor.save_level()
                elif editor.load_btn.is_clicked((mx, my)):
                    editor.load_level()
                elif editor.clear_btn.is_clicked((mx, my)):
                    editor.clear_level()
                elif editor.toggle_btn.is_clicked((mx, my)):
                    editor.toggle_mode()
            # If click in right panel, ignore
            elif mx > screen.get_width() - RIGHT_PANEL_WIDTH:
                pass
            else:
                if event.button == 1:
                    editor.select_element(mx, my, screen.get_width())
                    if editor.selected_element is None:
                        editor.add_element()
                    else:
                        editor.dragging = True
                elif event.button == 3:
                    editor.delete_selected()
        elif event.type == pygame.MOUSEBUTTONUP:
            editor.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if editor.dragging:
                editor.move_element(event.pos[0], event.pos[1], screen.get_width())
            else:
                editor.update_preview(event.pos[0], event.pos[1], screen.get_width())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                editor.scroll("up")
            elif event.key == pygame.K_DOWN:
                editor.scroll("down")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
