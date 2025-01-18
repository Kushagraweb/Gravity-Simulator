import math
import random
import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
WIDTH, HEIGHT = 1300, 800
SIM_WIDTH = 1000  # Width of the simulation area
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Simulator")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
HIGHLIGHT = (255, 255, 153)  # Highlight color for selected input

# Font
font = pygame.font.SysFont(None, 24)



# Particle class
class Particle:
    def __init__(self, x, y, mass, radius, color=None):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.color = color if color else [
            random.randint(50, 255) for _ in range(3)]
        self.vx = 0
        self.vy = 0
        self.trail = []

    def update(self, particles, G=1):
        # Apply gravitational forces
        for particle in particles:
            if particle != self:
                dx = particle.x - self.x
                dy = particle.y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance > 5:
                    force = G * self.mass * particle.mass / distance ** 2
                    angle = math.atan2(dy, dx)
                    fx = force * math.cos(angle)
                    fy = force * math.sin(angle)
                    self.vx += fx / self.mass
                    self.vy += fy / self.mass

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Check for screen wrapping
        teleported = False
        if self.x < 0:
            self.x += SIM_WIDTH
            teleported = True
        elif self.x >= SIM_WIDTH:
            self.x -= SIM_WIDTH
            teleported = True

        if self.y < 0:
            self.y += HEIGHT
            teleported = True
        elif self.y >= HEIGHT:
            self.y -= HEIGHT
            teleported = True

        # Reset trail if teleported
        if teleported:
            self.trail = []

        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 50:  # Limit trail length
            self.trail.pop(0)

    def draw(self, screen):
        # Draw the particle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # Draw the trail with transparency
        if len(self.trail) > 1:
            trail_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)  # Transparent surface
            for i in range(1, len(self.trail)):
                alpha = int(255 * (i / len(self.trail)))  # Transparency gradient
                trail_color = (*self.color, alpha)
                pygame.draw.line(
                    trail_surface,
                    trail_color,
                    (int(self.trail[i - 1][0]), int(self.trail[i - 1][1])),
                    (int(self.trail[i][0]), int(self.trail[i][1])),
                    2
                )
            screen.blit(trail_surface, (0, 0))

    def is_clicked(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        return math.sqrt(dx**2 + dy**2) <= self.radius


# Functions for drawing and handling the sidebar
def draw_sidebar(
    screen, inputs, selected_input, input_active, input_buffer, paused, fps
):
    pygame.draw.rect(screen, GRAY, (SIM_WIDTH, 0, WIDTH - SIM_WIDTH, HEIGHT))
    labels = ["X:", "Y:", "Mass:", "Radius:", "Velocity:"]
    instructions = [
        "Controls:",
        "  - Arrows: Select input",
        "  - Enter: Confirm input",
        "  - Backspace: Clear input",
        "  - Scroll: Adjust radius",
        "  - Space: Pause/Resume",
        "  - Right Click: Add particle",
        "  - Middle Click: Delete particle",
    ]

    # Draw input fields
    for i, label in enumerate(labels):
        color = RED if i == selected_input else BLACK
        bg_color = HIGHLIGHT if i == selected_input else GRAY
        pygame.draw.rect(screen, bg_color,
                         (SIM_WIDTH + 10, 40 + i * 40, 180, 30))
        text = font.render(f"{label} {inputs[i]}", True, color)
        screen.blit(text, (SIM_WIDTH + 20, 50 + i * 40))

        if i == selected_input and input_active:
            # Render text to a surface
            text_surface = font.render(
                input_buffer, True, (255, 0, 255)
            )  # Render with solid color

            # Create a new surface for transparency
            transparent_surface = pygame.Surface(
                text_surface.get_size(), pygame.SRCALPHA
            )
            transparent_surface.blit(text_surface, (0, 0))

            # Set the transparency (alpha value from 0 to 255)
            transparent_surface.set_alpha(0)

            # Blit the transparent surface onto the main screen
            screen.blit(transparent_surface,
                        (SIM_WIDTH + 20, 50 + selected_input * 40))

        # Highlight invalid input
        if i == selected_input and input_active and not is_valid_number(input_buffer):
            pygame.draw.rect(
                screen, RED, (SIM_WIDTH + 10, 40 + i * 40, 180, 30), 2)

    # Display instructions
    for i, line in enumerate(instructions):
        text = font.render(line, True, BLACK)
        screen.blit(text, (SIM_WIDTH + 10, 300 + i * 20))

    # Display pause button
    pause_text = font.render(
        "Paused" if paused else "Running", True, RED if paused else BLUE
    )
    screen.blit(pause_text, (SIM_WIDTH + 10, HEIGHT - 40))

    # Display FPS
    fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
    screen.blit(fps_text, (SIM_WIDTH + 120, HEIGHT - 40))


def is_valid_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


# Default particle settings
default_inputs = [400, 300, 5, 25, 5]  # x, y, mass, radius, velocity
inputs = default_inputs[:]

# Other state variables
selected_input: int = 0
input_active = False
input_buffer = str(inputs[selected_input])
paused = False
particles = []
dragging = False

# Main loop
running = True
clock = pygame.time.Clock()
onetime = 0

# Create a central "sun" and orbiting "planet"
particles.append(Particle(400, 300, 3500, 20, YELLOW))  # Sun
planet = Particle(400, 150, 1, 5, BLUE)
planet.vx = 5  # Give the planet an initial velocity for orbit
particles.append(planet)

while running:
    screen.fill(BLACK)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    fps = clock.get_fps()

    # Create preview particle
    x, y, mass, radius, velocity = inputs
    preview_particle = Particle(x, y, mass, radius, color=GREEN)

    # Update preview particle if dragging
    if dragging:
        inputs[0], inputs[1] = mouse_x, mouse_y
        preview_particle.x, preview_particle.y = mouse_x, mouse_y

    # Draw preview particle
    preview_particle.draw(screen)
    pygame.draw.line(
        screen, BLUE, (preview_particle.x,
                       preview_particle.y), (mouse_x, mouse_y), 2
    )

    for event in pygame.event.get():
        while onetime == 0:
            for i in range(len(inputs)):
                input_rect = pygame.Rect(SIM_WIDTH + 10, 40 + i * 40, 180, 30)
                selected_input = i
                input_active = True
                input_buffer = str(inputs[selected_input])
                print(f"Selected input {i}")  # Debug statement
                onetime = 1
                break
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if preview_particle.is_clicked((mouse_x, mouse_y)):
                    dragging = True
                for i in range(len(inputs)):
                    input_rect = pygame.Rect(
                        SIM_WIDTH + 10, 40 + i * 40, 180, 30)
                    if input_rect.collidepoint(event.pos):
                        selected_input = i
                        input_active = True
                        input_buffer = str(inputs[selected_input])
                        print(f"Selected input {i}")  # Debug statement
                        break
            elif event.button == 3:  # Right click
                angle = math.atan2(mouse_y - y, mouse_x - x)
                vx = velocity * math.cos(angle)
                vy = velocity * math.sin(angle)
                particle = Particle(x, y, mass, radius)
                particle.vx = vx
                particle.vy = vy
                particles.append(particle)
            elif event.button == 2:  # Middle click
                for particle in particles[:]:
                    if particle.is_clicked((mouse_x, mouse_y)):
                        particles.remove(particle)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected_input: int = (selected_input + 1) % len(inputs)
                input_buffer = str(inputs[selected_input])
                input_active = True
            elif event.key == pygame.K_UP:
                selected_input = (selected_input - 1) % len(inputs)
                input_buffer = str(inputs[selected_input])
                input_active = True
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif input_active:
                if event.key == pygame.K_BACKSPACE:
                    print(f"Input buffer: {input_buffer}")
                    input_buffer = input_buffer[:-1]
                    if is_valid_number(input_buffer):
                        inputs[selected_input] = float(input_buffer)
                        # Debug statement
                        print(f"Input buffer: {input_buffer}")
                    else:
                        inputs[selected_input] = 0
                elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    if is_valid_number(input_buffer):
                        if input_buffer == "":
                            inputs[selected_input] = 0
                        else:
                            inputs[selected_input] = float(input_buffer)
                    else:
                        inputs[selected_input] = 0
                        input_buffer = ""
                    input_active = False
                    print(f"Input buffer: {input_buffer}")  # Debug statement
                else:
                    input_buffer += event.unicode
                    if is_valid_number(input_buffer):
                        if input_buffer == "":
                            inputs[selected_input] = 0
                        else:
                            inputs[selected_input] = float(input_buffer)
                    else:
                        inputs[selected_input] = 0
                        input_buffer = ""
                    print(f"Input buffer: {input_buffer}")  # Debug statement
        elif event.type == pygame.MOUSEWHEEL:
            inputs[3] = max(1, min(inputs[3] + event.y, 200))

    # Update particles if not paused
    if not paused:
        for particle in particles:
            particle.update(particles)

    # Draw all particles
    for particle in particles:
        particle.draw(screen)

        # Collision detection
    for particle in particles[:]:
        for other in particles[:]:
            if particle != other:
                dx = other.x - particle.x
                dy = other.y - particle.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance <= particle.radius + other.radius:
                    if particle.mass >= other.mass:
                        particle.mass += other.mass
                        particle.radius = int(
                            math.sqrt(particle.radius ** 2 + other.radius ** 2)
                        )
                        particles.remove(other)
    # Draw sidebar
    draw_sidebar(
        screen, inputs, selected_input, input_active, input_buffer, paused, fps
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
