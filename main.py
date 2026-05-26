import sys

import pygame
from pygame.event import Event

from config import (
    BUTTON_GREEN,
    BUTTON_GREEN_HOVER,
    BUTTON_RED,
    BUTTON_RED_HOVER,
    DISPLAY_FLAGS,
    FPS,
    GRID_MARGIN,
    HEIGHT,
    INPUT_ACTIVE_BORDER,
    INPUT_BORDER,
    PANEL_W,
    TITLE_COLOR,
    TUTORIAL_PANEL_H,
    UI_SCALE,
    WIDTH,
)
from geometry import Vec2, classify_polygon, ensure_ccw
from grid import GridParams, draw_grid
from panel import draw_panel
from polygon import draw_polygon
from screens import draw_input_screen
from sweep import make_monotone
from tutorial import TutorialState
from tutorial_panel import compute_tutorial_hover, draw_tutorial_panel
from ui import Button, InputBox

GRID_AREA_W = WIDTH - PANEL_W - 2 * GRID_MARGIN
GRID_AREA_H = HEIGHT - 2 * GRID_MARGIN
MAX_DIM = 200
GRID_W = WIDTH
GRID_H = HEIGHT
WINDOW_H = GRID_H + TUTORIAL_PANEL_H


def analyze(vertices):
    vecs = [Vec2(gx, gy) for gx, gy in vertices]
    ccw = ensure_ccw(vecs)
    ccw_tuples = [(v.x, v.y) for v in ccw]
    labels = classify_polygon(ccw)
    diags = make_monotone(ccw)
    return ccw_tuples, labels, diags


def _validate_dims(dx, dy):
    if dx <= 0 or dy <= 0:
        return "Please enter positive values for both dimensions."
    if dx > MAX_DIM or dy > MAX_DIM:
        return f"Maximum dimension is {MAX_DIM}."
    return None


def _make_grid_params(dx, dy):
    return GridParams(dx, dy, GRID_AREA_W, GRID_AREA_H, GRID_MARGIN, GRID_MARGIN)


def _reset_polygon():
    return [], None, None


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((GRID_W, WINDOW_H), DISPLAY_FLAGS)
        pygame.display.set_caption("Polygon Triangulation Tutorial")
        self.clock = pygame.time.Clock()

        cx = GRID_W // 2
        self.input_x = InputBox(cx - int(130 * UI_SCALE), int(280 * UI_SCALE), int(260 * UI_SCALE), int(40 * UI_SCALE), label="Width (X)", hint="e.g. 20")
        self.input_y = InputBox(cx - int(130 * UI_SCALE), int(370 * UI_SCALE), int(260 * UI_SCALE), int(40 * UI_SCALE), label="Height (Y)", hint="e.g. 20")
        self.btn_draw = Button(cx - int(80 * UI_SCALE), int(460 * UI_SCALE), int(160 * UI_SCALE), int(48 * UI_SCALE), "Draw")

        panel_w = PANEL_W
        self.panel_rect = pygame.Rect(GRID_W - panel_w, 0, panel_w, GRID_H)
        self.tutorial_panel_rect = pygame.Rect(0, GRID_H, GRID_W, TUTORIAL_PANEL_H)
        px = self.panel_rect.x + int(16 * UI_SCALE)

        self.btn_create = Button(px, int(200 * UI_SCALE), panel_w - int(32 * UI_SCALE), int(40 * UI_SCALE), "Create", BUTTON_GREEN, BUTTON_GREEN_HOVER)
        self.btn_delete = Button(px, int(250 * UI_SCALE), panel_w - int(32 * UI_SCALE), int(40 * UI_SCALE), "Delete", BUTTON_RED, BUTTON_RED_HOVER)
        self.btn_tutorial = Button(px, int(360 * UI_SCALE), panel_w - int(32 * UI_SCALE), int(40 * UI_SCALE), "Tutorial")

        self.btn_prev = Button(int(16 * UI_SCALE), GRID_H + TUTORIAL_PANEL_H - int(50 * UI_SCALE), int(88 * UI_SCALE), int(32 * UI_SCALE), "< Prev", BUTTON_GREEN, BUTTON_GREEN_HOVER)
        self.btn_next = Button(int(114 * UI_SCALE), GRID_H + TUTORIAL_PANEL_H - int(50 * UI_SCALE), int(88 * UI_SCALE), int(32 * UI_SCALE), "Next >", BUTTON_GREEN, BUTTON_GREEN_HOVER)
        self.btn_exit = Button(int(216 * UI_SCALE), GRID_H + TUTORIAL_PANEL_H - int(50 * UI_SCALE), int(88 * UI_SCALE), int(32 * UI_SCALE), "Exit")

        self.state = "input"
        self.dim_x = 0.0
        self.dim_y = 0.0
        self.gp = None
        self.error_msg = ""
        self.mode = "idle"
        self.vertices = []
        self.hovered_point = None
        self.vertex_labels = None
        self.diagonals = None
        self.tutorial = None
        self.hover_highlight = None

    def _try_start_grid(self):
        dx = self.input_x.value()
        dy = self.input_y.value()
        err = _validate_dims(dx, dy)
        if err:
            self.error_msg = err
            return
        self.dim_x = dx
        self.dim_y = dy
        self.error_msg = ""
        self.gp = _make_grid_params(dx, dy)
        self.state = "grid"
        self.mode = "idle"
        self.vertices, self.vertex_labels, self.diagonals = _reset_polygon()
        self.tutorial = None

    def _handle_start_screen(self, event: Event):
        self.input_x.handle_event(event)
        self.input_y.handle_event(event)

        if self.input_x.active and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.input_x.active = False
            self.input_x.color = INPUT_BORDER
            self.input_y.active = True
            self.input_y.color = INPUT_ACTIVE_BORDER
            return

        if self.input_y.active and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.input_y.active = False
            self.input_y.color = INPUT_BORDER
            self._try_start_grid()
            return

        if self.btn_draw.handle_event(event):
            self._try_start_grid()

    def _handle_grid_loop(self, event: Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.tutorial:
                self._exit_tutorial()
                return
            self.state = "input"
            return

        if self.tutorial:
            self._handle_tutorial(event)
            return

        if self.btn_create.handle_event(event):
            self.mode = "creating"
            self.vertices, self.vertex_labels, self.diagonals = _reset_polygon()
            self.tutorial = None
            return

        if self.btn_delete.handle_event(event):
            if self.mode == "creating" and self.vertices:
                self.vertices.pop()
            return

        if self.mode == "creating" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.panel_rect.collidepoint(event.pos):
                return
            snapped = self.gp.snap(*event.pos)
            if snapped is None:
                return
            if len(self.vertices) >= 3 and snapped == self.vertices[0]:
                self.mode = "done"
                self.vertices, self.vertex_labels, self.diagonals = analyze(self.vertices)
                self.tutorial = None
            elif snapped not in self.vertices:
                self.vertices.append(snapped)

        if self.mode == "done" and self.btn_tutorial.handle_event(event):
            self._start_tutorial()

    def _start_tutorial(self):
        self.tutorial = TutorialState.create(self.vertices)
        self.state = "grid"
        self.mode = "tutorial"

    def _exit_tutorial(self):
        self.tutorial = None
        self.mode = "done"
        self.hover_highlight = None

    def _handle_tutorial(self, event: Event):
        if self.btn_prev.handle_event(event):
            if not self.tutorial.at_start():
                self.tutorial.undo()
        if self.btn_next.handle_event(event):
            self.tutorial.advance()
        if self.btn_exit.handle_event(event):
            self._exit_tutorial()

    def _update_hover(self, mouse_pos):
        self.mouse_pos = mouse_pos
        self.hovered_point = None
        self.hover_highlight = None
        if self.mode == "creating" and not self.panel_rect.collidepoint(mouse_pos):
            snapped = self.gp.snap(*mouse_pos)
            if snapped is not None:
                self.hovered_point = snapped
        if self.mode == "tutorial" and self.tutorial:
            self.hover_highlight = compute_tutorial_hover(
                self.tutorial, mouse_pos, self.tutorial_panel_rect,
            )

    def _draw(self):
        if self.state == "input":
            draw_input_screen(self.screen, self.input_x, self.input_y, self.btn_draw, self.error_msg)
        elif self.state == "grid":
            self.screen.fill((255, 255, 255))
            draw_grid(self.screen, self.gp)

            tutorial = None
            diags = self.diagonals
            if self.mode == "tutorial" and self.tutorial:
                tutorial = self.tutorial.preview()
                diags = self.tutorial.diagonals

            draw_polygon(
                self.screen, self.gp, self.vertices,
                self.mode in ("done", "tutorial"), self.hovered_point,
                self.vertex_labels, diags,
                tutorial=tutorial,
                hover_highlight=self.hover_highlight,
            )

            title_font = pygame.font.SysFont("Arial", int(18 * UI_SCALE), bold=True)
            title = title_font.render(f"Plane {self.dim_x} x {self.dim_y}", True, TITLE_COLOR)
            self.screen.blit(title, (GRID_MARGIN, int(10 * UI_SCALE)))

            if self.mode == "tutorial" and self.tutorial:
                draw_panel(
                    self.screen, self.panel_rect, "tutorial", self.vertices,
                    self.btn_create, self.btn_delete,
                )
                draw_tutorial_panel(
                    self.screen, self.tutorial_panel_rect, self.tutorial,
                    self.btn_prev, self.btn_next, self.btn_exit,
                    hover_keys=self.hover_highlight,
                )
            else:
                draw_panel(
                    self.screen, self.panel_rect, self.mode, self.vertices,
                    self.btn_create, self.btn_delete, self.btn_tutorial,
                )

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.state == "input":
                    self._handle_start_screen(event)
                elif self.state == "grid":
                    self._handle_grid_loop(event)

            self._update_hover(mouse_pos)
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    App().run()
