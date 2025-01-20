import math
import random
import pygame
import multiprocessing
import db


def main():
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

    grid_spacing:int=50
    G=1
    on_vector=True
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

        def update(self, particles,G):

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
    def draw_sidebar(screen, inputs, selected_input, input_active, input_buffer, paused, fps, G):
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
            pygame.draw.rect(screen, bg_color, (SIM_WIDTH + 10, 40 + i * 40, 180, 30))
            text = font.render(f"{label} {inputs[i]}", True, color)
            screen.blit(text, (SIM_WIDTH + 20, 50 + i * 40))

        # Draw G slider
        slider_x = SIM_WIDTH + 10
        slider_y = 240
        slider_width = 180
        slider_height = 10
        slider_value_x = slider_x + int((G - 0.1) / (5.0 - 0.1) * slider_width)

        pygame.draw.rect(screen, BLACK, (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.circle(screen, RED, (slider_value_x, slider_y + slider_height // 2), 8)

        g_text = font.render(f"G: {G:.2f}", True, BLACK)
        screen.blit(g_text, (SIM_WIDTH + 20, slider_y + 20))

        # Draw vector density slider
        vsslider_x = SIM_WIDTH + 10
        vsslider_y = 290
        vsslider_width = 180
        vsslider_height = 10
        vsslider_value_x = vsslider_x + int((grid_spacing - 10) / (100 - 10) * vsslider_width)

        pygame.draw.rect(screen, BLACK, (vsslider_x, vsslider_y, vsslider_width, vsslider_height))
        pygame.draw.circle(screen, RED, (vsslider_value_x, vsslider_y + vsslider_height // 2), 8)

        g_text = font.render(f"Vector Field Density: {grid_spacing}", True, BLACK)
        screen.blit(g_text, (SIM_WIDTH + 20, vsslider_y + 20))


        # Display instructions
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (SIM_WIDTH + 10, 350 + i * 20))




        # Display pause button
        pause_text = font.render("Paused" if paused else "Running", True, RED if paused else BLUE)
        screen.blit(pause_text, (SIM_WIDTH + 10, HEIGHT - 40))

        # Display FPS
        fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
        screen.blit(fps_text, (SIM_WIDTH + 120, HEIGHT - 40))

        # Draw checkbox for vector field
        checkbox_rect = pygame.Rect(SIM_WIDTH + 10, 550, 20, 20)
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2)
        if on_vector:
            pygame.draw.line(screen, BLACK, (checkbox_rect.left + 4, checkbox_rect.centery),
                             (checkbox_rect.centerx, checkbox_rect.bottom - 4), 2)
            pygame.draw.line(screen, BLACK, (checkbox_rect.centerx, checkbox_rect.bottom - 4),
                             (checkbox_rect.right - 4, checkbox_rect.top + 4), 2)


        checkbox_label = font.render("Show Vector Field", True, BLACK)
        screen.blit(checkbox_label, (checkbox_rect.right + 10, checkbox_rect.top))


    def draw_vector_field(screen, particles, G, grid_spacing):
        for x in range(0, SIM_WIDTH, int(grid_spacing)):
            for y in range(0, HEIGHT, int(grid_spacing)):
                max_force = 0
                max_force_particle = None
                force_x, force_y = 0, 0

                # Calculate the total force at this grid point from all particles
                for particle in particles:
                    dx = particle.x - x
                    dy = particle.y - y
                    distance = math.sqrt(dx ** 2 + dy ** 2)
                    if distance > 5:  # Avoid division by zero or excessive force
                        force = G * particle.mass / distance ** 2
                        angle = math.atan2(dy, dx)
                        force_x += force * math.cos(angle)
                        force_y += force * math.sin(angle)

                        # Track the particle exerting the maximum force
                        if force > max_force:
                            max_force = force
                            max_force_particle = particle

                # Normalize vector for consistent display
                magnitude = math.sqrt(force_x ** 2 + force_y ** 2)
                if magnitude > 0:
                    force_x /= magnitude
                    force_y /= magnitude

                # Scale the vector for visualization
                arrow_length = 20  # Adjust for visibility
                end_x = x + force_x * arrow_length
                end_y = y + force_y * arrow_length

                # Use the color of the particle with the maximum force exerted at this point
                vector_color = max_force_particle.color if max_force_particle else WHITE

                # Draw the arrow
                pygame.draw.line(screen, vector_color, (x, y), (end_x, end_y), 1)
                pygame.draw.circle(screen, vector_color, (int(end_x), int(end_y)), 2)


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
    g_slider_dragging = False
    vsslider_dragging = False

    # Main loop
    running = True
    clock = pygame.time.Clock()
    onetime = 0

    # Create a central "sun" and orbiting "planet"
    particles.append(Particle(470, 365, 3500, 20, YELLOW))  # Sun
    planet = Particle(470, 215, 1, 5, BLUE)
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
                    slider_rect = pygame.Rect(SIM_WIDTH + 10, 240, 180, 10)
                    vsslider_rect = pygame.Rect(SIM_WIDTH + 10, 290, 180, 10)
                    handle_x = SIM_WIDTH + 10 + int((G - 0.1) / (5.0 - 0.1) * 180)
                    handle_rect = pygame.Rect(handle_x - 8, 240 - 8, 16, 26)  # Handle area

                    vshandle_x =SIM_WIDTH + 10 + int((grid_spacing - 10) / (100 - 10) * 180)
                    vshandle_rect = pygame.Rect(vshandle_x - 8, 290 - 8, 16, 26)  # Handle area

                    checkbox_rect = pygame.Rect(SIM_WIDTH + 10, 550, 20, 20)
                    if checkbox_rect.collidepoint(event.pos):
                        on_vector = not on_vector
                    elif handle_rect.collidepoint(event.pos):
                        g_slider_dragging = True
                    elif vshandle_rect.collidepoint(event.pos):
                        vsslider_dragging = True
                    elif slider_rect.collidepoint(event.pos):
                        slider_value = (event.pos[0] - slider_rect.x) / slider_rect.width
                        G = max(0.1, min(slider_value * (5.0 - 0.1) + 0.1, 5.0))
                    elif vsslider_rect.collidepoint(event.pos):
                        vsslider_value = (event.pos[0] - vsslider_rect.x) / vsslider_rect.width
                        grid_spacing = max(10, min(vsslider_value * (100 - 10) + 10, 100))
                    elif preview_particle.is_clicked((mouse_x, mouse_y)):
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
                    g_slider_dragging = False
                    vsslider_dragging=False
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

            elif event.type == pygame.MOUSEMOTION:
                if g_slider_dragging:
                    # Adjust G based on mouse position
                    slider_rect = pygame.Rect(SIM_WIDTH + 10, 240, 180, 10)
                    relative_x = max(0, min(event.pos[0] - slider_rect.x, slider_rect.width))
                    G = 0.1 + (relative_x / slider_rect.width) * (5.0 - 0.1)
                if vsslider_dragging:
                    # Adjust vector spacing based on mouse position
                    vsslider_rect = pygame.Rect(SIM_WIDTH + 10, 290, 180, 10)
                    vsrelative_x = max(0, min(event.pos[0] - vsslider_rect.x, vsslider_rect.width))
                    grid_spacing = int(10 + (vsrelative_x / vsslider_rect.width) * (100 - 10))

        # Update particles if not paused
        if not paused:
            for particle in particles:
                particle.update(particles,G)

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

        # Draw the vector field
        if on_vector:
            draw_vector_field(screen, particles, G, grid_spacing)
        else:
            pass

        # Draw sidebar
        draw_sidebar(screen, inputs, selected_input, input_active, input_buffer, paused, fps, G)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    multiprocessing.Process(target=main).start()
