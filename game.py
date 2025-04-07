import pygame
from king import King

pygame.init()

def lerp(a, b, t):
    return a + (b - a) * t

def game_loop(king_state, level_data):
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Jump King AI - Level Game")
    clock = pygame.time.Clock()

    # Load level data
    if isinstance(level_data, dict) and "elements" in level_data:
        elements = level_data["elements"]
    else:
        elements = level_data  # fallback if load_level returns a list

    # Initialize camera and king
    camera_offset = 0
    king = King(king_state["x"], 
                king_state["y"], 
                king_state["color"])

    global running
    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update camera
        target_offset = king.y - screen.get_height() / 2
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
        
        # Update and draw king
        king.update(elements)
        pygame.draw.rect(screen, king.color, (king.x, king.y - camera_offset, king.width, king.height))
        
        pygame.display.flip()

    pygame.quit()
