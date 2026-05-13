import pygame

from config import (
    ACCENT,
    EDGE_COLOR,
    EDGE_DONE_COLOR,
    LABEL_BG_COLOR,
    VERTEX_COLOR,
    VERTEX_DONE_COLOR,
    VERTEX_HOVER_COLOR,
    VERTEX_RADIUS,
    WHITE,
)


def draw_polygon(screen, gp, vertices, done, hovered_point):
    n = len(vertices)
    if n < 1:
        return

    label_font = pygame.font.SysFont("Arial", 13, bold=True)
    pts = [gp.pixel(gx, gy) for gx, gy in vertices]

    edge_color = EDGE_DONE_COLOR if done else EDGE_COLOR
    for i in range(n - 1):
        pygame.draw.line(screen, edge_color, pts[i], pts[i + 1], 3)
    if done and n >= 3:
        pygame.draw.line(screen, edge_color, pts[-1], pts[0], 3)

    vert_color = VERTEX_DONE_COLOR if done else VERTEX_COLOR
    for i, (px, py) in enumerate(pts):
        is_hovered = hovered_point == vertices[i]
        r = VERTEX_RADIUS + (2 if is_hovered else 0)
        c = VERTEX_HOVER_COLOR if is_hovered else vert_color
        pygame.draw.circle(screen, c, (int(px), int(py)), r)
        pygame.draw.circle(screen, WHITE, (int(px), int(py)), r, 2)

        if done or n > 1:
            idx_str = str(i)
            idx_surf = label_font.render(idx_str, True, WHITE)
            bw = idx_surf.get_width() + 8
            bh = idx_surf.get_height() + 4
            lx = int(px) - bw // 2
            ly = int(py) - VERTEX_RADIUS - bh - 4
            pygame.draw.rect(screen, LABEL_BG_COLOR if done else ACCENT, (lx, ly, bw, bh), border_radius=4)
            screen.blit(idx_surf, (lx + 4, ly + 2))
