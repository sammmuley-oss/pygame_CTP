"""
player.py - Stealth Assassin Player (themed visuals)
"""

import pygame
import math
from settings import (
    PLAYER_SPEED, PLAYER_SIZE, PLAYER_COLOR, PLAYER_OUTLINE,
    TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
)


class Player:
    def __init__(self, x, y, theme_style="space"):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.speed = PLAYER_SPEED
        self.alive = True
        self.size = PLAYER_SIZE
        self.facing_x = 0
        self.facing_y = 1
        self.facing_angle = math.pi / 2  # radians, down
        self.pulse_timer = 0
        self.kills = 0
        self.theme_style = theme_style

    def get_rect(self):
        half = self.size // 2
        return pygame.Rect(self.x - half, self.y - half, self.size, self.size)

    def handle_input(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:   dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:    dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:   dx += self.speed

        if dx != 0 and dy != 0:
            factor = self.speed / math.sqrt(dx * dx + dy * dy)
            dx *= factor
            dy *= factor

        if dx != 0 or dy != 0:
            self.facing_x = dx
            self.facing_y = dy
            self.facing_angle = math.atan2(dy, dx)

        return dx, dy

    def move(self, dx, dy, walls):
        if not self.alive:
            return False

        hit_wall = False

        self.x += dx
        pr = self.get_rect()
        for w in walls:
            if pr.colliderect(w):
                if dx > 0: self.x = w.left - self.size // 2
                elif dx < 0: self.x = w.right + self.size // 2
                hit_wall = True

        self.y += dy
        pr = self.get_rect()
        for w in walls:
            if pr.colliderect(w):
                if dy > 0: self.y = w.top - self.size // 2
                elif dy < 0: self.y = w.bottom + self.size // 2
                hit_wall = True

        half = self.size // 2
        self.x = max(half, min(SCREEN_WIDTH - half, self.x))
        self.y = max(half, min(SCREEN_HEIGHT - half, self.y))

        return hit_wall

    def update(self):
        self.pulse_timer += 1

    def draw(self, surface):
        if not self.alive:
            return

        if self.theme_style == "space":
            self._draw_space(surface)
        elif self.theme_style == "jungle":
            self._draw_jungle(surface)
        elif self.theme_style == "lava":
            self._draw_lava(surface)
        else:
            self._draw_space(surface)

    # ================================================================
    #  SPACE PLAYER — Stealth agent with energy blade
    # ================================================================
    def _draw_space(self, surface):
        half = self.size // 2
        px, py = int(self.x), int(self.y)
        ca = math.cos(self.facing_angle)
        sa = math.sin(self.facing_angle)
        perp_x, perp_y = -sa, ca

        # Shadow
        s = pygame.Surface((self.size + 4, self.size + 4), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 50), (0, 0, self.size + 4, self.size + 4), border_radius=6)
        surface.blit(s, (px - half + 1, py - half + 3))

        # --- Energy blade ---
        blade_ox = px + int(perp_x * 4)
        blade_oy = py + int(perp_y * 4)

        # Handle
        h_sx = blade_ox - int(ca * 4)
        h_sy = blade_oy - int(sa * 4)
        h_ex = blade_ox + int(ca * 4)
        h_ey = blade_oy + int(sa * 4)
        pygame.draw.line(surface, (50, 55, 70), (h_sx, h_sy), (h_ex, h_ey), 5)
        pygame.draw.line(surface, (80, 90, 110), (h_sx, h_sy), (h_ex, h_ey), 3)

        # Crossguard
        g_len = 4
        gx1 = h_ex + int(perp_x * g_len)
        gy1 = h_ey + int(perp_y * g_len)
        gx2 = h_ex - int(perp_x * g_len)
        gy2 = h_ey - int(perp_y * g_len)
        pygame.draw.line(surface, (100, 180, 255), (gx1, gy1), (gx2, gy2), 3)

        # Energy blade (glowing cyan)
        blade_len = half + 12
        tip_x = blade_ox + int(ca * blade_len)
        tip_y = blade_oy + int(sa * blade_len)
        # Glow
        glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(glow, (30, 180, 255, 30), (h_ex, h_ey), (tip_x, tip_y), 7)
        surface.blit(glow, (0, 0))
        # Core blade
        pulse = math.sin(self.pulse_timer * 0.15) * 20
        blade_col = (int(80 + pulse), int(210 + pulse * 0.5), 255)
        pygame.draw.line(surface, blade_col, (h_ex, h_ey), (tip_x, tip_y), 3)
        pygame.draw.line(surface, (200, 240, 255), (h_ex, h_ey), (tip_x, tip_y), 1)
        pygame.draw.circle(surface, (200, 240, 255), (tip_x, tip_y), 2)

        # --- Body: stealth suit ---
        body_col = (30, 140, 200)
        body_out = (20, 100, 160)
        pulse_v = math.sin(self.pulse_timer * 0.08) * 8
        suit_col = (int(body_col[0] + pulse_v), int(body_col[1] + pulse_v), body_col[2])
        suit_col = tuple(max(0, min(255, c)) for c in suit_col)

        body = pygame.Rect(px - half, py - half, self.size, self.size)
        pygame.draw.rect(surface, suit_col, body, border_radius=6)
        pygame.draw.rect(surface, body_out, body, width=2, border_radius=6)

        # Circuit lines on suit
        circuit_col = (60, 200, 255, 80)
        cs = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.line(cs, circuit_col, (half, 3), (half, self.size - 3), 1)
        pygame.draw.line(cs, circuit_col, (3, half), (self.size - 3, half), 1)
        # Small circuit nodes
        for cx_off, cy_off in [(half-5, half-5), (half+5, half+5),
                                (half-5, half+5), (half+5, half-5)]:
            pygame.draw.circle(cs, (80, 220, 255, 100), (cx_off, cy_off), 2)
        surface.blit(cs, (px - half, py - half))

        # --- Helmet with visor ---
        head_x = px + int(ca * 2)
        head_y = py + int(sa * 2)
        helmet_col = (25, 120, 180)
        pygame.draw.circle(surface, helmet_col, (head_x, head_y), 9)
        pygame.draw.circle(surface, body_out, (head_x, head_y), 9, 1)

        # Visor (cyan glow)
        v_len = 5
        v1x = head_x + int(perp_x * v_len) + int(ca * 3)
        v1y = head_y + int(perp_y * v_len) + int(sa * 3)
        v2x = head_x - int(perp_x * v_len) + int(ca * 3)
        v2y = head_y - int(perp_y * v_len) + int(sa * 3)
        visor_pulse = int(math.sin(self.pulse_timer * 0.1) * 30)
        visor_col = (80, min(255, 230 + visor_pulse), 255)
        pygame.draw.line(surface, visor_col, (v1x, v1y), (v2x, v2y), 3)
        vg = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(vg, (visor_col[0], visor_col[1], visor_col[2], 35), (7, 7), 7)
        surface.blit(vg, (head_x + int(ca * 3) - 7, head_y + int(sa * 3) - 7))

    # ================================================================
    #  JUNGLE PLAYER — Stealthy hunter with machete
    # ================================================================
    def _draw_jungle(self, surface):
        half = self.size // 2
        px, py = int(self.x), int(self.y)
        ca = math.cos(self.facing_angle)
        sa = math.sin(self.facing_angle)
        perp_x, perp_y = -sa, ca

        # Shadow
        s = pygame.Surface((self.size + 4, self.size + 4), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 55), (0, 0, self.size + 4, self.size + 4), border_radius=6)
        surface.blit(s, (px - half + 1, py - half + 3))

        # --- Machete ---
        knife_ox = px + int(perp_x * 4)
        knife_oy = py + int(perp_y * 4)

        # Wood handle
        h_sx = knife_ox - int(ca * 5)
        h_sy = knife_oy - int(sa * 5)
        h_ex = knife_ox + int(ca * 4)
        h_ey = knife_oy + int(sa * 4)
        pygame.draw.line(surface, (55, 35, 15), (h_sx, h_sy), (h_ex, h_ey), 5)
        pygame.draw.line(surface, (90, 60, 30), (h_sx, h_sy), (h_ex, h_ey), 3)
        # Leather wrap marks
        for i in range(3):
            wx = int(h_sx + (h_ex - h_sx) * (i * 0.3 + 0.1))
            wy = int(h_sy + (h_ey - h_sy) * (i * 0.3 + 0.1))
            pygame.draw.circle(surface, (70, 45, 20), (wx, wy), 1)

        # Crossguard (brass)
        g_len = 3
        gx1 = h_ex + int(perp_x * g_len)
        gy1 = h_ey + int(perp_y * g_len)
        gx2 = h_ex - int(perp_x * g_len)
        gy2 = h_ey - int(perp_y * g_len)
        pygame.draw.line(surface, (140, 120, 60), (gx1, gy1), (gx2, gy2), 3)

        # Machete blade (wider, slight curve feel)
        blade_len = half + 14
        tip_x = knife_ox + int(ca * blade_len)
        tip_y = knife_oy + int(sa * blade_len)
        pygame.draw.line(surface, (180, 185, 190), (h_ex, h_ey), (tip_x, tip_y), 4)
        pygame.draw.line(surface, (220, 225, 230), (h_ex, h_ey), (tip_x, tip_y), 2)
        # Edge highlight
        pygame.draw.line(surface, (240, 245, 250),
                         (h_ex + int(perp_x), h_ey + int(perp_y)),
                         (tip_x, tip_y), 1)
        pygame.draw.circle(surface, WHITE, (tip_x, tip_y), 1)

        # --- Body: dark green stealth gear ---
        body_col = (40, 110, 55)
        body_out = (25, 75, 35)
        pulse_v = math.sin(self.pulse_timer * 0.08) * 5
        gear_col = (int(body_col[0] + pulse_v), int(body_col[1] + pulse_v), int(body_col[2] + pulse_v))
        gear_col = tuple(max(0, min(255, c)) for c in gear_col)

        body = pygame.Rect(px - half, py - half, self.size, self.size)
        pygame.draw.rect(surface, gear_col, body, border_radius=6)
        pygame.draw.rect(surface, body_out, body, width=2, border_radius=6)

        # Vest straps
        strap_col = (30, 80, 40)
        pygame.draw.line(surface, strap_col,
                         (px - half + 4, py - half + 4),
                         (px + half - 4, py + half - 4), 2)
        pygame.draw.line(surface, strap_col,
                         (px + half - 4, py - half + 4),
                         (px - half + 4, py + half - 4), 2)

        # Utility belt
        pygame.draw.line(surface, (70, 55, 30),
                         (px - half + 3, py + 2), (px + half - 3, py + 2), 2)
        pygame.draw.circle(surface, (120, 100, 50), (px, py + 2), 2)  # buckle

        # --- Head: bandana + face ---
        head_x = px + int(ca * 2)
        head_y = py + int(sa * 2)

        # Skin
        skin_col = (180, 145, 110)
        pygame.draw.circle(surface, skin_col, (head_x, head_y), 8)
        pygame.draw.circle(surface, (140, 110, 80), (head_x, head_y), 8, 1)

        # Bandana (dark green, wraps around forehead)
        band_x = head_x - int(ca * 1)
        band_y = head_y - int(sa * 1) - 2
        pygame.draw.ellipse(surface, (30, 80, 35),
                            (band_x - 8, band_y - 3, 16, 6))
        # Bandana tail
        tail_x = head_x - int(ca * 6) - int(perp_x * 3)
        tail_y = head_y - int(sa * 6) - int(perp_y * 3)
        pygame.draw.line(surface, (30, 80, 35),
                         (band_x - 6, band_y), (tail_x, tail_y), 2)

        # Eyes
        eye_off = 3
        ex = int(ca * eye_off)
        ey = int(sa * eye_off)
        for side in (-3, 3):
            eye_x = head_x + int(perp_x * side) + ex
            eye_y = head_y + int(perp_y * side) + ey
            pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 2)
            pupil_x = eye_x + int(ca * 1)
            pupil_y = eye_y + int(sa * 1)
            pygame.draw.circle(surface, (15, 15, 25), (pupil_x, pupil_y), 1)

    # ================================================================
    #  LAVA / NETHER PLAYER — Molten flame warrior (bright, distinct)
    # ================================================================
    def _draw_lava(self, surface):
        half = self.size // 2
        px, py = int(self.x), int(self.y)
        ca = math.cos(self.facing_angle)
        sa = math.sin(self.facing_angle)
        perp_x, perp_y = -sa, ca

        # Flame aura glow behind the player
        aura_pulse = math.sin(self.pulse_timer * 0.1) * 3
        aura_size = int(self.size + 10 + aura_pulse)
        aura = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura, (255, 120, 20, 18), (aura_size, aura_size), aura_size)
        pygame.draw.circle(aura, (255, 180, 40, 12), (aura_size, aura_size), aura_size - 5)
        surface.blit(aura, (px - aura_size, py - aura_size))

        # Shadow
        s = pygame.Surface((self.size + 4, self.size + 4), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 50), (0, 0, self.size + 4, self.size + 4), border_radius=6)
        surface.blit(s, (px - half + 1, py - half + 3))

        # --- Fire blade (golden bright) ---
        blade_ox = px + int(perp_x * 4)
        blade_oy = py + int(perp_y * 4)

        # Golden handle
        h_sx = blade_ox - int(ca * 5)
        h_sy = blade_oy - int(sa * 5)
        h_ex = blade_ox + int(ca * 4)
        h_ey = blade_oy + int(sa * 4)
        pygame.draw.line(surface, (140, 100, 30), (h_sx, h_sy), (h_ex, h_ey), 5)
        pygame.draw.line(surface, (200, 160, 50), (h_sx, h_sy), (h_ex, h_ey), 3)

        # Crossguard (bright gold)
        g_len = 4
        gx1 = h_ex + int(perp_x * g_len)
        gy1 = h_ey + int(perp_y * g_len)
        gx2 = h_ex - int(perp_x * g_len)
        gy2 = h_ey - int(perp_y * g_len)
        pygame.draw.line(surface, (255, 220, 80), (gx1, gy1), (gx2, gy2), 3)

        # Fire blade (bright yellow-white)
        blade_len = half + 12
        tip_x = blade_ox + int(ca * blade_len)
        tip_y = blade_oy + int(sa * blade_len)
        # Glow
        glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(glow, (255, 200, 50, 35), (h_ex, h_ey), (tip_x, tip_y), 9)
        surface.blit(glow, (0, 0))
        # Core blade
        pulse = math.sin(self.pulse_timer * 0.15) * 20
        blade_col = (255, int(min(255, 220 + pulse)), int(max(50, 80 + pulse)))
        pygame.draw.line(surface, blade_col, (h_ex, h_ey), (tip_x, tip_y), 3)
        pygame.draw.line(surface, (255, 255, 200), (h_ex, h_ey), (tip_x, tip_y), 1)
        pygame.draw.circle(surface, (255, 255, 200), (tip_x, tip_y), 2)

        # --- Body: bright molten orange armor ---
        pulse_v = math.sin(self.pulse_timer * 0.08) * 10
        body_r = int(max(0, min(255, 210 + pulse_v)))
        body_g = int(max(0, min(255, 110 + pulse_v * 0.6)))
        body_b = 25
        body_col = (body_r, body_g, body_b)
        body_out = (170, 75, 15)

        body = pygame.Rect(px - half, py - half, self.size, self.size)
        pygame.draw.rect(surface, body_col, body, border_radius=6)
        pygame.draw.rect(surface, body_out, body, width=2, border_radius=6)

        # Bright flame vein lines on suit
        vein_col = (255, 200, 60, 80)
        cs = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.line(cs, vein_col, (half, 3), (half, self.size - 3), 1)
        pygame.draw.line(cs, vein_col, (3, half), (self.size - 3, half), 1)
        # Bright ember nodes
        for cx_off, cy_off in [(half-5, half-5), (half+5, half+5),
                                (half-5, half+5), (half+5, half-5)]:
            pygame.draw.circle(cs, (255, 230, 80, 120), (cx_off, cy_off), 2)
        surface.blit(cs, (px - half, py - half))

        # --- Head: flame crown ---
        head_x = px + int(ca * 2)
        head_y = py + int(sa * 2)

        # Bright amber face
        skin_col = (230, 170, 80)
        pygame.draw.circle(surface, skin_col, (head_x, head_y), 8)
        pygame.draw.circle(surface, (180, 120, 50), (head_x, head_y), 8, 1)

        # Flame crown spikes (3 small triangles on top)
        crown_base_y = head_y - 6
        for offset in (-4, 0, 4):
            spike_x = head_x + offset
            tip_spike_y = crown_base_y - 5 - abs(offset) // 2
            # Flame color
            f_pulse = int(math.sin(self.pulse_timer * 0.15 + offset) * 20)
            flame_col = (255, min(255, 180 + f_pulse), max(0, 30 + f_pulse))
            pts = [(spike_x - 2, crown_base_y), (spike_x + 2, crown_base_y),
                   (spike_x, tip_spike_y)]
            pygame.draw.polygon(surface, flame_col, pts)

        # Glowing yellow eyes
        eye_off = 3
        ex = int(ca * eye_off)
        ey = int(sa * eye_off)
        for side in (-3, 3):
            eye_x = head_x + int(perp_x * side) + ex
            eye_y = head_y + int(perp_y * side) + ey
            pygame.draw.circle(surface, (255, 240, 100), (eye_x, eye_y), 2)
            pygame.draw.circle(surface, (255, 180, 30), (eye_x, eye_y), 1)

