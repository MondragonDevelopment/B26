import sys
import random
import pygame

random.seed(7)
# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 720, 480
MAIN_BG = (33, 33, 33)
INPUT_BG = (66, 66, 66)
INPUT_BORDER_ACTIVE = (150, 150, 255)
INPUT_BORDER_INACTIVE = (120, 120, 140)
DIE_COLOR = (204, 0, 204)
TEXT_COLOR = (255, 255, 255)
HINT_COLOR = (180, 180, 180)
FONT_LARGE = pygame.font.SysFont("arial", 72, bold=True)
FONT_MEDIUM = pygame.font.SysFont("arial", 28)
FONT_SMALL = pygame.font.SysFont("arial", 20)
clock = pygame.time.Clock()
input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)

# screen display
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Dice Roller")


# Initial state
state = "INPUT"
user_input = ""
input_active = False
error_message = ""
n_sides = 1
current_value = 1
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "INPUT":
            if event.type == pygame.MOUSEBUTTONDOWN:
                input_active = input_box.collidepoint(event.pos)

            elif event.type == pygame.KEYDOWN and not input_active:
                if event.key == pygame.K_TAB:
                    input_active = True
                    
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    # Validate input
                    if user_input.isdigit() and int(user_input) >= 1:
                        n_sides = int(user_input)
                        error_message = ""
                        current_value = random.randint(1, n_sides)
                        state = "RESULT"
                    else:
                        error_message = "Please enter an integer >= 1"
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.unicode.isdigit():
                    # Max sides
                    if len(user_input) < 6:
                        user_input += event.unicode

        elif state == "RESULT":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Keep rolling same die
                    current_value = random.randint(1, n_sides)
                elif event.key == pygame.K_ESCAPE:
                    # Try another die
                    state = "INPUT"
                    user_input = ""
                    error_message = ""

    # Render
    screen.fill(MAIN_BG)

    if state == "INPUT":
        # Render every element
        instructions = FONT_MEDIUM.render("Enter number of sides:", True, TEXT_COLOR)
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 80))

        border_color = INPUT_BORDER_ACTIVE if input_active else INPUT_BORDER_INACTIVE
        pygame.draw.rect(screen, INPUT_BG, input_box, border_radius=8)
        pygame.draw.rect(screen, border_color, input_box, width=3, border_radius=8)

        sides = FONT_MEDIUM.render(user_input, True, TEXT_COLOR)
        # center input box
        screen.blit(
            sides,
            (
                input_box.centerx - sides.get_width() // 2,
                input_box.centery - sides.get_height() // 2,
            ),
        )

        if error_message:
            err = FONT_SMALL.render(error_message, True, DIE_COLOR)
            screen.blit(err, (WIDTH // 2 - err.get_width() // 2, 280))
        else:
            hint = FONT_SMALL.render("Type a number and press ENTER", True, HINT_COLOR)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 280))

    elif state == "RESULT":
        # First we draw the result box and center it to get everything
        # else nicely displayed with respect to it
        die_rect = pygame.Rect(0, 0, 150, 150)
        val = FONT_LARGE.render(str(current_value), True, TEXT_COLOR)
        
        die_rect.w = max(150, val.get_width()+15)
        die_rect.h = max(150, val.get_width()+15)
        die_rect.center = (WIDTH // 2, HEIGHT // 2)

        pygame.draw.rect(screen, DIE_COLOR, die_rect, border_radius=16)
        pygame.draw.rect(screen, TEXT_COLOR, die_rect, width=4, border_radius=16)

        screen.blit(
            val,
            (
                die_rect.centerx - val.get_width() // 2,
                die_rect.centery - val.get_height() // 2,
            ),
        )

        header = FONT_MEDIUM.render(f"d{n_sides} Die Roll", True, TEXT_COLOR)
        screen.blit(header, (WIDTH // 2 - header.get_width() // 2, die_rect.top//2))

        hint = FONT_SMALL.render("SPACE to re-roll | ESC for new die", True, HINT_COLOR)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, die_rect.top + die_rect.h + 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
