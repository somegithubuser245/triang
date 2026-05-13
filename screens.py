import pygame

from config import BG, DARK_GRAY, TITLE_COLOR, WIDTH


def draw_input_screen(screen, input_x, input_y, btn_draw, error_msg):
    screen.fill(BG)
    title_font = pygame.font.SysFont("Arial", 32, bold=True)
    sub_font = pygame.font.SysFont("Arial", 16)

    title = title_font.render("Polygon Triangulation Tutorial", True, TITLE_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

    sub = sub_font.render(
        "Set the dimensions of the plane, then click Draw to begin.", True, DARK_GRAY
    )
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 170))

    input_x.draw(screen)
    input_y.draw(screen)
    btn_draw.draw(screen)

    if error_msg:
        err_font = pygame.font.SysFont("Arial", 16)
        err_surf = err_font.render(error_msg, True, (200, 50, 50))
        screen.blit(err_surf, (WIDTH // 2 - err_surf.get_width() // 2, 540))
