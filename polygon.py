import pygame

from config import (
    ACCENT,
    DIAGONAL_COLOR,
    EDGE_COLOR,
    EDGE_DONE_COLOR,
    LABEL_BG_COLOR,
    TUTORIAL_ACTIVE_VERTEX,
    TUTORIAL_EDGE_COLOR,
    TUTORIAL_HELPER_COLOR,
    TUTORIAL_PREDECESSOR_COLOR,
    UI_SCALE,
    VERTEX_COLOR,
    VERTEX_DONE_COLOR,
    VERTEX_HOVER_COLOR,
    VERTEX_RADIUS,
    VERTEX_TYPE_COLORS,
    WHITE,
)

HOVER_VI = "vi"
HOVER_EI_PREV = "ei_prev"
HOVER_EI_CURR = "ei_curr"
HOVER_EJ = "ej"
HOVER_HELPER_EI_PREV = "helper_ei_prev"
HOVER_HELPER_EJ = "helper_ej"
HOVER_EDGE_INFO_PREV = "edge_info_prev"
HOVER_EDGE_INFO_CURR = "edge_info_curr"
HOVER_EDGE_INFO_EJ = "edge_info_ej"

HOVER_GLOW = (50, 200, 255)


def draw_polygon(screen, gp, vertices, done, hovered_point, vertex_labels=None, diagonals=None,
                 tutorial=None, hover_highlight=None):
    n = len(vertices)
    if n < 1:
        return

    idx_font = pygame.font.SysFont("Arial", int(13 * UI_SCALE), bold=True)
    type_font = pygame.font.SysFont("Arial", int(11 * UI_SCALE), bold=True)
    tag_font = pygame.font.SysFont("Arial", int(11 * UI_SCALE), bold=True)
    pts = [gp.pixel(gx, gy) for gx, gy in vertices]

    tut_edges = set()
    tut_vertex_tags = {}
    active_vertex = None

    if tutorial is not None:
        step = tutorial
        active_vertex = step.vi
        tut_edges.add(step.ei_prev)
        tut_edges.add(step.ei_curr)
        if step.predecessor_edge is not None:
            tut_edges.add(step.predecessor_edge)
        if step.helper_ei_prev is not None:
            tut_vertex_tags[step.helper_ei_prev] = ("helper(ei-1)", TUTORIAL_HELPER_COLOR)
        if step.predecessor_helper is not None:
            tut_vertex_tags[step.predecessor_helper] = ("helper(ej)", TUTORIAL_PREDECESSOR_COLOR)

    hover_edges = set()
    hover_vertices = set()
    hover_edge_labels = set()

    if hover_highlight and tutorial is not None:
        step = tutorial
        for key in hover_highlight:
            if key == HOVER_VI:
                hover_vertices.add(step.vi)
            elif key in (HOVER_EI_PREV, HOVER_EDGE_INFO_PREV):
                hover_edges.add(step.ei_prev)
                hover_vertices.add(step.ei_prev[0])
                hover_vertices.add(step.ei_prev[1])
                hover_edge_labels.add(step.ei_prev)
            elif key in (HOVER_EI_CURR, HOVER_EDGE_INFO_CURR):
                hover_edges.add(step.ei_curr)
                hover_vertices.add(step.ei_curr[0])
                hover_vertices.add(step.ei_curr[1])
                hover_edge_labels.add(step.ei_curr)
            elif key in (HOVER_EJ, HOVER_EDGE_INFO_EJ) and step.predecessor_edge is not None:
                hover_edges.add(step.predecessor_edge)
                hover_vertices.add(step.predecessor_edge[0])
                hover_vertices.add(step.predecessor_edge[1])
                hover_edge_labels.add(step.predecessor_edge)
            elif key == HOVER_HELPER_EI_PREV and step.helper_ei_prev is not None:
                hover_vertices.add(step.helper_ei_prev)
            elif key == HOVER_HELPER_EJ and step.predecessor_helper is not None:
                hover_vertices.add(step.predecessor_helper)

    edge_color = EDGE_DONE_COLOR if done else EDGE_COLOR
    for i in range(n):
        e = (i, (i + 1) % n)
        if i == n - 1 and not done:
            continue
        c = edge_color
        w = int(3 * UI_SCALE) if done else int(2 * UI_SCALE)
        if w < 1:
            w = 1
        if e in hover_edges:
            c = HOVER_GLOW
            w = max(1, int(5 * UI_SCALE))
        elif e in tut_edges:
            if tutorial and e == tutorial.predecessor_edge:
                c = TUTORIAL_PREDECESSOR_COLOR
            else:
                c = TUTORIAL_EDGE_COLOR
            w = max(1, int(3 * UI_SCALE))
        a_pt = (int(pts[i][0]), int(pts[i][1]))
        b_pt = (int(pts[(i + 1) % n][0]), int(pts[(i + 1) % n][1]))
        pygame.draw.line(screen, c, a_pt, b_pt, w)

    if done and diagonals:
        for a, b in diagonals:
            pygame.draw.line(
                screen,
                DIAGONAL_COLOR,
                (int(pts[a][0]), int(pts[a][1])),
                (int(pts[b][0]), int(pts[b][1])),
                max(1, int(2 * UI_SCALE)),
            )

    if tutorial is not None:
        step = tutorial
        edge_label_font = pygame.font.SysFont("Arial", int(11 * UI_SCALE), bold=True)
        edge_label_map = {
            step.ei_prev: ("ei-1", TUTORIAL_EDGE_COLOR),
            step.ei_curr: ("ei", TUTORIAL_EDGE_COLOR),
        }
        if step.predecessor_edge is not None:
            edge_label_map[step.predecessor_edge] = ("ej", TUTORIAL_PREDECESSOR_COLOR)

        for edge, (label, color) in edge_label_map.items():
            a_i, b_i = edge
            mx = (pts[a_i][0] + pts[b_i][0]) / 2
            my = (pts[a_i][1] + pts[b_i][1]) / 2
            is_hover = edge in hover_edges
            lbl_color = HOVER_GLOW if is_hover else color
            lbl = edge_label_font.render(label, True, lbl_color)
            lx = int(mx) - lbl.get_width() // 2
            ly = int(my) - lbl.get_height() - int(6 * UI_SCALE)
            bg = pygame.Rect(
                lx - int(3 * UI_SCALE),
                ly - int(1 * UI_SCALE),
                lbl.get_width() + int(6 * UI_SCALE),
                lbl.get_height() + int(2 * UI_SCALE),
            )
            pygame.draw.rect(screen, WHITE, bg, border_radius=max(1, int(3 * UI_SCALE)))
            pygame.draw.rect(screen, lbl_color, bg, max(1, int(1 * UI_SCALE)), border_radius=max(1, int(3 * UI_SCALE)))
            screen.blit(lbl, (lx, ly))

    for i, (px, py) in enumerate(pts):
        ipx, ipy = int(px), int(py)
        is_hovered = hovered_point == vertices[i]
        is_active = (i == active_vertex)
        is_hover_v = (i in hover_vertices)

        r = VERTEX_RADIUS
        if is_hovered:
            r += max(1, int(2 * UI_SCALE))
        if is_active:
            r += max(1, int(5 * UI_SCALE))
        if is_hover_v and not is_active:
            r += max(1, int(4 * UI_SCALE))

        if done and vertex_labels:
            type_name = vertex_labels[i]
            c = VERTEX_HOVER_COLOR if is_hovered else VERTEX_TYPE_COLORS.get(type_name, VERTEX_DONE_COLOR)
        else:
            c = VERTEX_HOVER_COLOR if is_hovered else (VERTEX_DONE_COLOR if done else VERTEX_COLOR)

        if is_active:
            c = TUTORIAL_ACTIVE_VERTEX

        pygame.draw.circle(screen, c, (ipx, ipy), r)

        border_c = WHITE
        border_w = max(1, int(2 * UI_SCALE))
        if is_hover_v:
            border_c = HOVER_GLOW
            border_w = max(1, int(3 * UI_SCALE))
        elif i in tut_vertex_tags:
            _, tag_color = tut_vertex_tags[i]
            border_c = tag_color
            border_w = max(1, int(3 * UI_SCALE))

        pygame.draw.circle(screen, border_c, (ipx, ipy), r, border_w)

        if done or n > 1:
            idx_str = str(i)
            idx_surf = idx_font.render(idx_str, True, WHITE)
            bw = idx_surf.get_width() + int(8 * UI_SCALE)
            bh = idx_surf.get_height() + int(4 * UI_SCALE)
            lx = ipx - bw // 2
            ly = ipy - r - bh - int(4 * UI_SCALE)

            badge_color = LABEL_BG_COLOR if done else ACCENT
            if done and vertex_labels:
                badge_color = VERTEX_TYPE_COLORS.get(vertex_labels[i], LABEL_BG_COLOR)

            pygame.draw.rect(screen, badge_color, (lx, ly, bw, bh), border_radius=max(1, int(4 * UI_SCALE)))
            screen.blit(idx_surf, (lx + int(4 * UI_SCALE), ly + int(2 * UI_SCALE)))

        if done and vertex_labels:
            type_name = vertex_labels[i]
            type_surf = type_font.render(type_name, True, c)
            screen.blit(type_surf, (ipx - type_surf.get_width() // 2, ipy + r + int(4 * UI_SCALE)))

        if i in tut_vertex_tags:
            tag_text, tag_color = tut_vertex_tags[i]
            tag = tag_font.render(tag_text, True, tag_color)
            tag_x = ipx - tag.get_width() // 2
            tag_y = ipy + r + int(18 * UI_SCALE)
            bg_rect = pygame.Rect(
                tag_x - int(4 * UI_SCALE),
                tag_y - int(2 * UI_SCALE),
                tag.get_width() + int(8 * UI_SCALE),
                tag.get_height() + int(4 * UI_SCALE),
            )
            pygame.draw.rect(screen, WHITE, bg_rect, border_radius=max(1, int(3 * UI_SCALE)))
            pygame.draw.rect(screen, tag_color, bg_rect, max(1, int(2 * UI_SCALE)), border_radius=max(1, int(3 * UI_SCALE)))
            screen.blit(tag, (tag_x, tag_y))
