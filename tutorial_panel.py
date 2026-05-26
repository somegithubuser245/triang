import pygame

from config import (
    BLACK,
    BUTTON_GREEN,
    DARK_GRAY,
    DIAGONAL_COLOR,
    HINT_COLOR,
    PANEL_BG,
    PANEL_BORDER,
    TITLE_COLOR,
    VERTEX_TYPE_COLORS,
    WHITE,
    TUTORIAL_CODE_BG,
    TUTORIAL_CODE_BORDER,
    TUTORIAL_EDGE_COLOR,
    TUTORIAL_HELPER_COLOR,
    TUTORIAL_PREDECESSOR_COLOR,
    TUTORIAL_ACTIVE_VERTEX,
    UI_SCALE,
)
from sweep import PSEUDOCODE_SEGMENTS

HOVER_VI = "vi"
HOVER_EI_PREV = "ei_prev"
HOVER_EI_CURR = "ei_curr"
HOVER_EJ = "ej"
HOVER_HELPER_EI_PREV = "helper_ei_prev"
HOVER_HELPER_EJ = "helper_ej"
HOVER_EDGE_INFO_PREV = "edge_info_prev"
HOVER_EDGE_INFO_CURR = "edge_info_curr"
HOVER_EDGE_INFO_EJ = "edge_info_ej"

_CODE_FONT = "Courier New"
_CODE_SIZE = int(13 * UI_SCALE)
_CODE_BOLD_SIZE = int(13 * UI_SCALE)
_INFO_SIZE = int(14 * UI_SCALE)
_HEADER_SIZE = int(16 * UI_SCALE)
_SMALL_SIZE = int(12 * UI_SCALE)

HOVER_TEXT_COLOR = (100, 230, 255)
HOVERABLE_COLOR = (220, 225, 235)
NORMAL_CODE_COLOR = (180, 185, 195)
ACTIVE_MARKER_COLOR = (80, 200, 120)

_CODE_X_PAD = int(12 * UI_SCALE)
_HEADER_Y_OFFSET = int(42 * UI_SCALE)
_EDGE_INFO_Y_OFFSET = int(68 * UI_SCALE)
_VERTEX_HEADER_HOVER_H = int(26 * UI_SCALE)
_EDGE_HEADER_HOVER_H = int(22 * UI_SCALE)
_CODE_Y_OFFSET = int(114 * UI_SCALE)
_LINE_H = int(22 * UI_SCALE)


def compute_tutorial_hover(tut_state, mouse_pos, panel_rect):
    if not mouse_pos:
        return None
    step = tut_state.preview()
    if step is None:
        return None

    header_rect = pygame.Rect(
        panel_rect.x + int(16 * UI_SCALE),
        panel_rect.y + _HEADER_Y_OFFSET,
        int(400 * UI_SCALE),
        _VERTEX_HEADER_HOVER_H,
    )
    if header_rect.collidepoint(mouse_pos):
        return {HOVER_VI}

    segments = PSEUDOCODE_SEGMENTS.get(step.pseudocode_key, [])
    code_x = panel_rect.x + int(16 * UI_SCALE) + _CODE_X_PAD
    code_y = panel_rect.y + _CODE_Y_OFFSET

    font = pygame.font.SysFont(_CODE_FONT, _CODE_SIZE)

    for line_segments in segments:
        cx = code_x
        for text, hover_key in line_segments:
            if hover_key is None:
                tw, _ = font.size(text)
                cx += tw
                continue
            tw, _ = font.size(text)
            seg_rect = pygame.Rect(cx, code_y, tw, _LINE_H)
            if seg_rect.collidepoint(mouse_pos):
                return {hover_key}
            cx += tw
        code_y += _LINE_H

    edge_info_y = panel_rect.y + _EDGE_INFO_Y_OFFSET
    edge_info_x = panel_rect.x + int(16 * UI_SCALE)
    small_font = pygame.font.SysFont("Arial", _SMALL_SIZE)

    ei_prev_str = f"ei-1 = e({step.ei_prev[0]},{step.ei_prev[1]})"
    tw1, _ = small_font.size(ei_prev_str + "   ")
    r1 = pygame.Rect(edge_info_x, edge_info_y, tw1, _EDGE_HEADER_HOVER_H)
    if r1.collidepoint(mouse_pos):
        return {HOVER_EDGE_INFO_PREV}

    ei_curr_str = f"ei = e({step.ei_curr[0]},{step.ei_curr[1]})"
    tw2, _ = small_font.size(ei_curr_str + "   ")
    r2 = pygame.Rect(edge_info_x + tw1, edge_info_y, tw2, _EDGE_HEADER_HOVER_H)
    if r2.collidepoint(mouse_pos):
        return {HOVER_EDGE_INFO_CURR}

    if step.predecessor_edge is not None:
        ej_str = f"ej = e({step.predecessor_edge[0]},{step.predecessor_edge[1]})"
        r3 = pygame.Rect(
            edge_info_x + tw1 + tw2,
            edge_info_y,
            len(ej_str) * int(8 * UI_SCALE) + int(10 * UI_SCALE),
            _EDGE_HEADER_HOVER_H,
        )
        if r3.collidepoint(mouse_pos):
            return {HOVER_EDGE_INFO_EJ}

    return None
    step = tut_state.preview()
    if step is None:
        return None

    header_rect = pygame.Rect(
        panel_rect.x + int(16 * UI_SCALE),
        panel_rect.y + _HEADER_Y_OFFSET,
        int(400 * UI_SCALE),
        int(26 * UI_SCALE),
    )
    if header_rect.collidepoint(mouse_pos):
        return {HOVER_VI}

    segments = PSEUDOCODE_SEGMENTS.get(step.pseudocode_key, [])
    code_x = panel_rect.x + int(16 * UI_SCALE) + _CODE_X_PAD
    code_y = panel_rect.y + _CODE_Y_OFFSET

    font = pygame.font.SysFont(_CODE_FONT, _CODE_SIZE)

    for line_segments in segments:
        cx = code_x
        for text, hover_key in line_segments:
            if hover_key is None:
                tw, _ = font.size(text)
                cx += tw
                continue
            tw, _ = font.size(text)
            seg_rect = pygame.Rect(cx, code_y, tw, _LINE_H)
            if seg_rect.collidepoint(mouse_pos):
                return {hover_key}
            cx += tw
        code_y += _LINE_H

    return None


def draw_tutorial_panel(screen, panel_rect, tut_state, btn_prev, btn_next, btn_exit,
                        hover_keys=None):
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(screen, PANEL_BORDER, (0, panel_rect.y), (panel_rect.width, panel_rect.y), 2)

    x = int(16 * UI_SCALE)
    left_w = (panel_rect.width - int(64 * UI_SCALE)) // 2
    right_col_x = x + left_w + int(32 * UI_SCALE)

    header_font = pygame.font.SysFont(_CODE_FONT, _HEADER_SIZE, bold=True)
    info_font = pygame.font.SysFont("Arial", _INFO_SIZE)
    info_font_bold = pygame.font.SysFont("Arial", _INFO_SIZE, bold=True)
    small_font = pygame.font.SysFont("Arial", _SMALL_SIZE)
    code_font = pygame.font.SysFont(_CODE_FONT, _CODE_SIZE)
    code_bold = pygame.font.SysFont(_CODE_FONT, _CODE_BOLD_SIZE, bold=True)

    y = panel_rect.y + int(12 * UI_SCALE)
    title = header_font.render("MAKE MONOTONE - Step by Step", True, TITLE_COLOR)
    screen.blit(title, (x, y))
    y += int(30 * UI_SCALE)

    step = tut_state.preview()
    if step is None:
        done_font = pygame.font.SysFont("Arial", int(20 * UI_SCALE), bold=True)
        done_surf = done_font.render("Algorithm complete!", True, BUTTON_GREEN)
        screen.blit(done_surf, (x + int(20 * UI_SCALE), y + int(20 * UI_SCALE)))
        btn_exit.draw(screen)
        return

    vtype_color = VERTEX_TYPE_COLORS.get(step.vtype, DARK_GRAY)
    vertex_label_str = f"Current vertex:  v{step.vi}  -  {step.vtype.upper()}"

    vertex_label_surf = info_font_bold.render(vertex_label_str, True, vtype_color)
    vertex_label_rect = vertex_label_surf.get_rect(topleft=(x, y))
    screen.blit(vertex_label_surf, vertex_label_rect)

    is_vertex_header_hovered = hover_keys and HOVER_VI in hover_keys
    if is_vertex_header_hovered:
        highlight_surf = pygame.Surface(vertex_label_rect.size, pygame.SRCALPHA)
        highlight_surf.fill((*vtype_color, 50))
        screen.blit(highlight_surf, vertex_label_rect)
        screen.blit(vertex_label_surf, vertex_label_rect)
    y += int(26 * UI_SCALE)

    edge_info_y = y
    ei_prev_str = f"ei-1 = e({step.ei_prev[0]},{step.ei_prev[1]})"
    ei_curr_str = f"ei = e({step.ei_curr[0]},{step.ei_curr[1]})"

    ei_prev_surf = small_font.render(ei_prev_str, True, TUTORIAL_EDGE_COLOR)
    screen.blit(ei_prev_surf, (x, edge_info_y))
    prev_w = ei_prev_surf.get_width() + int(20 * UI_SCALE)

    ei_curr_surf = small_font.render(ei_curr_str, True, TUTORIAL_EDGE_COLOR)
    screen.blit(ei_curr_surf, (x + prev_w, edge_info_y))
    curr_w = ei_curr_surf.get_width() + int(20 * UI_SCALE)

    if step.predecessor_edge is not None:
        ej_str = f"ej = e({step.predecessor_edge[0]},{step.predecessor_edge[1]})"
        ej_surf = small_font.render(ej_str, True, TUTORIAL_PREDECESSOR_COLOR)
        screen.blit(ej_surf, (x + prev_w + curr_w, edge_info_y))

    for key, bx, bw in [
        (HOVER_EDGE_INFO_PREV, x, ei_prev_surf.get_width() + 12),
        (HOVER_EDGE_INFO_CURR, x + prev_w, ei_curr_surf.get_width() + 12),
    ]:
        if hover_keys and key in hover_keys:
            hr = pygame.Rect(bx, edge_info_y, bw, _EDGE_HEADER_HOVER_H)
            hs = pygame.Surface(hr.size, pygame.SRCALPHA)
            hs.fill((100, 180, 255, 50))
            screen.blit(hs, hr)
    if step.predecessor_edge is not None and hover_keys and HOVER_EDGE_INFO_EJ in hover_keys:
        ej_surf2 = small_font.render(ej_str, True, TUTORIAL_PREDECESSOR_COLOR)
        hr = pygame.Rect(x + prev_w + curr_w, edge_info_y, ej_surf2.get_width() + 12, _EDGE_HEADER_HOVER_H)
        hs = pygame.Surface(hr.size, pygame.SRCALPHA)
        hs.fill((160, 120, 255, 50))
        screen.blit(hs, hr)

    y += int(22 * UI_SCALE)

    progress = small_font.render(
        f"Step {tut_state.step_number} / {tut_state.total_steps}", True, HINT_COLOR
    )
    screen.blit(progress, (x, y))
    y += int(24 * UI_SCALE)

    segments = PSEUDOCODE_SEGMENTS.get(step.pseudocode_key, [])
    active_lines = set(step.active_lines)
    code_x = x + _CODE_X_PAD

    code_block_h = len(segments) * _LINE_H + 12
    pygame.draw.rect(
        screen,
        TUTORIAL_CODE_BG,
        (x - int(6 * UI_SCALE), y - int(4 * UI_SCALE), left_w + int(12 * UI_SCALE), code_block_h),
        border_radius=max(1, int(5 * UI_SCALE)),
    )
    pygame.draw.rect(
        screen,
        TUTORIAL_CODE_BORDER,
        (x - int(6 * UI_SCALE), y - int(4 * UI_SCALE), left_w + int(12 * UI_SCALE), code_block_h),
        max(1, int(1 * UI_SCALE)),
        border_radius=max(1, int(5 * UI_SCALE)),
    )

    for line_idx, line_segments in enumerate(segments):
        ly = y + line_idx * _LINE_H
        is_active = line_idx in active_lines

        if is_active:
            pygame.draw.rect(
                screen,
                ACTIVE_MARKER_COLOR,
                (x - int(2 * UI_SCALE), ly + int(4 * UI_SCALE), max(1, int(3 * UI_SCALE)), _LINE_H - int(8 * UI_SCALE)),
                border_radius=max(1, int(1 * UI_SCALE)),
            )

        cx = code_x
        for text, hover_key in line_segments:
            is_hovered = hover_keys and hover_key in hover_keys

            if is_hovered:
                color = HOVER_TEXT_COLOR
                fnt = code_bold
            elif hover_key is not None:
                color = HOVERABLE_COLOR
                fnt = code_font
            else:
                color = NORMAL_CODE_COLOR
                fnt = code_font

            surf = fnt.render(text, True, color)
            screen.blit(surf, (cx, ly + int(1 * UI_SCALE)))
            cx += surf.get_width()

    right_y = panel_rect.y + int(12 * UI_SCALE)
    tree_header = info_font_bold.render("Status Tree (left to right):", True, DARK_GRAY)
    screen.blit(tree_header, (right_col_x, right_y))
    right_y += int(22 * UI_SCALE)

    tree = step.tree_before
    if not tree:
        empty = small_font.render("(empty)", True, HINT_COLOR)
        screen.blit(empty, (right_col_x + int(8 * UI_SCALE), right_y))
        right_y += int(18 * UI_SCALE)
    else:
        for edge, helper in tree:
            a, b = edge
            h_str = f"h=v{helper}" if helper is not None else "h=None"
            entry_str = f"e({a},{b})  {h_str}"
            is_ej_hover = (hover_keys and HOVER_EJ in hover_keys
                           and step.predecessor_edge is not None
                           and edge == step.predecessor_edge)
            if is_ej_hover:
                surf = code_bold.render(entry_str, True, HOVER_TEXT_COLOR)
            else:
                surf = code_font.render(entry_str, True, BLACK)
            screen.blit(surf, (right_col_x + int(4 * UI_SCALE), right_y))
            right_y += int(17 * UI_SCALE)

    right_y += int(14 * UI_SCALE)
    diags_header = info_font_bold.render("Diagonals added this step:", True, DARK_GRAY)
    screen.blit(diags_header, (right_col_x, right_y))
    right_y += int(20 * UI_SCALE)

    new_diags = [d for d in step.diagonals_after if d not in step.diagonals_before]
    if new_diags:
        for a, b in new_diags:
            d_str = f"v{a} -- v{b}"
            surf = code_font.render(d_str, True, (200, 130, 30))
            screen.blit(surf, (right_col_x + int(4 * UI_SCALE), right_y))
            right_y += int(17 * UI_SCALE)
    else:
        none_surf = small_font.render("(none)", True, HINT_COLOR)
        screen.blit(none_surf, (right_col_x + int(4 * UI_SCALE), right_y))

    right_y += int(20 * UI_SCALE)
    legend_header = info_font_bold.render("Legend:", True, DARK_GRAY)
    screen.blit(legend_header, (right_col_x, right_y))
    right_y += int(20 * UI_SCALE)

    legend_items = [
        (TUTORIAL_ACTIVE_VERTEX, "Current vertex (vi)"),
        (TUTORIAL_EDGE_COLOR, "Current edges (ei-1, ei)"),
        (TUTORIAL_PREDECESSOR_COLOR, "Predecessor edge (ej)"),
        (TUTORIAL_HELPER_COLOR, "Helper of ei-1"),
        ((160, 120, 255), "Helper of ej"),
        (DIAGONAL_COLOR, "Diagonals"),
    ]
    for color, label in legend_items:
        pygame.draw.rect(
            screen,
            color,
            (right_col_x + int(4 * UI_SCALE), right_y + int(1 * UI_SCALE), int(14 * UI_SCALE), int(10 * UI_SCALE)),
            border_radius=max(1, int(2 * UI_SCALE)),
        )
        surf = small_font.render(label, True, DARK_GRAY)
        screen.blit(surf, (right_col_x + int(24 * UI_SCALE), right_y))
        right_y += int(17 * UI_SCALE)

    btn_prev.draw(screen, enabled=(not tut_state.at_start()))
    btn_next.draw(screen, enabled=(not tut_state.at_end()))
    btn_exit.draw(screen)

    esc_hint = small_font.render("ESC - back to results", True, HINT_COLOR)
    screen.blit(esc_hint, (x, panel_rect.bottom - int(24 * UI_SCALE)))
