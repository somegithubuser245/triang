import pygame

from config import (
    ACCENT,
    BLACK,
    BUTTON_HOVER,
    DARK_GRAY,
    GRAY,
    HINT_COLOR,
    INPUT_ACTIVE_BORDER,
    INPUT_BG,
    INPUT_BORDER,
    LABEL_COLOR,
    WHITE,
)


class InputBox:
    def __init__(self, x, y, w, h, label="", hint="", text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = INPUT_BORDER
        self.text = text
        self.label = label
        self.hint = hint
        self.active = False
        self.font = pygame.font.SysFont("Arial", 20)
        self.label_font = pygame.font.SysFont("Arial", 16)
        self.hint_font = pygame.font.SysFont("Arial", 14)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = INPUT_ACTIVE_BORDER if self.active else INPUT_BORDER
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_TAB):
                return "next"
            elif event.unicode.isdigit() or event.unicode == ".":
                self.text += event.unicode
        return None

    def draw(self, screen):
        if self.label:
            lbl = self.label_font.render(self.label, True, LABEL_COLOR)
            screen.blit(lbl, (self.rect.x, self.rect.y - 24))
        if self.hint and not self.text:
            hint_surf = self.hint_font.render(self.hint, True, HINT_COLOR)
            screen.blit(hint_surf, (self.rect.x + 10, self.rect.y + 8))
        pygame.draw.rect(screen, INPUT_BG, self.rect, border_radius=6)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=6)
        txt_surf = self.font.render(self.text, True, BLACK)
        screen.blit(txt_surf, (self.rect.x + 10, self.rect.y + 6))

    def value(self):
        try:
            return float(self.text) if self.text else 0
        except ValueError:
            return 0


class Button:
    def __init__(self, x, y, w, h, text, color=ACCENT, hover=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.hovered = False
        self.color = color
        self.hover = hover

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False

    def draw(self, screen, enabled=True):
        if not enabled:
            pygame.draw.rect(screen, GRAY, self.rect, border_radius=8)
            txt_surf = self.font.render(self.text, True, DARK_GRAY)
        else:
            color = self.hover if self.hovered else self.color
            pygame.draw.rect(screen, color, self.rect, border_radius=8)
            txt_surf = self.font.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)
