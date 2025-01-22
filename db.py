import pygame
from pygame import MOUSEBUTTONDOWN

# Initialize Pygame
pygame.init()
def dbmain():
    # Set window dimensions
    width = 800
    height = 600
    screen = pygame.display.set_mode((width, height))

    # Set window title
    pygame.display.set_caption("My Pygame Window")

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
               pass

        # Clear the screen
        screen.fill((0, 0, 0))  # Black background
        pygame.draw.rect(screen, (255, 255, 0), (200, 100, 150, 150))


        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
