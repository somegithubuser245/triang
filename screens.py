import pygame

from config import BG, DARK_GRAY, TITLE_COLOR, UI_SCALE, WIDTH


def draw_input_screen(screen, input_x, input_y, btn_draw, error_msg):
    screen.fill(BG)
    title_font = pygame.font.SysFont("Arial", int(32 * UI_SCALE), bold=True)
    sub_font = pygame.font.SysFont("Arial", int(16 * UI_SCALE))

    title = title_font.render("Polygon Triangulation Tutorial", True, TITLE_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(120 * UI_SCALE)))

    sub = sub_font.render(
        "Set the dimensions of the plane, then click Draw to begin.", True, DARK_GRAY
    )
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, int(170 * UI_SCALE)))

    input_x.draw(screen)
    input_y.draw(screen)
    btn_draw.draw(screen)

    if error_msg:
        err_font = pygame.font.SysFont("Arial", int(16 * UI_SCALE))
        err_surf = err_font.render(error_msg, True, (200, 50, 50))
        screen.blit(err_surf, (WIDTH // 2 - err_surf.get_width() // 2, int(540 * UI_SCALE)))
