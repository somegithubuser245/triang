import sys

import pygame

from config import (
    BUTTON_GREEN,
    BUTTON_GREEN_HOVER,
    BUTTON_RED,
    BUTTON_RED_HOVER,
    FPS,
    GRID_MARGIN,
    HEIGHT,
    INPUT_BORDER,
    INPUT_ACTIVE_BORDER,
    PANEL_W,
    TITLE_COLOR,
    WHITE,
    WIDTH,
)
from grid import GridParams, draw_grid
from panel import draw_panel
from polygon import draw_polygon
from screens import draw_input_screen
from ui import Button, InputBox


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Polygon Triangulation Tutorial")
    clock = pygame.time.Clock()

    state = "input"

    cx = WIDTH // 2
    input_x = InputBox(cx - 130, 280, 260, 40, label="Width (X)", hint="e.g. 20")
    input_y = InputBox(cx - 130, 370, 260, 40, label="Height (Y)", hint="e.g. 20")
    btn_draw = Button(cx - 80, 460, 160, 48, "Draw")

    dim_x = dim_y = 0.0
    gp = None
    error_msg = ""

    panel_rect = pygame.Rect(WIDTH - PANEL_W, 0, PANEL_W, HEIGHT)
    px = panel_rect.x + 16
    btn_create = Button(px, 200, PANEL_W - 32, 40, "Create", BUTTON_GREEN, BUTTON_GREEN_HOVER)
    btn_delete = Button(px, 250, PANEL_W - 32, 40, "Delete", BUTTON_RED, BUTTON_RED_HOVER)

    mode = "idle"
    vertices = []
    hovered_point = None

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == "input":
                result_x = input_x.handle_event(event)
                result_y = input_y.handle_event(event)

                if result_x == "next":
                    input_x.active = False
                    input_x.color = INPUT_BORDER
                    input_y.active = True
                    input_y.color = INPUT_ACTIVE_BORDER

                if result_y == "next":
                    input_y.active = False
                    input_y.color = INPUT_BORDER

                if btn_draw.handle_event(event):
                    dx = input_x.value()
                    dy = input_y.value()
                    if dx <= 0 or dy <= 0:
                        error_msg = "Please enter positive values for both dimensions."
                    elif dx > 200 or dy > 200:
                        error_msg = "Maximum dimension is 200."
                    else:
                        dim_x = dx
                        dim_y = dy
                        error_msg = ""
                        gp = GridParams(dim_x, dim_y, WIDTH - PANEL_W - 2 * GRID_MARGIN, HEIGHT - 2 * GRID_MARGIN, GRID_MARGIN, GRID_MARGIN)
                        mode = "idle"
                        vertices = []
                        hovered_point = None
                        state = "grid"

                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    dx = input_x.value()
                    dy = input_y.value()
                    if dx > 0 and dy > 0 and dx <= 200 and dy <= 200:
                        dim_x = dx
                        dim_y = dy
                        error_msg = ""
                        gp = GridParams(dim_x, dim_y, WIDTH - PANEL_W - 2 * GRID_MARGIN, HEIGHT - 2 * GRID_MARGIN, GRID_MARGIN, GRID_MARGIN)
                        mode = "idle"
                        vertices = []
                        hovered_point = None
                        state = "grid"

            elif state == "grid":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "input"

                if btn_create.handle_event(event):
                    vertices = []
                    mode = "creating"
                    hovered_point = None

                if btn_delete.handle_event(event):
                    if mode == "creating" and len(vertices) > 0:
                        vertices.pop()

                if mode == "creating" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not panel_rect.collidepoint(event.pos):
                        snapped = gp.snap(*event.pos)
                        if snapped is not None:
                            if len(vertices) >= 3 and snapped == vertices[0]:
                                mode = "done"
                            else:
                                if snapped not in vertices:
                                    vertices.append(snapped)

        if state == "input":
            draw_input_screen(screen, input_x, input_y, btn_draw, error_msg)
        elif state == "grid":
            screen.fill(WHITE)
            draw_grid(screen, gp)

            if mode == "creating":
                hovered_point = None
                if not panel_rect.collidepoint(mouse_pos):
                    snapped = gp.snap(*mouse_pos)
                    if snapped is not None:
                        hovered_point = snapped

            draw_polygon(screen, gp, vertices, mode == "done", hovered_point)

            title_font = pygame.font.SysFont("Arial", 18, bold=True)
            title = title_font.render(f"Plane {dim_x} x {dim_y}", True, TITLE_COLOR)
            screen.blit(title, (GRID_MARGIN, 10))

            draw_panel(screen, panel_rect, mode, vertices, btn_create, btn_delete)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
