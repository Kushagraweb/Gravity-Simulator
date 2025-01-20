import pygame
import sys
import random

# Pygame setup
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PLANET_RECT_WIDTH, PLANET_RECT_HEIGHT = 100, 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACE_BLUE = (0, 0, 50)
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 28)

# Sample planets data
planets = [
    {"name": "Mercury", "x": 50, "y": 50, "velocity": 5, "color": (169, 169, 169), "radius": 20},
    {"name": "Venus", "x": 200, "y": 150, "velocity": 3, "color": (255, 223, 186), "radius": 30},
    {"name": "Earth", "x": 400, "y": 250, "velocity": 2, "color": (70, 130, 180), "radius": 25},
    {"name": "Mars", "x": 600, "y": 350, "velocity": 1, "color": (255, 99, 71), "radius": 18},
    {"name": "Jupiter", "x": 50, "y": 500, "velocity": 0.5, "color": (255, 223, 186), "radius": 50},
    {"name": "Saturn", "x": 250, "y": 550, "velocity": 0.3, "color": (210, 180, 140), "radius": 45},
    {"name": "Uranus", "x": 500, "y": 500, "velocity": 0.2, "color": (135, 206, 235), "radius": 40},
    {"name": "Neptune", "x": 650, "y": 100, "velocity": 0.1, "color": (0, 0, 255), "radius": 35}
]

# Window setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Database")

# Scroll variables
scroll_offset = 0
scroll_speed = 30


# Function to generate random stars in the background



def draw_planet(planet, surface, x, y):
    """Draw planet as a colored circle inside a rectangle."""
    pygame.draw.rect(surface, WHITE, (x, y, PLANET_RECT_WIDTH, PLANET_RECT_HEIGHT), 2)
    pygame.draw.circle(surface, planet["color"], (x + PLANET_RECT_WIDTH // 2, y + PLANET_RECT_HEIGHT // 2),
                       planet["radius"])


def draw_text(surface, text, x, y, font=FONT):
    """Draw text at (x, y)"""
    label = font.render(text, True, WHITE)
    surface.blit(label, (x, y))


def draw_planet_database():
    """Draw the planets and their info on the window."""
    global scroll_offset

    screen.fill(SPACE_BLUE)


    # Loop through planets and display their information
    for i, planet in enumerate(planets):
        # Calculate position for each planet in the list, considering scrolling
        y_pos = 20 + (i * (PLANET_RECT_HEIGHT + 20)) - scroll_offset

        # Draw planet image (circle inside a rectangle)
        draw_planet(planet, screen, 50, y_pos)

        # Draw planet name
        draw_text(screen, f"Name: {planet['name']}", 200, y_pos + 10)
        draw_text(screen, f"Pos: ({planet['x']}, {planet['y']})", 200, y_pos + 40)
        draw_text(screen, f"Vel: {planet['velocity']}", 200, y_pos + 70)

        # Draw the fixed rectangle for the planet's "picture" (color and radius)
        pygame.draw.rect(screen, WHITE, (50, y_pos, PLANET_RECT_WIDTH, PLANET_RECT_HEIGHT), 2)

    pygame.display.update()


def get_input_rect(x, y, width, height):
    return pygame.Rect(x, y, width, height)


def handle_planet_editing(planet, event, input_rect):
    """Handle mouse clicks to edit planet's attributes."""
    if input_rect.collidepoint(event.pos):
        # Toggle editable fields when clicked
        planet["name"] = input("Enter new name: ")
        planet["x"] = int(input("Enter new X position: "))
        planet["y"] = int(input("Enter new Y position: "))
        planet["velocity"] = float(input("Enter new velocity: "))
        planet["radius"] = int(input("Enter new radius: "))
        # Update color (Just randomize color for now)
        planet["color"] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def main():
    global scroll_offset

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    scroll_offset += scroll_speed  # Scroll down
                elif event.key == pygame.K_UP:
                    scroll_offset -= scroll_speed  # Scroll up
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if any planet is clicked
                for i, planet in enumerate(planets):
                    y_pos = 20 + (i * (PLANET_RECT_HEIGHT + 20)) - scroll_offset
                    input_rect = get_input_rect(50, y_pos, PLANET_RECT_WIDTH, PLANET_RECT_HEIGHT)
                    handle_planet_editing(planet, event, input_rect)

        draw_planet_database()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
