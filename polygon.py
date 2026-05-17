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
    VERTEX_TYPE_COLORS,
    WHITE,
)


def draw_polygon(screen, gp, vertices, done, hovered_point, vertex_labels=None):
    n = len(vertices)
    if n < 1:
        return

    idx_font = pygame.font.SysFont("Arial", 13, bold=True)
    type_font = pygame.font.SysFont("Arial", 11, bold=True)
    pts = [gp.pixel(gx, gy) for gx, gy in vertices]

    edge_color = EDGE_DONE_COLOR if done else EDGE_COLOR
    for i in range(n - 1):
        pygame.draw.line(screen, edge_color, pts[i], pts[i + 1], 3)
    if done and n >= 3:
        pygame.draw.line(screen, edge_color, pts[-1], pts[0], 3)

    for i, (px, py) in enumerate(pts):
        is_hovered = hovered_point == vertices[i]
        r = VERTEX_RADIUS + (2 if is_hovered else 0)

        if done and vertex_labels:
            type_name = vertex_labels[i]
            c = VERTEX_HOVER_COLOR if is_hovered else VERTEX_TYPE_COLORS.get(type_name, VERTEX_DONE_COLOR)
        else:
            c = VERTEX_HOVER_COLOR if is_hovered else (VERTEX_DONE_COLOR if done else VERTEX_COLOR)

        pygame.draw.circle(screen, c, (int(px), int(py)), r)
        pygame.draw.circle(screen, WHITE, (int(px), int(py)), r, 2)

        if done or n > 1:
            idx_str = str(i)
            idx_surf = idx_font.render(idx_str, True, WHITE)
            bw = idx_surf.get_width() + 8
            bh = idx_surf.get_height() + 4
            lx = int(px) - bw // 2
            ly = int(py) - VERTEX_RADIUS - bh - 4

            badge_color = LABEL_BG_COLOR if done else ACCENT
            if done and vertex_labels:
                badge_color = VERTEX_TYPE_COLORS.get(vertex_labels[i], LABEL_BG_COLOR)

            pygame.draw.rect(screen, badge_color, (lx, ly, bw, bh), border_radius=4)
            screen.blit(idx_surf, (lx + 4, ly + 2))

        if done and vertex_labels:
            type_name = vertex_labels[i]
            type_surf = type_font.render(type_name, True, c)
            screen.blit(type_surf, (int(px) - type_surf.get_width() // 2, int(py) + VERTEX_RADIUS + 4))
