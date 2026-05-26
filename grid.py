import pygame

from config import AXIS_COLOR, GRID_LINE, SNAP_RADIUS, UI_SCALE


class GridParams:
    def __init__(self, dim_x, dim_y, area_w, area_h, offset_x, offset_y):
        cell_w = area_w / dim_x
        cell_h = area_h / dim_y
        self.cell = min(cell_w, cell_h)
        self.grid_w = self.cell * dim_x
        self.grid_h = self.cell * dim_y
        self.origin_x = offset_x + (area_w - self.grid_w) / 2
        self.origin_y = offset_y + (area_h - self.grid_h) / 2
        self.dim_x = dim_x
        self.dim_y = dim_y

    def pixel(self, gx, gy):
        return (
            self.origin_x + gx * self.cell,
            self.origin_y + self.grid_h - gy * self.cell,
        )

    def snap(self, mx, my):
        gx = round((mx - self.origin_x) / self.cell)
        gy = round((self.origin_y + self.grid_h - my) / self.cell)
        if gx < 0 or gx > self.dim_x or gy < 0 or gy > self.dim_y:
            return None
        px, py = self.pixel(gx, gy)
        if ((px - mx) ** 2 + (py - my) ** 2) ** 0.5 > SNAP_RADIUS:
            return None
        return (gx, gy)


def _label_step(dim, max_labels):
    raw = dim / max_labels
    if raw <= 1:
        return 1
    for nice in [1, 2, 5, 10, 20, 50, 100]:
        if nice >= raw:
            return nice
    return int(raw)


def draw_grid(screen, gp):
    for i in range(int(gp.dim_x) + 1):
        x = gp.origin_x + i * gp.cell
        pygame.draw.line(screen, GRID_LINE, (x, gp.origin_y), (x, gp.origin_y + gp.grid_h), 1)

    for j in range(int(gp.dim_y) + 1):
        y = gp.origin_y + j * gp.cell
        pygame.draw.line(screen, GRID_LINE, (gp.origin_x, y), (gp.origin_x + gp.grid_w, y), 1)

    pygame.draw.line(screen, AXIS_COLOR, (gp.origin_x, gp.origin_y), (gp.origin_x, gp.origin_y + gp.grid_h), 2)
    pygame.draw.line(screen, AXIS_COLOR, (gp.origin_x, gp.origin_y + gp.grid_h), (gp.origin_x + gp.grid_w, gp.origin_y + gp.grid_h), 2)

    axis_font = pygame.font.SysFont("Arial", int(13 * UI_SCALE))

    step = max(1, _label_step(gp.dim_x, 20))
    i = 0
    while i <= gp.dim_x:
        x = gp.origin_x + i * gp.cell
        label = axis_font.render(str(int(i)) if i == int(i) else f"{i:.1f}", True, AXIS_COLOR)
        screen.blit(label, (x - label.get_width() // 2, gp.origin_y + gp.grid_h + int(6 * UI_SCALE)))
        pygame.draw.line(
            screen,
            AXIS_COLOR,
            (x, gp.origin_y + gp.grid_h),
            (x, gp.origin_y + gp.grid_h + int(5 * UI_SCALE)),
            max(1, int(2 * UI_SCALE)),
        )
        i += step

    step = max(1, _label_step(gp.dim_y, 15))
    j = 0
    while j <= gp.dim_y:
        y = gp.origin_y + gp.grid_h - j * gp.cell
        label = axis_font.render(str(int(j)) if j == int(j) else f"{j:.1f}", True, AXIS_COLOR)
        screen.blit(label, (gp.origin_x - label.get_width() - int(8 * UI_SCALE), y - label.get_height() // 2))
        pygame.draw.line(
            screen,
            AXIS_COLOR,
            (gp.origin_x - int(5 * UI_SCALE), y),
            (gp.origin_x, y),
            max(1, int(2 * UI_SCALE)),
        )
        j += step
