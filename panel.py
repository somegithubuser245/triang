import pygame

from config import (
    DARK_GRAY,
    HEIGHT,
    HINT_COLOR,
    PANEL_BG,
    PANEL_BORDER,
    TITLE_COLOR,
    VERTEX_DONE_COLOR,
)


def draw_panel(screen, panel_rect, mode, vertices, btn_create, btn_delete):
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(screen, PANEL_BORDER, (panel_rect.x, 0), (panel_rect.x, HEIGHT), 2)

    x = panel_rect.x + 16
    title_font = pygame.font.SysFont("Arial", 18, bold=True)
    info_font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 13)

    title = title_font.render("Polygon Editor", True, TITLE_COLOR)
    screen.blit(title, (x, 20))

    y = 58
    if mode == "idle":
        lines = ["Click Create to start", "drawing a polygon.", "", "Click grid intersections", "to place vertices."]
    elif mode == "creating":
        lines = [
            "Click intersections to",
            "add vertices.",
            "",
            "Click first vertex to",
            "close the polygon.",
            "",
            f"Vertices: {len(vertices)}",
        ]
    elif mode == "done":
        lines = [
            "Polygon complete!",
            f"Vertices: {len(vertices)}",
            "",
            "Click Create to draw",
            "a new polygon.",
        ]
    else:
        lines = []

    for line in lines:
        surf = info_font.render(line, True, DARK_GRAY)
        screen.blit(surf, (x, y))
        y += 20

    btn_create.draw(screen, enabled=(mode != "creating"))
    btn_delete.draw(screen, enabled=(mode == "creating" and len(vertices) > 0))

    if mode == "creating" and len(vertices) >= 3:
        close_hint = small_font.render("Click 1st vertex to close", True, VERTEX_DONE_COLOR)
        screen.blit(close_hint, (x, panel_rect.bottom - 60))

    esc_hint = small_font.render("ESC - back to input", True, HINT_COLOR)
    screen.blit(esc_hint, (x, panel_rect.bottom - 30))
