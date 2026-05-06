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
            self.font_title = pygame.font.SysFont("consolas", 58, bold=True)
            self.font_large = pygame.font.SysFont("consolas", 52, bold=True)
            self.font_medium = pygame.font.SysFont("consolas", 28)
            self.font_small = pygame.font.SysFont("consolas", 18)
            self.font_tiny = pygame.font.SysFont("consolas", 14)
            self.font_cta = pygame.font.SysFont("consolas", 30, bold=True)
            self.font_controls = pygame.font.SysFont("consolas", 16)
        except Exception:
            self.font_title = pygame.font.Font(None, 58)
            self.font_large = pygame.font.Font(None, 52)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 18)
            self.font_tiny = pygame.font.Font(None, 14)
            self.font_cta = pygame.font.Font(None, 30)
            self.font_controls = pygame.font.Font(None, 16)
        self.anim_timer = 0

    def update(self):
        self.anim_timer += 1

    # ──────────────────────────────────────────────────────────────
    #   MAIN MENU
    # ──────────────────────────────────────────────────────────────
    def draw_menu(self, surface):
        surface.fill((12, 12, 18))

        # --- Subtle scanline overlay ---
        self._draw_scanlines(surface)

        # --- Ambient particles (refined) ---
        self._draw_particles(surface)

        # --- Outer frame border ---
        self._draw_frame_border(surface)

        # --- Decorative top line accent ---
        accent_y = 60
        line_w = 260
        cx = SCREEN_WIDTH // 2
        pygame.draw.line(surface, (60, 60, 80), (cx - line_w, accent_y), (cx + line_w, accent_y), 1)
        # Small diamond in the center of the top line
        diamond_pts = [(cx, accent_y - 5), (cx + 5, accent_y), (cx, accent_y + 5), (cx - 5, accent_y)]
        pygame.draw.polygon(surface, (80, 80, 110), diamond_pts, 1)

        # --- Title section ---
        title_y = 120
        pulse = math.sin(self.anim_timer * 0.04) * 3

        # Glow layers (soft bloom behind the text)
        for i in range(3):
            glow_alpha = 18 - i * 5
            glow_col = (255, 70, 70)
            glow_surf = self.font_title.render("HUNTER ASSASSIN", True, glow_col)
            glow_overlay = pygame.Surface(glow_surf.get_size(), pygame.SRCALPHA)
            glow_overlay.blit(glow_surf, (0, 0))
            glow_overlay.set_alpha(glow_alpha)
            offset = (i + 1) * 2
            surface.blit(glow_overlay, glow_overlay.get_rect(
                center=(cx + offset, title_y + pulse + offset)))

        # Shadow
        sh = self.font_title.render("HUNTER ASSASSIN", True, (40, 10, 10))
        surface.blit(sh, sh.get_rect(center=(cx + 2, title_y + 2 + pulse)))

        # Main title
        t = self.font_title.render("HUNTER ASSASSIN", True, TITLE_COLOR)
        surface.blit(t, t.get_rect(center=(cx, title_y + pulse)))

        # Subtitle with refined style
        sub_y = title_y + 55
        sub = self.font_small.render("A  S T E A L T H  E L I M I N A T I O N  G A M E", True, (120, 120, 140))
        surface.blit(sub, sub.get_rect(center=(cx, sub_y)))

        # --- Decorative divider below subtitle ---
        div_y = sub_y + 28
        pygame.draw.line(surface, (45, 45, 60), (cx - 180, div_y), (cx - 20, div_y), 1)
        pygame.draw.line(surface, (45, 45, 60), (cx + 20, div_y), (cx + 180, div_y), 1)
        # Small crosshair icon in the gap
        self._draw_crosshair(surface, cx, div_y, 8, (70, 70, 90))

        # --- Instructions panel ---
        panel_y = div_y + 30
        panel_w = 380
        panel_h = 170
        panel_x = cx - panel_w // 2

        # Panel background with subtle border
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 20, 30, 140), (0, 0, panel_w, panel_h), border_radius=6)
        pygame.draw.rect(panel_surf, (50, 50, 65, 100), (0, 0, panel_w, panel_h), width=1, border_radius=6)
        surface.blit(panel_surf, (panel_x, panel_y))

        # Panel header
        hdr = self.font_controls.render("—  HOW  TO  PLAY  —", True, (100, 100, 120))
        surface.blit(hdr, hdr.get_rect(center=(cx, panel_y + 20)))

        # Control instructions
        instructions = [
            ("WASD / Arrow Keys", "Move"),
            ("Sneak BEHIND", "Eliminate enemies"),
            ("Stay OUT", "of their vision cone"),
            ("Eliminate ALL", "guards to clear"),
        ]
        instr_y = panel_y + 48
        for i, (key_text, desc_text) in enumerate(instructions):
            y = instr_y + i * 28
            # Key part (highlighted)
            kt = self.font_controls.render(key_text, True, HUD_ACCENT)
            # Description part (dimmer)
            dt = self.font_controls.render(f"  —  {desc_text}", True, (140, 140, 155))
            total_w = kt.get_width() + dt.get_width()
            start_x = cx - total_w // 2
            surface.blit(kt, (start_x, y))
            surface.blit(dt, (start_x + kt.get_width(), y))

        # --- Bottom divider ---
        bot_div_y = panel_y + panel_h + 25
        pygame.draw.line(surface, (40, 40, 55), (cx - 140, bot_div_y), (cx + 140, bot_div_y), 1)

        # --- CTA: "Press ENTER to Start" with smooth fade pulse ---
        cta_y = bot_div_y + 40
        # Smooth sinusoidal alpha pulse (never fully invisible)
        alpha = int(140 + 115 * math.sin(self.anim_timer * 0.06))
        alpha = max(40, min(255, alpha))

        cta_text = self.font_cta.render("Press ENTER to Start", True, HUD_ACCENT)
        cta_overlay = pygame.Surface(cta_text.get_size(), pygame.SRCALPHA)
        cta_overlay.blit(cta_text, (0, 0))
        cta_overlay.set_alpha(alpha)
        surface.blit(cta_overlay, cta_text.get_rect(center=(cx, cta_y)))

        # Subtle underline for CTA
        underline_alpha = max(20, alpha // 3)
        ul_surf = pygame.Surface((cta_text.get_width() + 20, 1), pygame.SRCALPHA)
        ul_surf.fill((100, 200, 255, underline_alpha))
        surface.blit(ul_surf, (cx - cta_text.get_width() // 2 - 10, cta_y + 22))

        # --- Footer ---
        cr = self.font_tiny.render("Made with Python + Pygame", True, (50, 50, 60))
        surface.blit(cr, cr.get_rect(center=(cx, SCREEN_HEIGHT - 28)))

        # Version / flavor text
        ver = self.font_tiny.render("v1.0", True, (40, 40, 50))
        surface.blit(ver, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 28))

    # ──────────────────────────────────────────────────────────────
    #   MAP SELECTION SCREEN
    # ──────────────────────────────────────────────────────────────
    def draw_map_select(self, surface, selected_idx):
        """Draw the map/theme selection screen."""
        surface.fill(DARK_GRAY)
        self._draw_scanlines(surface)
        self._draw_particles(surface)
        self._draw_frame_border(surface)

        cx = SCREEN_WIDTH // 2
        title_y = 100
        pulse = math.sin(self.anim_timer * 0.05) * 3
        t = self.font_large.render("SELECT MAP", True, TITLE_COLOR)
        surface.blit(t, t.get_rect(center=(cx, title_y + pulse)))

        sub = self.font_small.render("Use LEFT / RIGHT arrows to select, ENTER to confirm", True, LIGHT_GRAY)
        surface.blit(sub, sub.get_rect(center=(cx, title_y + 55)))

        # Draw map options as cards
        card_w = 260
        card_h = 220
        total_w = len(MAP_PACKS) * card_w + (len(MAP_PACKS) - 1) * 40
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = SCREEN_HEIGHT // 2 - 40

        for i, pack in enumerate(MAP_PACKS):
            card_x = start_x + i * (card_w + 40)
            is_selected = (i == selected_idx)

            # Card background
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_selected:
                # Glowing border
                glow = pygame.Surface((card_w + 8, card_h + 8), pygame.SRCALPHA)
                pulse_alpha = int(120 + math.sin(self.anim_timer * 0.08) * 60)
                pygame.draw.rect(glow, (100, 200, 255, pulse_alpha), (0, 0, card_w + 8, card_h + 8), border_radius=14)
                surface.blit(glow, (card_x - 4, card_y - 4))
                bg_col = (40, 50, 65, 230)
            else:
                bg_col = (28, 28, 38, 200)

            pygame.draw.rect(card_surf, bg_col, (0, 0, card_w, card_h), border_radius=12)
            surface.blit(card_surf, (card_x, card_y))

            # Map preview (mini tiles)
            theme = pack["theme"]
            preview_size = 8
            preview_x = card_x + 20
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
            surface.blit(name, name.get_rect(center=(card_x + card_w // 2, card_y + 22)))

            # Level count
            lvl_text = f"{len(pack['levels'])} Levels"
            lvl = self.font_small.render(lvl_text, True, (180, 180, 190) if is_selected else (100, 100, 110))
            surface.blit(lvl, lvl.get_rect(center=(card_x + card_w // 2, card_y + card_h - 18)))

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

    # ──────────────────────────────────────────────────────────────
    #   HUD
    # ──────────────────────────────────────────────────────────────
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

    # ──────────────────────────────────────────────────────────────
    #   GAME OVER
    # ──────────────────────────────────────────────────────────────
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

    # ──────────────────────────────────────────────────────────────
    #   LEVEL CLEAR
    # ──────────────────────────────────────────────────────────────
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

    # ──────────────────────────────────────────────────────────────
    #   WIN SCREEN
    # ──────────────────────────────────────────────────────────────
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

    # ──────────────────────────────────────────────────────────────
    #   HELPER: Particles
    # ──────────────────────────────────────────────────────────────
    def _draw_particles(self, surface):
        for i in range(20):
            x = (i * 137 + self.anim_timer * (0.15 + i * 0.03)) % SCREEN_WIDTH
            y = (i * 97 + self.anim_timer * (0.2 + i * 0.02)) % SCREEN_HEIGHT
            sz = 1 + (i % 3)
            alpha = 15 + (i * 5) % 30
            ps = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            # Subtle cool-toned particles instead of bright red
            r_col = 80 + (i * 13) % 40
            g_col = 80 + (i * 7) % 30
            b_col = 100 + (i * 11) % 50
            pygame.draw.circle(ps, (r_col, g_col, b_col, alpha), (sz, sz), sz)
            surface.blit(ps, (int(x), int(y)))

    # ──────────────────────────────────────────────────────────────
    #   HELPER: Scanlines
    # ──────────────────────────────────────────────────────────────
    def _draw_scanlines(self, surface):
        """Draw subtle horizontal scanlines for a tactical CRT feel."""
        scanline_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(scanline_surf, (0, 0, 0, 12), (0, y), (SCREEN_WIDTH, y), 1)
        surface.blit(scanline_surf, (0, 0))

    # ──────────────────────────────────────────────────────────────
    #   HELPER: Frame border
    # ──────────────────────────────────────────────────────────────
    def _draw_frame_border(self, surface):
        """Draw a thin elegant border frame around the screen."""
        margin = 12
        w = SCREEN_WIDTH - margin * 2
        h = SCREEN_HEIGHT - margin * 2
        # Outer line
        border_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, (50, 50, 65, 60), (margin, margin, w, h), width=1, border_radius=2)
        # Corner accents (small L-shapes)
        corner_len = 20
        col = (70, 70, 90, 90)
        # Top-left
        pygame.draw.line(border_surf, col, (margin, margin), (margin + corner_len, margin), 2)
        pygame.draw.line(border_surf, col, (margin, margin), (margin, margin + corner_len), 2)
        # Top-right
        pygame.draw.line(border_surf, col, (margin + w, margin), (margin + w - corner_len, margin), 2)
        pygame.draw.line(border_surf, col, (margin + w, margin), (margin + w, margin + corner_len), 2)
        # Bottom-left
        pygame.draw.line(border_surf, col, (margin, margin + h), (margin + corner_len, margin + h), 2)
        pygame.draw.line(border_surf, col, (margin, margin + h), (margin, margin + h - corner_len), 2)
        # Bottom-right
        pygame.draw.line(border_surf, col, (margin + w, margin + h), (margin + w - corner_len, margin + h), 2)
        pygame.draw.line(border_surf, col, (margin + w, margin + h), (margin + w, margin + h - corner_len), 2)
        surface.blit(border_surf, (0, 0))

    # ──────────────────────────────────────────────────────────────
    #   HELPER: Crosshair icon
    # ──────────────────────────────────────────────────────────────
    def _draw_crosshair(self, surface, x, y, size, color):
        """Draw a small crosshair/target icon."""
        s = size
        # Horizontal line
        pygame.draw.line(surface, color, (x - s, y), (x - s // 3, y), 1)
        pygame.draw.line(surface, color, (x + s // 3, y), (x + s, y), 1)
        # Vertical line
        pygame.draw.line(surface, color, (x, y - s), (x, y - s // 3), 1)
        pygame.draw.line(surface, color, (x, y + s // 3), (x, y + s), 1)
        # Center dot
        pygame.draw.circle(surface, color, (x, y), 1)
