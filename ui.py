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
            # Blocky Minecraft-style title font (Impact is heavy & wide)
            self.font_title = pygame.font.SysFont("impact", 72, bold=False)
            self.font_large = pygame.font.SysFont("impact", 48, bold=False)
            self.font_medium = pygame.font.SysFont("consolas", 28)
            self.font_small = pygame.font.SysFont("consolas", 18)
            self.font_tiny = pygame.font.SysFont("consolas", 14)
            self.font_cta = pygame.font.SysFont("consolas", 30, bold=True)
            self.font_controls = pygame.font.SysFont("consolas", 16)
        except Exception:
            self.font_title = pygame.font.Font(None, 72)
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 18)
            self.font_tiny = pygame.font.Font(None, 14)
            self.font_cta = pygame.font.Font(None, 30)
            self.font_controls = pygame.font.Font(None, 16)
        self.anim_timer = 0

    def update(self):
        self.anim_timer += 1

    # ──────────────────────────────────────────────────────────────
    #   QUIT CONFIRMATION SCREEN
    # ──────────────────────────────────────────────────────────────
    def draw_quit_confirm(self, surface):
        """Quit confirmation screen — themed to match the game aesthetic."""
        surface.fill((12, 12, 18))

        # --- Atmospheric layers (same as main menu) ---
        self._draw_scanlines(surface)
        self._draw_particles(surface)
        self._draw_frame_border(surface)

        cx = SCREEN_WIDTH // 2

        # --- Top decorative line ---
        accent_y = 80
        line_w = 200
        pygame.draw.line(surface, (60, 60, 80), (cx - line_w, accent_y), (cx + line_w, accent_y), 1)
        diamond_pts = [(cx, accent_y - 5), (cx + 5, accent_y), (cx, accent_y + 5), (cx - 5, accent_y)]
        pygame.draw.polygon(surface, (80, 80, 110), diamond_pts, 1)

        # --- Animated crosshair (danger feel) ---
        ch_y = 155
        pulse = math.sin(self.anim_timer * 0.06) * 3
        # Rotating outer ring
        ring_r = 30
        ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
        ring_cx = ring_r + 2
        ring_cy = ring_r + 2
        pygame.draw.circle(ring_surf, (80, 30, 30, 70), (ring_cx, ring_cy), ring_r, 2)
        angle_offset = self.anim_timer * 0.03
        for i in range(6):
            a = angle_offset + i * math.pi / 3
            x1 = ring_cx + int((ring_r - 4) * math.cos(a))
            y1 = ring_cy + int((ring_r - 4) * math.sin(a))
            x2 = ring_cx + int((ring_r + 1) * math.cos(a))
            y2 = ring_cy + int((ring_r + 1) * math.sin(a))
            pygame.draw.line(ring_surf, (120, 40, 40, 100), (x1, y1), (x2, y2), 2)
        surface.blit(ring_surf, (cx - ring_cx, ch_y - ring_cy + pulse))
        # Inner crosshair
        ch_s = 12
        ch_col = (200, 50, 50)
        pygame.draw.line(surface, ch_col, (cx - ch_s, ch_y + pulse), (cx - 4, ch_y + pulse), 2)
        pygame.draw.line(surface, ch_col, (cx + 4, ch_y + pulse), (cx + ch_s, ch_y + pulse), 2)
        pygame.draw.line(surface, ch_col, (cx, ch_y - ch_s + pulse), (cx, ch_y - 4 + pulse), 2)
        pygame.draw.line(surface, ch_col, (cx, ch_y + 4 + pulse), (cx, ch_y + ch_s + pulse), 2)
        pygame.draw.circle(surface, (255, 60, 60), (cx, int(ch_y + pulse)), 2)

        # --- Headline ---
        headline = self.font_medium.render("The game remembers quitters.", True, (160, 160, 175))
        surface.blit(headline, headline.get_rect(center=(cx, 215)))

        # Divider below headline
        div_y = 240
        pygame.draw.line(surface, (45, 45, 60), (cx - 160, div_y), (cx - 10, div_y), 1)
        pygame.draw.line(surface, (45, 45, 60), (cx + 10, div_y), (cx + 160, div_y), 1)
        self._draw_crosshair(surface, cx, div_y, 6, (60, 60, 80))

        # Button dimensions
        btn_w = 420
        btn_h = 56

        # ── RED BUTTON ──
        red_y = 275
        red_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(red_surf, (45, 12, 12, 220), (0, 0, btn_w, btn_h), border_radius=6)
        # Animated border
        r_alpha = int(100 + 60 * math.sin(self.anim_timer * 0.06))
        pygame.draw.rect(red_surf, (180, 50, 50, r_alpha), (0, 0, btn_w, btn_h), width=2, border_radius=6)
        surface.blit(red_surf, (cx - btn_w // 2, red_y))
        # Text
        red_txt = self.font_cta.render("Don't have enough guts?", True, (220, 80, 70))
        surface.blit(red_txt, red_txt.get_rect(center=(cx, red_y + btn_h // 2)))
        # Hint
        esc_hint = self.font_tiny.render("[ ESC ]", True, (120, 55, 55))
        surface.blit(esc_hint, esc_hint.get_rect(center=(cx, red_y + btn_h + 14)))

        # ── GREEN BUTTON ──
        green_y = 380
        green_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(green_surf, (12, 40, 20, 220), (0, 0, btn_w, btn_h), border_radius=6)
        # Animated border
        g_alpha = int(100 + 60 * math.sin(self.anim_timer * 0.06 + 1.0))
        pygame.draw.rect(green_surf, (50, 180, 80, g_alpha), (0, 0, btn_w, btn_h), width=2, border_radius=6)
        surface.blit(green_surf, (cx - btn_w // 2, green_y))
        # Text (pulsing brightness)
        txt_alpha = int(180 + 75 * math.sin(self.anim_timer * 0.08))
        green_txt = self.font_cta.render("Just kidding!", True, (80, 230, 110))
        gt_surf = pygame.Surface(green_txt.get_size(), pygame.SRCALPHA)
        gt_surf.blit(green_txt, (0, 0))
        gt_surf.set_alpha(txt_alpha)
        surface.blit(gt_surf, green_txt.get_rect(center=(cx, green_y + btn_h // 2)))
        # Hint
        enter_hint = self.font_tiny.render("[ ENTER ]", True, (55, 120, 70))
        surface.blit(enter_hint, enter_hint.get_rect(center=(cx, green_y + btn_h + 14)))

        # --- Footer ---
        footer = self.font_tiny.render("Choose wisely, shadow.", True, (50, 50, 60))
        surface.blit(footer, footer.get_rect(center=(cx, SCREEN_HEIGHT - 35)))

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

        # --- Title section (Minecraft-inspired 3D blocky text) ---
        title_y = 105
        pulse = math.sin(self.anim_timer * 0.04) * 2
        title_text = "NOCTURNE VOID"

        # 3D extrusion depth layers (darkest at back, brighter toward front)
        depth = 6
        for d in range(depth, 0, -1):
            # Gradient from very dark maroon (back) to dark red (front)
            shade = int(40 + (depth - d) * 12)
            col = (shade, 5, 5)
            layer = self.font_title.render(title_text, True, col)
            surface.blit(layer, layer.get_rect(
                center=(cx + d, title_y + pulse + d)))

        # Outline pass (render in near-black at slight offsets)
        outline_col = (20, 0, 0)
        for ox, oy in [(-2,0),(2,0),(0,-2),(0,2),(-1,-1),(1,-1),(-1,1),(1,1)]:
            ol = self.font_title.render(title_text, True, outline_col)
            surface.blit(ol, ol.get_rect(center=(cx + ox, title_y + pulse + oy)))

        # Main face (bright red)
        face_col = (220, 45, 40)
        face = self.font_title.render(title_text, True, face_col)
        surface.blit(face, face.get_rect(center=(cx, title_y + pulse)))

        # Top highlight strip (lighter red on upper portion for 3D pop)
        highlight_col = (255, 90, 75)
        highlight = self.font_title.render(title_text, True, highlight_col)
        # Clip to only show top ~40% of the text
        h_rect = highlight.get_rect(center=(cx, title_y + pulse))
        clip_h = h_rect.height * 4 // 10
        clip_surf = pygame.Surface((h_rect.width, clip_h), pygame.SRCALPHA)
        clip_surf.blit(highlight, (0, 0), (0, 0, h_rect.width, clip_h))
        surface.blit(clip_surf, (h_rect.x, h_rect.y))

        # Subtle glow behind title
        glow_surf = self.font_title.render(title_text, True, (255, 50, 40))
        glow_overlay = pygame.Surface(glow_surf.get_size(), pygame.SRCALPHA)
        glow_overlay.blit(glow_surf, (0, 0))
        glow_overlay.set_alpha(20)
        surface.blit(glow_overlay, glow_overlay.get_rect(
            center=(cx, title_y + pulse + 3)))

        # Subtitle
        sub_y = title_y + 65
        sub = self.font_small.render("S T E A L T H  ·  E L I M I N A T I O N  ·  S U R V I V A L", True, (120, 120, 140))
        surface.blit(sub, sub.get_rect(center=(cx, sub_y)))

        # --- Decorative divider below subtitle ---
        div_y = sub_y + 28
        pygame.draw.line(surface, (45, 45, 60), (cx - 180, div_y), (cx - 20, div_y), 1)
        pygame.draw.line(surface, (45, 45, 60), (cx + 20, div_y), (cx + 180, div_y), 1)
        # Small crosshair icon in the gap
        self._draw_crosshair(surface, cx, div_y, 8, (70, 70, 90))

        # --- Large animated crosshair centerpiece ---
        center_y = SCREEN_HEIGHT // 2 + 20
        # Rotating outer ring
        ring_r = 55
        ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
        ring_cx = ring_r + 2
        ring_cy = ring_r + 2
        # Outer ring
        pygame.draw.circle(ring_surf, (60, 60, 80, 80), (ring_cx, ring_cy), ring_r, 2)
        # Inner ring
        pygame.draw.circle(ring_surf, (80, 80, 110, 60), (ring_cx, ring_cy), ring_r - 15, 1)
        # Rotating tick marks
        angle_offset = self.anim_timer * 0.02
        for i in range(8):
            a = angle_offset + i * math.pi / 4
            x1 = ring_cx + int((ring_r - 6) * math.cos(a))
            y1 = ring_cy + int((ring_r - 6) * math.sin(a))
            x2 = ring_cx + int((ring_r + 1) * math.cos(a))
            y2 = ring_cy + int((ring_r + 1) * math.sin(a))
            pygame.draw.line(ring_surf, (100, 100, 130, 120), (x1, y1), (x2, y2), 2)
        surface.blit(ring_surf, (cx - ring_cx, center_y - ring_cy))

        # Center crosshair (static, sharp)
        ch_size = 20
        ch_col = (200, 60, 60)
        pygame.draw.line(surface, ch_col, (cx - ch_size, center_y), (cx - 6, center_y), 2)
        pygame.draw.line(surface, ch_col, (cx + 6, center_y), (cx + ch_size, center_y), 2)
        pygame.draw.line(surface, ch_col, (cx, center_y - ch_size), (cx, center_y - 6), 2)
        pygame.draw.line(surface, ch_col, (cx, center_y + 6), (cx, center_y + ch_size), 2)
        # Center dot
        pygame.draw.circle(surface, (255, 80, 80), (cx, center_y), 3)
        # Glow around dot
        glow_s = pygame.Surface((20, 20), pygame.SRCALPHA)
        glow_alpha = int(40 + 20 * math.sin(self.anim_timer * 0.08))
        pygame.draw.circle(glow_s, (255, 60, 60, glow_alpha), (10, 10), 10)
        surface.blit(glow_s, (cx - 10, center_y - 10))

        # --- Tagline below crosshair ---
        tag_y = center_y + 80
        tag = self.font_small.render("E L I M I N A T E  ·  E V A D E  ·  S U R V I V E", True, (100, 100, 120))
        surface.blit(tag, tag.get_rect(center=(cx, tag_y)))

        # Decorative lines flanking tagline
        tag_w = tag.get_width() // 2 + 15
        line_y = tag_y
        pygame.draw.line(surface, (50, 50, 65), (cx - tag_w - 40, line_y), (cx - tag_w, line_y), 1)
        pygame.draw.line(surface, (50, 50, 65), (cx + tag_w, line_y), (cx + tag_w + 40, line_y), 1)

        # --- CTA Button: big, glowing ---
        cta_y = tag_y + 60
        alpha = int(160 + 95 * math.sin(self.anim_timer * 0.06))
        alpha = max(60, min(255, alpha))

        # Button background
        btn_w = 320
        btn_h = 50
        btn_x = cx - btn_w // 2
        btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (25, 25, 40, 180), (0, 0, btn_w, btn_h), border_radius=8)
        # Animated border glow
        border_col = (100 + int(50 * math.sin(self.anim_timer * 0.05)),
                      200 + int(40 * math.sin(self.anim_timer * 0.05)),
                      255, alpha)
        pygame.draw.rect(btn_surf, border_col, (0, 0, btn_w, btn_h), width=2, border_radius=8)
        surface.blit(btn_surf, (btn_x, cta_y - btn_h // 2))

        cta_text = self.font_cta.render("PRESS ENTER", True, HUD_ACCENT)
        cta_overlay = pygame.Surface(cta_text.get_size(), pygame.SRCALPHA)
        cta_overlay.blit(cta_text, (0, 0))
        cta_overlay.set_alpha(alpha)
        surface.blit(cta_overlay, cta_text.get_rect(center=(cx, cta_y)))

        # --- Footer ---
        cr = self.font_tiny.render("Made with Python + Pygame", True, (50, 50, 60))
        surface.blit(cr, cr.get_rect(center=(cx, SCREEN_HEIGHT - 28)))

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

        sub = self.font_small.render("C H O O S E   Y O U R   B A T T L E G R O U N D", True, LIGHT_GRAY)
        surface.blit(sub, sub.get_rect(center=(cx, title_y + 55)))

        # Draw map options as cards
        card_w = 220
        card_h = 200
        gap = 20
        total_w = len(MAP_PACKS) * card_w + (len(MAP_PACKS) - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = SCREEN_HEIGHT // 2 - 30

        for i, pack in enumerate(MAP_PACKS):
            card_x = start_x + i * (card_w + gap)
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

            # Map preview (mini tiles — smaller to fit card)
            theme = pack["theme"]
            preview_size = 6
            preview_gap = 1
            preview_total_w = 20 * (preview_size + preview_gap)
            preview_x = card_x + (card_w - preview_total_w) // 2
            preview_y = card_y + 42
            first_map = pack["levels"][0]["map"]
            for r in range(min(15, len(first_map))):
                for c in range(min(20, len(first_map[0]))):
                    tile = first_map[r][c]
                    if tile == 1:
                        color = theme["wall"]
                    else:
                        color = theme["floor1"] if (r+c) % 2 == 0 else theme["floor2"]
                    px = preview_x + c * (preview_size + preview_gap)
                    py = preview_y + r * (preview_size + preview_gap)
                    pygame.draw.rect(surface, color, (px, py, preview_size, preview_size))

            # Map name
            name_col = HUD_ACCENT if is_selected else LIGHT_GRAY
            name = self.font_small.render(pack["name"], True, name_col)
            surface.blit(name, name.get_rect(center=(card_x + card_w // 2, card_y + 20)))

            # Level count
            lvl_text = f"{len(pack['levels'])} Levels"
            lvl = self.font_tiny.render(lvl_text, True, (180, 180, 190) if is_selected else (100, 100, 110))
            surface.blit(lvl, lvl.get_rect(center=(card_x + card_w // 2, card_y + card_h - 16)))

        # Arrows
        arrow_y = card_y + card_h // 2
        if selected_idx > 0:
            arr = self.font_medium.render("<", True, HUD_ACCENT)
            surface.blit(arr, arr.get_rect(center=(start_x - 18, arrow_y)))
        if selected_idx < len(MAP_PACKS) - 1:
            arr = self.font_medium.render(">", True, HUD_ACCENT)
            surface.blit(arr, arr.get_rect(center=(start_x + total_w + 18, arrow_y)))

        # Back hint
        back = self.font_small.render("Press ESC to go back", True, (80, 80, 90))
        surface.blit(back, back.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))

    # ──────────────────────────────────────────────────────────────
    #   LAUNCHING SCREEN (4-sec cinematic transition)
    # ──────────────────────────────────────────────────────────────
    def draw_launching(self, surface, pack, progress):
        """Draw the cinematic launching screen with portal effect.

        Args:
            surface: pygame display surface
            pack: the selected map pack dict (name, theme, levels)
            progress: 0.0 to 1.0 representing launch progress
        """
        # Theme-tinted dark background
        theme = pack["theme"]
        style = theme.get("style", "space")
        if style == "lava":
            bg = (18, 6, 3)
            accent = (255, 100, 30)
            accent2 = (200, 60, 15)
            portal_col = (255, 80, 20)
        elif style == "jungle":
            bg = (6, 16, 6)
            accent = (80, 220, 90)
            accent2 = (50, 160, 60)
            portal_col = (60, 200, 80)
        else:  # space
            bg = (6, 6, 18)
            accent = (80, 160, 255)
            accent2 = (40, 100, 200)
            portal_col = (60, 140, 255)

        surface.fill(bg)

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # --- Animated portal ring effect ---
        ring_count = 6
        for i in range(ring_count):
            phase = (self.anim_timer * 0.03 + i * 0.5) % (math.pi * 2)
            # Rings expand outward over time
            base_r = 30 + i * 35
            pulse = math.sin(phase) * 8
            r = int(base_r + pulse + progress * 40)
            alpha = max(10, int(80 - i * 12 - progress * 30))
            ring_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            col = (*portal_col, alpha)
            pygame.draw.circle(ring_surf, col, (cx, cy - 30), r, 2)
            surface.blit(ring_surf, (0, 0))

        # --- Central portal glow ---
        glow_r = int(25 + 15 * math.sin(self.anim_timer * 0.08))
        glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
        glow_alpha = int(60 + 40 * math.sin(self.anim_timer * 0.06))
        pygame.draw.circle(glow_surf, (*portal_col, glow_alpha), (glow_r * 2, glow_r * 2), glow_r * 2)
        pygame.draw.circle(glow_surf, (*accent, glow_alpha // 2), (glow_r * 2, glow_r * 2), glow_r)
        surface.blit(glow_surf, (cx - glow_r * 2, cy - 30 - glow_r * 2))

        # --- Scanlines for atmosphere ---
        self._draw_scanlines(surface)

        # --- Particle trails spiraling around portal ---
        for i in range(15):
            angle = self.anim_timer * 0.04 + i * (math.pi * 2 / 15)
            dist = 60 + 80 * ((self.anim_timer * 0.01 + i * 0.1) % 1.0)
            px = cx + int(dist * math.cos(angle))
            py = cy - 30 + int(dist * math.sin(angle) * 0.6)
            sz = 1 + (i % 3)
            p_alpha = max(10, int(50 - dist * 0.2))
            ps = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*accent, p_alpha), (sz, sz), sz)
            surface.blit(ps, (px - sz, py - sz))

        # --- Map name title ---
        title_pulse = math.sin(self.anim_timer * 0.05) * 3
        # Shadow
        sh = self.font_large.render(pack["name"].upper(), True, (20, 20, 20))
        surface.blit(sh, sh.get_rect(center=(cx + 2, 100 + title_pulse + 2)))
        # Main
        title = self.font_large.render(pack["name"].upper(), True, accent)
        surface.blit(title, title.get_rect(center=(cx, 100 + title_pulse)))

        # --- Subtitle ---
        sub_text = f"{len(pack['levels'])} LEVELS  •  STEALTH ELIMINATION"
        sub = self.font_small.render(sub_text, True, accent2)
        surface.blit(sub, sub.get_rect(center=(cx, 148)))

        # --- "LAUNCHING..." text with animated dots ---
        dots = "." * (1 + (self.anim_timer // 20) % 3)
        launch_text = f"LAUNCHING{dots}"
        lt = self.font_medium.render(launch_text, True, accent)
        surface.blit(lt, lt.get_rect(center=(cx, SCREEN_HEIGHT - 120)))

        # --- Progress bar ---
        bar_w = 320
        bar_h = 8
        bar_x = cx - bar_w // 2
        bar_y = SCREEN_HEIGHT - 80

        # Bar background
        bar_bg = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, (40, 40, 50, 150), (0, 0, bar_w, bar_h), border_radius=4)
        surface.blit(bar_bg, (bar_x, bar_y))

        # Bar fill
        fill_w = max(2, int(bar_w * progress))
        bar_fill = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
        pygame.draw.rect(bar_fill, (*accent, 220), (0, 0, fill_w, bar_h), border_radius=4)
        surface.blit(bar_fill, (bar_x, bar_y))

        # Glow at leading edge
        if fill_w > 4:
            edge_glow = pygame.Surface((16, bar_h + 8), pygame.SRCALPHA)
            edge_alpha = int(120 + 80 * math.sin(self.anim_timer * 0.12))
            pygame.draw.rect(edge_glow, (*accent, edge_alpha), (0, 0, 16, bar_h + 8), border_radius=6)
            surface.blit(edge_glow, (bar_x + fill_w - 8, bar_y - 4))

        # --- Frame border ---
        self._draw_frame_border(surface)

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

        # ESC Leave hint (top-right)
        leave_panel = pygame.Surface((120, 24), pygame.SRCALPHA)
        pygame.draw.rect(leave_panel, (20, 20, 28, 180), (0, 0, 120, 24), border_radius=4)
        surface.blit(leave_panel, (SCREEN_WIDTH - 130, 10))
        leave_txt = self.font_small.render("ESC  Leave", True, (180, 100, 100))
        surface.blit(leave_txt, leave_txt.get_rect(center=(SCREEN_WIDTH - 70, 22)))

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
