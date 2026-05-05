"""
zombie.py - Guard (Enemy) with Patrol AI & Vision Cone (themed visuals)
"""

import pygame
import math
import random
from settings import (
    GUARD_SIZE, GUARD_VISION_DIST, GUARD_VISION_ANGLE, GUARD_WAIT_FRAMES,
    GUARD_COLOR, GUARD_OUTLINE, VISION_COLOR, VISION_EDGE_COLOR,
    TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
)


def line_intersects_rect(x1, y1, x2, y2, rect):
    """Check if line segment (x1,y1)-(x2,y2) intersects a rect using clipping."""
    lines = [
        (rect.left, rect.top, rect.right, rect.top),
        (rect.right, rect.top, rect.right, rect.bottom),
        (rect.left, rect.bottom, rect.right, rect.bottom),
        (rect.left, rect.top, rect.left, rect.bottom),
    ]
    for lx1, ly1, lx2, ly2 in lines:
        if _segments_intersect(x1, y1, x2, y2, lx1, ly1, lx2, ly2):
            return True
    return False


def _segments_intersect(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    """Check if two line segments intersect."""
    def cross(ox, oy, ax, ay, bx, by):
        return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)

    d1 = cross(bx1, by1, bx2, by2, ax1, ay1)
    d2 = cross(bx1, by1, bx2, by2, ax2, ay2)
    d3 = cross(ax1, ay1, ax2, ay2, bx1, by1)
    d4 = cross(ax1, ay1, ax2, ay2, bx2, by2)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False


def has_line_of_sight(x1, y1, x2, y2, walls):
    """Check if there's a clear line between two points (no walls blocking)."""
    for w in walls:
        if line_intersects_rect(x1, y1, x2, y2, w):
            return False
    return True


class Guard:
    """Enemy guard with patrol path and vision cone."""

    def __init__(self, patrol_points, speed=1.5, vision_dist=None, theme_style="space"):
        self.patrol = [(c * TILE_SIZE + TILE_SIZE // 2,
                        r * TILE_SIZE + TILE_SIZE // 2) for c, r in patrol_points]
        self.patrol_idx = 0
        self.x, self.y = float(self.patrol[0][0]), float(self.patrol[0][1])
        self.base_speed = speed
        self.speed = speed
        self.size = GUARD_SIZE
        self.alive = True
        self.wait_timer = 0
        self.theme_style = theme_style

        self.vision_dist = vision_dist or GUARD_VISION_DIST
        self.vision_half_angle = math.radians(GUARD_VISION_ANGLE)

        tx, ty = self.patrol[1 % len(self.patrol)]
        self.angle = math.atan2(ty - self.y, tx - self.x)

        self.anim_timer = 0
        self.detected = False

        # --- Unpredictable movement state ---
        self.direction = 1
        self.stuck_timer = 0
        self.look_around_timer = 0
        self.look_around_target = 0.0
        self.look_phase = 0

        # --- Alert / investigate state ---
        self.alert_target = None   # (x, y) position to investigate
        self.alert_timer = 0       # frames remaining to investigate
        self.alert_speed = self.base_speed * 1.6  # faster when alerted

    def get_rect(self):
        half = self.size // 2
        return pygame.Rect(int(self.x) - half, int(self.y) - half, self.size, self.size)

    def _next_patrol_index(self):
        """Advance patrol index, occasionally reversing direction."""
        if random.random() < 0.15:
            self.direction *= -1
        self.patrol_idx = (self.patrol_idx + self.direction) % len(self.patrol)

    def _random_wait(self):
        """Return a randomized wait duration so guards don't pause identically."""
        base = GUARD_WAIT_FRAMES
        return random.randint(int(base * 0.4), int(base * 1.8))

    def _randomize_speed(self):
        """Vary speed slightly each patrol segment."""
        self.speed = self.base_speed * random.uniform(0.75, 1.3)

    def alert_to(self, tx, ty):
        """Alert this guard to investigate a position (e.g. a kill location)."""
        self.alert_target = (float(tx), float(ty))
        self.alert_timer = 180  # 3 seconds at 60fps
        self.wait_timer = 0
        self.look_around_timer = 0

    def _move_toward(self, tx, ty, spd, walls):
        """Move toward a target position with wall collision."""
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 3:
            return True  # arrived
        self.angle = math.atan2(dy, dx)
        mx = (dx / dist) * spd
        my = (dy / dist) * spd
        self.x += mx
        gr = self.get_rect()
        for w in walls:
            if gr.colliderect(w):
                if mx > 0: self.x = w.left - self.size // 2
                elif mx < 0: self.x = w.right + self.size // 2
        self.y += my
        gr = self.get_rect()
        for w in walls:
            if gr.colliderect(w):
                if my > 0: self.y = w.top - self.size // 2
                elif my < 0: self.y = w.bottom + self.size // 2
        return False

    def update(self, walls):
        """Move along patrol path with wall collision and unpredictable behavior."""
        if not self.alive:
            return

        self.anim_timer += 1
        self.detected = False

        # --- Alert / investigate mode ---
        if self.alert_target is not None:
            self.alert_timer -= 1
            arrived = self._move_toward(self.alert_target[0], self.alert_target[1],
                                        self.alert_speed, walls)
            if arrived or self.alert_timer <= 0:
                # Look around at the alert spot, then return to patrol
                self.alert_target = None
                self.look_around_target = self.angle + random.uniform(-math.pi, math.pi)
                self.look_around_timer = random.randint(30, 60)
                self.look_phase = 0
            return

        # --- Look-around behavior at waypoints ---
        if self.look_around_timer > 0:
            self.look_around_timer -= 1
            diff = math.atan2(math.sin(self.look_around_target - self.angle),
                              math.cos(self.look_around_target - self.angle))
            self.angle += diff * 0.1
            if self.look_around_timer <= 0:
                self.look_phase += 1
                if self.look_phase < 3:
                    self.look_around_target = self.angle + random.uniform(-math.pi, math.pi)
                    self.look_around_timer = random.randint(15, 35)
                else:
                    nx, ny = self.patrol[self.patrol_idx]
                    self.angle = math.atan2(ny - self.y, nx - self.x)
                    self.look_phase = 0
            return

        # --- Normal wait timer ---
        if self.wait_timer > 0:
            self.wait_timer -= 1
            if self.wait_timer <= 0 and random.random() < 0.35:
                self.look_around_target = self.angle + random.uniform(-2.0, 2.0)
                self.look_around_timer = random.randint(20, 40)
                self.look_phase = 0
            return

        tx, ty = self.patrol[self.patrol_idx]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 3:
            self._next_patrol_index()
            self.wait_timer = self._random_wait()
            self._randomize_speed()
            nx, ny = self.patrol[self.patrol_idx]
            self.angle = math.atan2(ny - self.y, nx - self.x)
            self.stuck_timer = 0
            return

        self.angle = math.atan2(dy, dx)
        mx = (dx / dist) * self.speed
        my = (dy / dist) * self.speed

        old_x, old_y = self.x, self.y

        self.x += mx
        gr = self.get_rect()
        for w in walls:
            if gr.colliderect(w):
                if mx > 0: self.x = w.left - self.size // 2
                elif mx < 0: self.x = w.right + self.size // 2

        self.y += my
        gr = self.get_rect()
        for w in walls:
            if gr.colliderect(w):
                if my > 0: self.y = w.top - self.size // 2
                elif my < 0: self.y = w.bottom + self.size // 2

        # --- Stuck detection ---
        moved = abs(self.x - old_x) + abs(self.y - old_y)
        if moved < 0.5:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0

        if self.stuck_timer > 30:
            self._next_patrol_index()
            nx, ny = self.patrol[self.patrol_idx]
            self.angle = math.atan2(ny - self.y, nx - self.x)
            self.stuck_timer = 0
            self.wait_timer = self._random_wait()
            self._randomize_speed()

    def can_see_player(self, px, py, walls):
        """Check if player is within vision cone and has line of sight."""
        if not self.alive:
            return False

        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > self.vision_dist:
            return False

        angle_to_player = math.atan2(dy, dx)
        angle_diff = abs(math.atan2(math.sin(angle_to_player - self.angle),
                                     math.cos(angle_to_player - self.angle)))
        if angle_diff > self.vision_half_angle:
            return False

        if not has_line_of_sight(self.x, self.y, px, py, walls):
            return False

        self.detected = True
        return True

    def is_player_behind(self, px, py):
        """Check if player is behind this guard (outside front vision cone)."""
        dx = px - self.x
        dy = py - self.y
        angle_to_player = math.atan2(dy, dx)
        angle_diff = abs(math.atan2(math.sin(angle_to_player - self.angle),
                                     math.cos(angle_to_player - self.angle)))
        return angle_diff > math.radians(100)

    def _cast_ray(self, cx, cy, angle, max_dist, walls):
        """Cast a single ray, return the endpoint where it hits a wall or max dist."""
        step = 4
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for d in range(step, int(max_dist) + step, step):
            if d > max_dist:
                d = max_dist
            rx = cx + cos_a * d
            ry = cy + sin_a * d
            # Check if this point is inside any wall
            tc = int(rx) // TILE_SIZE
            tr = int(ry) // TILE_SIZE
            if 0 <= tr < len(self._layout) and 0 <= tc < len(self._layout[0]):
                if self._layout[tr][tc] == 1:
                    # Back up to just before the wall
                    return (cx + cos_a * (d - step), cy + sin_a * (d - step))
            if d >= max_dist:
                break
        return (cx + cos_a * max_dist, cy + sin_a * max_dist)

    def draw_vision(self, surface, layout=None):
        """Draw raycasted vision cone that stops at walls."""
        if not self.alive:
            return

        self._layout = layout  # store for _cast_ray
        cx, cy = int(self.x), int(self.y)
        vd = self.vision_dist

        num_rays = 24
        points = [(cx, cy)]
        if layout is not None:
            for i in range(num_rays + 1):
                a = self.angle - self.vision_half_angle + \
                    (2 * self.vision_half_angle * i / num_rays)
                endpoint = self._cast_ray(cx, cy, a, vd, None)
                points.append((int(endpoint[0]), int(endpoint[1])))
        else:
            # Fallback: no layout, simple cone
            for i in range(num_rays + 1):
                a = self.angle - self.vision_half_angle + \
                    (2 * self.vision_half_angle * i / num_rays)
                points.append((cx + int(math.cos(a) * vd),
                               cy + int(math.sin(a) * vd)))

        if len(points) >= 3:
            cone_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            if self.theme_style == "jungle":
                color = (255, 100, 100, 35) if self.detected else (200, 255, 100, 22)
                edge_col = (255, 80, 80, 80) if self.detected else (150, 200, 50, 50)
            elif self.theme_style == "space":
                color = (255, 80, 80, 40) if self.detected else (80, 180, 255, 25)
                edge_col = (255, 60, 60, 90) if self.detected else (60, 150, 255, 60)
            else:
                color = (255, 100, 100, 35) if self.detected else VISION_COLOR
                edge_col = (255, 80, 80, 80) if self.detected else VISION_EDGE_COLOR
            pygame.draw.polygon(cone_surf, color, points)
            pygame.draw.line(cone_surf, edge_col, points[0], points[1], 1)
            pygame.draw.line(cone_surf, edge_col, points[0], points[-1], 1)
            surface.blit(cone_surf, (0, 0))

    def draw(self, surface):
        """Draw the guard with theme-appropriate visuals."""
        if not self.alive:
            return

        if self.theme_style == "space":
            self._draw_space(surface)
        elif self.theme_style == "jungle":
            self._draw_jungle(surface)
        else:
            self._draw_space(surface)

    # ================================================================
    #  SPACE STATION GUARD — Armored trooper with laser rifle
    # ================================================================
    def _draw_space(self, surface):
        half = self.size // 2
        gx, gy = int(self.x), int(self.y)
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        perp_x, perp_y = -sa, ca

        # Shadow
        s = pygame.Surface((self.size + 6, self.size + 6), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 45), (0, 0, self.size + 6, self.size + 6), border_radius=4)
        surface.blit(s, (gx - half - 1, gy - half + 2))

        # --- Laser rifle ---
        if self.detected:
            barrel_col = (255, 80, 80)
            barrel_glow = (255, 120, 120)
            muzzle_col = (255, 50, 50)
        else:
            barrel_col = (100, 160, 220)
            barrel_glow = (140, 200, 255)
            muzzle_col = (80, 180, 255)

        gun_ox = gx + int(perp_x * 5)
        gun_oy = gy + int(perp_y * 5)

        # Barrel
        barrel_len = half + 14
        bex = gun_ox + int(ca * barrel_len)
        bey = gun_oy + int(sa * barrel_len)
        bsx = gun_ox + int(ca * 2)
        bsy = gun_oy + int(sa * 2)
        pygame.draw.line(surface, (60, 65, 85), (bsx, bsy), (bex, bey), 5)
        pygame.draw.line(surface, barrel_col, (bsx, bsy), (bex, bey), 2)

        # Muzzle glow
        glow = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(glow, (muzzle_col[0], muzzle_col[1], muzzle_col[2], 80), (5, 5), 5)
        surface.blit(glow, (bex - 5, bey - 5))
        pygame.draw.circle(surface, muzzle_col, (bex, bey), 3)

        # Stock
        stock_len = half + 4
        stx = gun_ox - int(ca * stock_len)
        sty = gun_oy - int(sa * stock_len)
        pygame.draw.line(surface, (40, 45, 60), (gun_ox, gun_oy), (stx, sty), 5)
        pygame.draw.line(surface, (55, 60, 80), (gun_ox, gun_oy), (stx, sty), 3)

        # --- Body: armored space suit ---
        if self.detected:
            body_col = (255, 80, 80)
            body_out = (200, 50, 50)
        else:
            body_col = (55, 70, 100)
            body_out = (35, 45, 70)

        body = pygame.Rect(gx - half, gy - half, self.size, self.size)
        pygame.draw.rect(surface, body_col, body, border_radius=6)
        pygame.draw.rect(surface, body_out, body, width=2, border_radius=6)

        # Chest plate / armor lines
        plate_col = tuple(min(255, c + 20) for c in body_col)
        pygame.draw.line(surface, plate_col,
                         (gx - half + 4, gy), (gx + half - 4, gy), 2)
        pygame.draw.line(surface, plate_col,
                         (gx, gy - half + 4), (gx, gy + half - 4), 2)

        # Small power indicator on chest
        indicator = (80, 255, 120) if not self.detected else (255, 60, 60)
        pygame.draw.circle(surface, indicator, (gx - 4, gy - 4), 2)
        # Glow
        ind_glow = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(ind_glow, (indicator[0], indicator[1], indicator[2], 40), (4, 4), 4)
        surface.blit(ind_glow, (gx - 8, gy - 8))

        # --- Helmet: rounded with visor ---
        head_x = gx + int(ca * 2)
        head_y = gy + int(sa * 2)
        helmet_col = tuple(max(0, c - 15) for c in body_col)
        pygame.draw.circle(surface, helmet_col, (head_x, head_y), 9)
        pygame.draw.circle(surface, body_out, (head_x, head_y), 9, 1)

        # Visor (glowing slit)
        visor_len = 5
        v1x = head_x + int(perp_x * visor_len) + int(ca * 3)
        v1y = head_y + int(perp_y * visor_len) + int(sa * 3)
        v2x = head_x - int(perp_x * visor_len) + int(ca * 3)
        v2y = head_y - int(perp_y * visor_len) + int(sa * 3)
        visor_col = (80, 220, 255) if not self.detected else (255, 80, 80)
        pygame.draw.line(surface, visor_col, (v1x, v1y), (v2x, v2y), 3)
        # Visor glow
        vg = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(vg, (visor_col[0], visor_col[1], visor_col[2], 30), (7, 7), 7)
        surface.blit(vg, (head_x + int(ca * 3) - 7, head_y + int(sa * 3) - 7))

    # ================================================================
    #  JUNGLE GUARD — Camo militia with assault rifle
    # ================================================================
    def _draw_jungle(self, surface):
        half = self.size // 2
        gx, gy = int(self.x), int(self.y)
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        perp_x, perp_y = -sa, ca

        # Shadow
        s = pygame.Surface((self.size + 6, self.size + 6), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 50), (0, 0, self.size + 6, self.size + 6), border_radius=4)
        surface.blit(s, (gx - half - 1, gy - half + 2))

        # --- Assault rifle ---
        gun_dark = (50, 42, 30)
        gun_metal = (90, 85, 75)
        if self.detected:
            muzzle_col = (255, 200, 60)
        else:
            muzzle_col = (100, 95, 85)

        gun_ox = gx + int(perp_x * 5)
        gun_oy = gy + int(perp_y * 5)

        # Barrel
        barrel_len = half + 14
        bex = gun_ox + int(ca * barrel_len)
        bey = gun_oy + int(sa * barrel_len)
        bsx = gun_ox + int(ca * 2)
        bsy = gun_oy + int(sa * 2)
        pygame.draw.line(surface, gun_dark, (bsx, bsy), (bex, bey), 4)
        pygame.draw.line(surface, gun_metal, (bsx, bsy), (bex, bey), 2)

        # Muzzle
        pygame.draw.circle(surface, muzzle_col, (bex, bey), 3)

        # Wood stock
        stock_len = half + 4
        stx = gun_ox - int(ca * stock_len)
        sty = gun_oy - int(sa * stock_len)
        pygame.draw.line(surface, (75, 55, 30), (gun_ox, gun_oy), (stx, sty), 5)
        pygame.draw.line(surface, (95, 70, 40), (gun_ox, gun_oy), (stx, sty), 3)

        # --- Body: camo pattern ---
        if self.detected:
            camo_base = (200, 180, 50)
            camo_dark = (170, 150, 40)
            camo_light = (220, 200, 60)
            outline = (160, 140, 30)
        else:
            camo_base = (70, 85, 45)
            camo_dark = (50, 65, 30)
            camo_light = (90, 105, 55)
            outline = (40, 55, 25)

        body = pygame.Rect(gx - half, gy - half, self.size, self.size)
        pygame.draw.rect(surface, camo_base, body, border_radius=5)

        # Camo splotches
        camo_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        spots = [(5, 5), (15, 8), (8, 18), (20, 15), (12, 3), (22, 22),
                 (3, 14), (18, 24), (25, 8), (10, 25)]
        for sx, sy in spots:
            if sx < self.size and sy < self.size:
                col = camo_dark if random.random() < 0.5 else camo_light
                pygame.draw.circle(camo_surf, col, (sx, sy), random.randint(3, 5))
        surface.blit(camo_surf, (gx - half, gy - half))
        pygame.draw.rect(surface, outline, body, width=2, border_radius=5)

        # Belt
        belt_y = gy + 2
        pygame.draw.line(surface, (60, 50, 30),
                         (gx - half + 2, belt_y), (gx + half - 2, belt_y), 2)
        # Belt buckle
        pygame.draw.circle(surface, (140, 130, 80), (gx, belt_y), 2)

        # --- Beret / jungle hat ---
        head_x = gx + int(ca * 2)
        head_y = gy + int(sa * 2)

        if self.detected:
            hat_col = (180, 160, 40)
            skin_col = (200, 170, 130)
        else:
            hat_col = (55, 70, 35)
            skin_col = (160, 130, 100)

        # Face
        pygame.draw.circle(surface, skin_col, (head_x, head_y), 8)
        pygame.draw.circle(surface, tuple(max(0, c - 30) for c in skin_col),
                           (head_x, head_y), 8, 1)

        # Beret: flat-top circle offset forward
        beret_x = head_x + int(ca * 1)
        beret_y = head_y + int(sa * 1) - 3
        pygame.draw.ellipse(surface, hat_col,
                            (beret_x - 8, beret_y - 4, 16, 8))
        # Beret brim
        pygame.draw.ellipse(surface, tuple(max(0, c - 15) for c in hat_col),
                            (beret_x - 9, beret_y + 1, 18, 5))

        # --- Eyes ---
        eye_off = 3
        ex = int(ca * eye_off)
        ey = int(sa * eye_off)
        for side in (-3, 3):
            eye_x = head_x + int(perp_x * side) + ex
            eye_y = head_y + int(perp_y * side) + ey
            pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), 2)
            pupil_x = eye_x + int(ca * 1)
            pupil_y = eye_y + int(sa * 1)
            pygame.draw.circle(surface, (20, 20, 20), (pupil_x, pupil_y), 1)

        # Face paint streaks (two dark green lines)
        if not self.detected:
            for offset in (-2, 2):
                p1x = head_x + int(perp_x * 6) + int(ca * offset)
                p1y = head_y + int(perp_y * 6) + int(sa * offset)
                p2x = head_x - int(perp_x * 6) + int(ca * offset)
                p2y = head_y - int(perp_y * 6) + int(sa * offset)
                pygame.draw.line(surface, (35, 50, 25), (p1x, p1y), (p2x, p2y), 1)
