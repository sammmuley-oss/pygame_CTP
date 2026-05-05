"""
ui.py - Stealth Game UI Screens & HUD
"""

import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, BLACK, DARK_GRAY, LIGHT_GRAY,
    HUD_TEXT, HUD_ACCENT, WIN_COLOR, LOSE_COLOR, TITLE_COLOR,
    MAP_PACKS
)


class UI:
    def __init__(self):
        try:
            self.font_large = pygame.font.SysFont("consolas", 52, bold=True)
            self.font_medium = pygame.font.SysFont("consolas", 28)
            self.font_small = pygame.font.SysFont("consolas", 18)
            self.font_tiny = pygame.font.SysFont("consolas", 14)
        except Exception:
            self.font_large = pygame.font.Font(None, 52)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 18)
            self.font_tiny = pygame.font.Font(None, 14)
        self.anim_timer = 0

    def update(self):
        self.anim_timer += 1

    def draw_menu(self, surface):
        surface.fill(DARK_GRAY)
        self._draw_particles(surface)
        title_y = SCREEN_HEIGHT // 2 - 130
        pulse = math.sin(self.anim_timer * 0.05) * 5
        sh = self.font_large.render("HUNTER ASSASSIN", True, (60, 15, 15))
        surface.blit(sh, sh.get_rect(center=(SCREEN_WIDTH//2+3, title_y+3+pulse)))
        t = self.font_large.render("HUNTER ASSASSIN", True, TITLE_COLOR)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, title_y+pulse)))
        sub = self.font_small.render("A Stealth Elimination Game", True, LIGHT_GRAY)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, title_y+55)))
        lines = [
            "WASD / Arrow Keys  —  Move", "",
            "Sneak BEHIND enemies to eliminate them",
            "Stay OUT of their vision cone!",
            "Eliminate ALL guards to clear the level",
        ]
        y = SCREEN_HEIGHT // 2 + 5
        for i, line in enumerate(lines):
            if line:
                txt = self.font_small.render(line, True, HUD_TEXT)
                surface.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, y + i*26)))
        if (self.anim_timer // 40) % 2 == 0:
            st = self.font_medium.render("Press ENTER to Start", True, HUD_ACCENT)
            surface.blit(st, st.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-80)))
        cr = self.font_tiny.render("Made with Python + Pygame", True, (70, 70, 80))
        surface.blit(cr, cr.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-30)))

    def draw_map_select(self, surface, selected_idx):
        """Draw the map/theme selection screen."""
        surface.fill(DARK_GRAY)
        self._draw_particles(surface)

        title_y = 100
        pulse = math.sin(self.anim_timer * 0.05) * 3
        t = self.font_large.render("SELECT MAP", True, TITLE_COLOR)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, title_y + pulse)))

        sub = self.font_small.render("Use LEFT / RIGHT arrows to select, ENTER to confirm", True, LIGHT_GRAY)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, title_y + 55)))

        # Draw map options as cards
        card_w = 260
        card_h = 220
        total_w = len(MAP_PACKS) * card_w + (len(MAP_PACKS) - 1) * 40
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = SCREEN_HEIGHT // 2 - 40

        for i, pack in enumerate(MAP_PACKS):
            cx = start_x + i * (card_w + 40)
            is_selected = (i == selected_idx)

            # Card background
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_selected:
                # Glowing border
                glow = pygame.Surface((card_w + 8, card_h + 8), pygame.SRCALPHA)
                pulse_alpha = int(120 + math.sin(self.anim_timer * 0.08) * 60)
                pygame.draw.rect(glow, (100, 200, 255, pulse_alpha), (0, 0, card_w + 8, card_h + 8), border_radius=14)
                surface.blit(glow, (cx - 4, card_y - 4))
                bg_col = (40, 50, 65, 230)
            else:
                bg_col = (28, 28, 38, 200)

            pygame.draw.rect(card_surf, bg_col, (0, 0, card_w, card_h), border_radius=12)
            surface.blit(card_surf, (cx, card_y))

            # Map preview (mini tiles)
            theme = pack["theme"]
            preview_size = 8
            preview_x = cx + 20
            preview_y = card_y + 45
            first_map = pack["levels"][0]["map"]
            for r in range(min(15, len(first_map))):
                for c in range(min(20, len(first_map[0]))):
                    tile = first_map[r][c]
                    if tile == 1:
                        color = theme["wall"]
                    else:
                        color = theme["floor1"] if (r+c) % 2 == 0 else theme["floor2"]
                    px = preview_x + c * (preview_size + 1)
                    py = preview_y + r * (preview_size + 1)
                    pygame.draw.rect(surface, color, (px, py, preview_size, preview_size))

            # Map name
            name_col = HUD_ACCENT if is_selected else LIGHT_GRAY
            name = self.font_medium.render(pack["name"], True, name_col)
            surface.blit(name, name.get_rect(center=(cx + card_w // 2, card_y + 22)))

            # Level count
            lvl_text = f"{len(pack['levels'])} Levels"
            lvl = self.font_small.render(lvl_text, True, (180, 180, 190) if is_selected else (100, 100, 110))
            surface.blit(lvl, lvl.get_rect(center=(cx + card_w // 2, card_y + card_h - 18)))

        # Arrows
        arrow_y = card_y + card_h // 2
        if selected_idx > 0:
            arr = self.font_large.render("<", True, HUD_ACCENT)
            surface.blit(arr, arr.get_rect(center=(start_x - 30, arrow_y)))
        if selected_idx < len(MAP_PACKS) - 1:
            arr = self.font_large.render(">", True, HUD_ACCENT)
            surface.blit(arr, arr.get_rect(center=(start_x + total_w + 30, arrow_y)))

        # Back hint
        back = self.font_small.render("Press ESC to go back", True, (80, 80, 90))
        surface.blit(back, back.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))

    def draw_hud(self, surface, level, enemies_left, elapsed_time):
        panel = pygame.Surface((140, 24), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 20, 28, 180), (0, 0, 140, 24), border_radius=4)
        surface.blit(panel, (10, 10))
        lt = self.font_small.render(f"LEVEL {level}", True, HUD_ACCENT)
        surface.blit(lt, (18, 13))
        panel2 = pygame.Surface((160, 24), pygame.SRCALPHA)
        pygame.draw.rect(panel2, (20, 20, 28, 180), (0, 0, 160, 24), border_radius=4)
        surface.blit(panel2, (10, 40))
        et = self.font_small.render(f"GUARDS: {enemies_left}", True, (255, 120, 120))
        surface.blit(et, (18, 43))
        m, s = int(elapsed_time) // 60, int(elapsed_time) % 60
        ts = pygame.Surface((130, 24), pygame.SRCALPHA)
        pygame.draw.rect(ts, (20, 20, 28, 180), (0, 0, 130, 24), border_radius=4)
        surface.blit(ts, (SCREEN_WIDTH//2 - 65, 10))
        tt = self.font_small.render(f"TIME: {m:02d}:{s:02d}", True, HUD_ACCENT)
        surface.blit(tt, tt.get_rect(center=(SCREEN_WIDTH//2, 22)))

    def draw_game_over(self, surface, elapsed_time):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))
        shake = math.sin(self.anim_timer * 0.3) * 3 if self.anim_timer < 60 else 0
        t = self.font_large.render("DETECTED!", True, LOSE_COLOR)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2 + shake, SCREEN_HEIGHT//2 - 60)))
        m, s = int(elapsed_time) // 60, int(elapsed_time) % 60
        tt = self.font_medium.render(f"Time: {m:02d}:{s:02d}", True, LIGHT_GRAY)
        surface.blit(tt, tt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10)))
        msg = self.font_small.render("A guard spotted you!", True, (200, 100, 100))
        surface.blit(msg, msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))
        if (self.anim_timer // 35) % 2 == 0:
            r = self.font_medium.render("Press R to Retry", True, HUD_ACCENT)
            surface.blit(r, r.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 110)))
        q = self.font_small.render("Press ESC to Quit", True, (100, 100, 110))
        surface.blit(q, q.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-40)))

    def draw_level_clear(self, surface, level, elapsed_time):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 15, 0, 180))
        surface.blit(overlay, (0, 0))
        pulse = math.sin(self.anim_timer * 0.06) * 4
        t = self.font_large.render(f"LEVEL {level} CLEAR!", True, WIN_COLOR)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60 + pulse)))
        m, s = int(elapsed_time) // 60, int(elapsed_time) % 60
        tt = self.font_medium.render(f"Time: {m:02d}:{s:02d}", True, WHITE)
        surface.blit(tt, tt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10)))
        msg = self.font_small.render("All guards eliminated!", True, (150, 255, 180))
        surface.blit(msg, msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 45)))
        if (self.anim_timer // 35) % 2 == 0:
            r = self.font_medium.render("Press ENTER for Next Level", True, HUD_ACCENT)
            surface.blit(r, r.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 110)))

    def draw_win(self, surface, elapsed_time, total_levels):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 20, 0, 190))
        surface.blit(overlay, (0, 0))
        pulse = math.sin(self.anim_timer * 0.06) * 4
        t = self.font_large.render("MISSION COMPLETE!", True, WIN_COLOR)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70 + pulse)))
        m, s = int(elapsed_time) // 60, int(elapsed_time) % 60
        tt = self.font_medium.render(f"Total Time: {m:02d}:{s:02d}", True, WHITE)
        surface.blit(tt, tt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 5)))
        msg = self.font_small.render(f"All {total_levels} levels completed!", True, (150, 255, 180))
        surface.blit(msg, msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 45)))
        if (self.anim_timer // 35) % 2 == 0:
            r = self.font_medium.render("Press R to Play Again", True, HUD_ACCENT)
            surface.blit(r, r.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 110)))
        q = self.font_small.render("Press ESC to Quit", True, (100, 100, 110))
        surface.blit(q, q.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-40)))

    def _draw_particles(self, surface):
        for i in range(15):
            x = (i * 137 + self.anim_timer * (0.2 + i * 0.05)) % SCREEN_WIDTH
            y = (i * 97 + self.anim_timer * (0.3 + i * 0.03)) % SCREEN_HEIGHT
            sz = 2 + (i % 3)
            ps = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (180, 50, 50, 30 + (i*7)%40), (sz, sz), sz)
            surface.blit(ps, (int(x), int(y)))
