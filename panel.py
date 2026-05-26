import pygame

from config import (
    DARK_GRAY,
    HINT_COLOR,
    PANEL_BG,
    PANEL_BORDER,
    TITLE_COLOR,
    UI_SCALE,
    VERTEX_DONE_COLOR,
    VERTEX_TYPE_COLORS,
    WHITE,
)
from ui import Button


def draw_panel(screen, panel_rect, mode, vertices, btn_create: Button, btn_delete: Button,
               btn_tutorial: Button = None):
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(
        screen,
        PANEL_BORDER,
        (panel_rect.x, 0),
        (panel_rect.x, panel_rect.height),
        max(1, int(2 * UI_SCALE)),
    )

    x = panel_rect.x + int(16 * UI_SCALE)
    title_font = pygame.font.SysFont("Arial", int(18 * UI_SCALE), bold=True)
    info_font = pygame.font.SysFont("Arial", int(14 * UI_SCALE))
    small_font = pygame.font.SysFont("Arial", int(13 * UI_SCALE))
    legend_font = pygame.font.SysFont("Arial", int(12 * UI_SCALE), bold=True)

    title = title_font.render("Polygon Editor", True, TITLE_COLOR)
    screen.blit(title, (x, int(20 * UI_SCALE)))

    y = int(58 * UI_SCALE)
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
    elif mode in ("done", "tutorial"):
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
        y += int(20 * UI_SCALE)

    btn_create.draw(screen, enabled=(mode not in ("creating", "tutorial")))
    btn_delete.draw(screen, enabled=(mode == "creating" and len(vertices) > 0))

    if btn_tutorial and mode != "tutorial":
        btn_tutorial.draw(screen, enabled=(mode == "done"))

    if mode == "creating" and len(vertices) >= 3:
        close_hint = small_font.render("Click 1st vertex to close", True, VERTEX_DONE_COLOR)
        screen.blit(close_hint, (x, panel_rect.bottom - int(120 * UI_SCALE)))

    if mode == "done":
        y_legend = panel_rect.bottom - int(130 * UI_SCALE)
        legend_title = small_font.render("Vertex types:", True, DARK_GRAY)
        screen.blit(legend_title, (x, y_legend))
        y_legend += int(18 * UI_SCALE)
        for name, color in VERTEX_TYPE_COLORS.items():
            pygame.draw.circle(screen, color, (x + int(8 * UI_SCALE), y_legend + int(7 * UI_SCALE)), max(1, int(6 * UI_SCALE)))
            pygame.draw.circle(
                screen,
                WHITE,
                (x + int(8 * UI_SCALE), y_legend + int(7 * UI_SCALE)),
                max(1, int(6 * UI_SCALE)),
                max(1, int(1 * UI_SCALE)),
            )
            label = legend_font.render(name.capitalize(), True, DARK_GRAY)
            screen.blit(label, (x + int(22 * UI_SCALE), y_legend))
            y_legend += int(18 * UI_SCALE)

    esc_hint = small_font.render("ESC - back to input", True, HINT_COLOR)
    screen.blit(esc_hint, (x, panel_rect.bottom - int(30 * UI_SCALE)))
