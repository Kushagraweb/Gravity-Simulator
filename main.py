import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
WIDTH, HEIGHT = 1000, 600
SIM_WIDTH = 800  # Width of the simulation area
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Simulator with Sidebar")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Particle class
class Particle:
    def __init__(self, x, y, mass, radius, color=WHITE):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.color = color
        self.vx = 0  # Velocity in the x direction
        self.vy = 0  # Velocity in the y direction

    def update(self, particles, G=1):
        for particle in particles:
            if particle != self:
                dx = particle.x - self.x
                dy = particle.y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 5:  # Avoid extreme forces at very small distances
                    force = G * self.mass * particle.mass / distance**2
                    angle = math.atan2(dy, dx)
                    fx = force * math.cos(angle)
                    fy = force * math.sin(angle)
                    self.vx += fx / self.mass
                    self.vy += fy / self.mass

        # Update position based on velocity
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Sidebar rendering
def draw_sidebar(screen, font, inputs, selected_input, input_active, input_buffer, paused):
    pygame.draw.rect(screen, GRAY, (SIM_WIDTH, 0, WIDTH - SIM_WIDTH, HEIGHT))

    labels = ["X:", "Y:", "Mass:", "Radius:", "Velocity:"]
    for i, label in enumerate(labels):
        color = RED if i == selected_input else BLACK
        text = font.render(f"{label} {inputs[i]}", True, color)
        screen.blit(text, (SIM_WIDTH + 20, 50 + i * 40))

        if i == selected_input and input_active:
            # Draw the text area above the value
            pygame.draw.rect(screen, WHITE, (SIM_WIDTH + 140, 40 + i * 40, 80, 30))
            pygame.draw.rect(screen, BLACK, (SIM_WIDTH + 140, 40 + i * 40, 80, 30), 2)
            input_text = font.render(input_buffer, True, BLACK)
            screen.blit(input_text, (SIM_WIDTH + 145, 45 + i * 40))

    # Pause button
    pause_button = pygame.Rect(SIM_WIDTH + 20, HEIGHT - 140, 160, 40)
    pygame.draw.rect(screen, RED if paused else BLUE, pause_button)
    button_text = font.render("Pause" if not paused else "Resume", True, WHITE)
    screen.blit(button_text, (SIM_WIDTH + 50, HEIGHT - 130))

    # Add particle button
    add_button = pygame.Rect(SIM_WIDTH + 20, HEIGHT - 80, 160, 40)
    pygame.draw.rect(screen, RED, add_button)
    button_text = font.render("Add Particle", True, WHITE)
    screen.blit(button_text, (SIM_WIDTH + 30, HEIGHT - 70))

    return pause_button, add_button

# Create particles
particles = [
    Particle(SIM_WIDTH // 2, HEIGHT // 2, mass=10, radius=10, color=RED),  # Central massive object
    Particle(SIM_WIDTH // 2 + 100, HEIGHT // 2, mass=5, radius=5, color=BLUE),  # Smaller orbiting object
]

sidebar=pygame.draw.rect(screen, GRAY, (SIM_WIDTH, 0, WIDTH - SIM_WIDTH, HEIGHT))
# Sidebar inputs
inputs = [400, 300, 5, 5, 5]  # x, y, mass, radius, velocity
selected_input = 0
input_active = False
input_buffer = str(inputs[selected_input])
paused = False

# Font
font = pygame.font.SysFont(None, 24)

# Velocity direction control
setting_velocity = False
velocity_direction = (0, 0)  # Store direction as an angle in radians

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLACK, (0, 0, SIM_WIDTH, HEIGHT))  # Simulation area

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(inputs)):
                input_rect = pygame.Rect(SIM_WIDTH + 20, 50 + i * 40, 160, 30)
                if input_rect.collidepoint(event.pos):
                    selected_input = i
                    input_active = True
                    input_buffer = str(inputs[i])

            # Handle add particle button
            add_button_rect = pygame.Rect(SIM_WIDTH + 20, HEIGHT - 80, 160, 40)
            if event.type == pygame.MOUSEBUTTONDOWN and not(sidebar.collidepoint(event.pos)):
                x, y, mass, radius, velocity = inputs
                angle = math.atan2(mouse_y - y, mouse_x - x)
                vx = velocity * math.cos(angle)
                vy = velocity * math.sin(angle)
                if 0 <= x < SIM_WIDTH and 0 <= y < HEIGHT:
                    new_particle = Particle(x, y, mass, radius, color=WHITE)
                    new_particle.vx = vx
                    new_particle.vy = vy
                    particles.append(new_particle)

            # Toggle setting velocity direction on click
            if (SIM_WIDTH + 140 <= mouse_x <= SIM_WIDTH + 220 and
                50 + 4 * 40 <= mouse_y <= 50 + 4 * 40 + 30):
                setting_velocity = not setting_velocity

        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_BACKSPACE:
                    input_buffer = input_buffer[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    try:
                        inputs[selected_input] = float(input_buffer)
                        input_active = False
                    except ValueError:
                        print("Invalid input: Please enter a numeric value")
                else:
                    input_buffer += event.unicode
                    try:
                        inputs[selected_input] = float(input_buffer)
                    except ValueError:
                        pass
            elif event.key == pygame.K_SPACE:  # Pause/Resume
                paused = not paused


    # Handle velocity direction selection
    if setting_velocity:
        pygame.draw.line(screen, BLUE, (inputs[0], inputs[1]), (mouse_x, mouse_y), 6)

    # Update particles if not paused
    if not paused:
        for particle in particles:
            particle.update(particles)

    # Preview Particle
    x, y, mass, radius, velocity = inputs
    preview_angle = math.atan2(mouse_y - y, mouse_x - x) if not setting_velocity else velocity_direction
    preview_vx = velocity * math.cos(preview_angle)
    preview_vy = velocity * math.sin(preview_angle)

    preview_particle = Particle(x, y, mass, radius, color=GREEN)
    preview_particle.vx = preview_vx
    preview_particle.vy = preview_vy
    preview_particle.draw(screen)

    # Draw particles
    for particle in particles:
        particle.draw(screen)

    # Draw sidebar
    pause_button, add_button = draw_sidebar(screen, font, inputs, selected_input, input_active, input_buffer, paused)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
