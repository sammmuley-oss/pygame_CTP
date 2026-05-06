"""
map_manager.py - Map Layout & Rendering (Space + Jungle + Lava themes)
"""

import pygame
import random
import math
from settings import (
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    TILE_WALL, TILE_PLAYER_SPAWN,
    WALL_COLOR, WALL_HIGHLIGHT, WALL_SHADOW,
    FLOOR_COLOR_1, FLOOR_COLOR_2
)


class GameMap:
    def __init__(self, level_data, theme=None):
        self.layout = [row[:] for row in level_data["map"]]
        self.walls = []
        self.player_spawn = (1, 1)

        self.wall_color = theme["wall"] if theme else WALL_COLOR
        self.wall_hi = theme["wall_hi"] if theme else WALL_HIGHLIGHT
        self.wall_sh = theme["wall_sh"] if theme else WALL_SHADOW
        self.floor1 = theme["floor1"] if theme else FLOOR_COLOR_1
        self.floor2 = theme["floor2"] if theme else FLOOR_COLOR_2
        self.style = theme.get("style", "space") if theme else "space"

        self._parse_map()
        random.seed(hash(str(self.layout)))
        self._build_surfaces()
        random.seed()

    def _parse_map(self):
        self.walls = []
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                tile = self.layout[r][c]
                if tile == TILE_WALL:
                    self.walls.append(pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif tile == TILE_PLAYER_SPAWN:
                    self.player_spawn = (c, r)

    def _build_surfaces(self):
        w, h = GRID_COLS * TILE_SIZE, GRID_ROWS * TILE_SIZE
        self.floor_surface = pygame.Surface((w, h))
        self.wall_surface = pygame.Surface((w, h), pygame.SRCALPHA)

        if self.style == "jungle":
            self._build_jungle(w, h)
        elif self.style == "lava":
            self._build_lava(w, h)
        else:
            self._build_space(w, h)

    # ================================================================
    #  SPACE STATION THEME
    # ================================================================
    def _build_space(self, w, h):
        """Deep-space floor with stars, nebula glow, and metallic walls."""
        # Fill with deep space
        self.floor_surface.fill((4, 4, 14))

        # Distant nebula clouds
        nebula_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        nebula_colors = [
            (40, 10, 60, 12), (10, 20, 60, 10), (60, 15, 30, 8),
            (20, 40, 70, 10), (50, 20, 50, 8),
        ]
        for _ in range(12):
            nx = random.randint(0, w)
            ny = random.randint(0, h)
            nr = random.randint(60, 180)
            col = random.choice(nebula_colors)
            for ring in range(5, 0, -1):
                a = max(2, col[3] - ring * 2)
                pygame.draw.circle(nebula_surf, (col[0], col[1], col[2], a),
                                   (nx, ny), nr * ring // 5)
        self.floor_surface.blit(nebula_surf, (0, 0))

        # Stars: multiple layers
        for _ in range(200):
            sx = random.randint(0, w-1)
            sy = random.randint(0, h-1)
            brightness = random.randint(60, 255)
            size = random.choices([1, 1, 1, 2], weights=[6, 3, 2, 1])[0]
            star_col = random.choice([
                (brightness, brightness, brightness),
                (brightness, brightness, int(brightness*0.8)),
                (int(brightness*0.8), int(brightness*0.9), brightness),
                (brightness, int(brightness*0.7), int(brightness*0.7)),
            ])
            if size == 1:
                self.floor_surface.set_at((sx, sy), star_col)
            else:
                pygame.draw.circle(self.floor_surface, star_col, (sx, sy), size)
                # Tiny glow for bright stars
                if brightness > 200:
                    glow = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (star_col[0], star_col[1], star_col[2], 30),
                                       (3, 3), 3)
                    self.floor_surface.blit(glow, (sx-3, sy-3))

        # Subtle floor grid overlay (space-station floor lines)
        grid_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                tile = self.layout[r][c] if r < len(self.layout) and c < len(self.layout[0]) else 1
                if tile != TILE_WALL:
                    px, py = c * TILE_SIZE, r * TILE_SIZE
                    # Faint grid lines
                    pygame.draw.rect(grid_surf, (30, 35, 55, 25),
                                     (px, py, TILE_SIZE, TILE_SIZE), 1)
                    # Corner dots
                    for dx, dy in [(2, 2), (TILE_SIZE-3, 2),
                                   (2, TILE_SIZE-3), (TILE_SIZE-3, TILE_SIZE-3)]:
                        pygame.draw.circle(grid_surf, (40, 50, 80, 40),
                                           (px + dx, py + dy), 1)
        self.floor_surface.blit(grid_surf, (0, 0))

        # --- Walls: metallic sci-fi panels ---
        for wr in self.walls:
            c = wr.left // TILE_SIZE
            r = wr.top // TILE_SIZE
            is_border = (r == 0 or r == GRID_ROWS-1 or c == 0 or c == GRID_COLS-1)

            if is_border:
                self._draw_space_border(wr)
            else:
                self._draw_space_panel(wr)

    def _draw_space_border(self, wr):
        """Thick hull plating for borders."""
        # Base plate
        pygame.draw.rect(self.wall_surface, (35, 40, 55), wr)
        # Riveted edges
        pygame.draw.rect(self.wall_surface, (55, 65, 85), wr, 2)
        # Inner shadow
        inner = wr.inflate(-4, -4)
        pygame.draw.rect(self.wall_surface, (25, 28, 40), inner, 1)
        # Rivet dots
        for corner in [(wr.left+5, wr.top+5), (wr.right-6, wr.top+5),
                        (wr.left+5, wr.bottom-6), (wr.right-6, wr.bottom-6)]:
            pygame.draw.circle(self.wall_surface, (70, 80, 100), corner, 2)
            pygame.draw.circle(self.wall_surface, (45, 50, 65), corner, 1)

    def _draw_space_panel(self, wr):
        """Interior tech panel / crate."""
        cx = wr.left + TILE_SIZE // 2
        cy = wr.top + TILE_SIZE // 2

        # Base panel
        panel_col = random.choice([
            (45, 50, 70), (50, 55, 75), (40, 48, 65),
        ])
        pygame.draw.rect(self.wall_surface, panel_col, wr, border_radius=3)

        # Highlight top + left
        pygame.draw.line(self.wall_surface, (75, 85, 115),
                         (wr.left+2, wr.top+1), (wr.right-2, wr.top+1), 1)
        pygame.draw.line(self.wall_surface, (70, 80, 105),
                         (wr.left+1, wr.top+2), (wr.left+1, wr.bottom-2), 1)
        # Shadow bottom + right
        pygame.draw.line(self.wall_surface, (20, 22, 35),
                         (wr.left+2, wr.bottom-2), (wr.right-2, wr.bottom-2), 1)
        pygame.draw.line(self.wall_surface, (22, 25, 38),
                         (wr.right-2, wr.top+2), (wr.right-2, wr.bottom-2), 1)

        # Center detail: glowing vent / screen
        detail_type = random.randint(0, 2)
        if detail_type == 0:
            # Glowing vent lines
            vent_col = random.choice([
                (60, 180, 220), (80, 200, 160), (200, 120, 60),
            ])
            for i in range(3):
                vy = cy - 6 + i * 6
                pygame.draw.line(self.wall_surface, vent_col,
                                 (cx - 8, vy), (cx + 8, vy), 1)
            # Vent glow
            glow = pygame.Surface((24, 18), pygame.SRCALPHA)
            pygame.draw.rect(glow, (vent_col[0], vent_col[1], vent_col[2], 20),
                             (0, 0, 24, 18), border_radius=4)
            self.wall_surface.blit(glow, (cx-12, cy-9))
        elif detail_type == 1:
            # Small indicator light
            light_col = random.choice([
                (80, 255, 120), (255, 80, 80), (80, 180, 255), (255, 200, 50),
            ])
            pygame.draw.circle(self.wall_surface, light_col, (cx, cy), 3)
            # Glow
            glow = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(glow, (light_col[0], light_col[1], light_col[2], 35),
                               (6, 6), 6)
            self.wall_surface.blit(glow, (cx-6, cy-6))
        else:
            # Cross-hatch panel texture
            for i in range(-2, 3):
                pygame.draw.line(self.wall_surface, (55, 60, 82),
                                 (cx - 10 + i*2, cy - 10),
                                 (cx + 10 + i*2, cy + 10), 1)

        # Outline
        pygame.draw.rect(self.wall_surface, (60, 68, 90), wr, 1, border_radius=3)

    # ================================================================
    #  JUNGLE THEME
    # ================================================================
    def _build_jungle(self, w, h):
        """Organic jungle with Oggy-style hedge lanes and trees."""
        # --- Ground ---
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                rv = random.randint(-5, 5)
                if (r+c) % 2 == 0:
                    base = tuple(max(0, min(255, x+rv)) for x in self.floor1)
                else:
                    base = tuple(max(0, min(255, x+rv)) for x in self.floor2)
                px, py = c*TILE_SIZE, r*TILE_SIZE
                pygame.draw.rect(self.floor_surface, base, (px, py, TILE_SIZE, TILE_SIZE))

                tile = self.layout[r][c] if r < len(self.layout) and c < len(self.layout[0]) else 1
                if tile != TILE_WALL:
                    # Grass tufts
                    for _ in range(random.randint(0, 3)):
                        gx = px + random.randint(2, TILE_SIZE-2)
                        gy = py + random.randint(2, TILE_SIZE-2)
                        grass_col = random.choice([
                            (40, 75, 30), (50, 85, 35), (35, 65, 28),
                            (55, 90, 40), (45, 70, 32),
                        ])
                        gl = random.randint(3, 7)
                        pygame.draw.line(self.floor_surface, grass_col,
                                         (gx, gy), (gx + random.randint(-2, 2), gy - gl), 1)
                    # Dirt patch
                    if random.random() < 0.12:
                        dx = px + random.randint(5, TILE_SIZE-5)
                        dy = py + random.randint(5, TILE_SIZE-5)
                        pygame.draw.circle(self.floor_surface,
                                           random.choice([(50,38,22),(55,42,25),(45,35,20)]),
                                           (dx, dy), random.randint(2, 4))
                    # Flower
                    if random.random() < 0.05:
                        fx = px + random.randint(5, TILE_SIZE-5)
                        fy = py + random.randint(5, TILE_SIZE-5)
                        pygame.draw.circle(self.floor_surface,
                                           random.choice([(200,180,50),(180,80,80),(160,120,200)]),
                                           (fx, fy), 2)

        # --- Determine hedge rows/cols for Oggy-style lanes ---
        # Find horizontal and vertical runs of walls for continuous hedges
        wall_set = set()
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.layout[r][c] == TILE_WALL:
                    wall_set.add((c, r))

        drawn = set()
        # Draw walls
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if (c, r) not in wall_set or (c, r) in drawn:
                    continue

                is_border = (r == 0 or r == GRID_ROWS-1 or c == 0 or c == GRID_COLS-1)
                wr = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                cx = wr.left + TILE_SIZE // 2
                cy = wr.top + TILE_SIZE // 2

                if is_border:
                    self._draw_jungle_border(wr, cx, cy)
                    drawn.add((c, r))
                    continue

                # Check for horizontal hedge run
                h_run = [(c, r)]
                nc = c + 1
                while nc < GRID_COLS and (nc, r) in wall_set and (nc, r) not in drawn:
                    h_run.append((nc, r))
                    nc += 1

                # Check for vertical hedge run
                v_run = [(c, r)]
                nr = r + 1
                while nr < GRID_ROWS and (c, nr) in wall_set and (c, nr) not in drawn:
                    v_run.append((c, nr))
                    nr += 1

                if len(h_run) >= 2:
                    # Draw as horizontal hedge lane
                    for tc, tr in h_run:
                        drawn.add((tc, tr))
                    self._draw_hedge_lane(h_run, "horizontal")
                elif len(v_run) >= 2:
                    # Draw as vertical hedge lane
                    for tc, tr in v_run:
                        drawn.add((tc, tr))
                    self._draw_hedge_lane(v_run, "vertical")
                else:
                    # Single tile: tree or bush
                    drawn.add((c, r))
                    if random.random() < 0.5:
                        self._draw_tree(wr, cx, cy)
                    else:
                        self._draw_single_bush(wr, cx, cy)

    def _draw_jungle_border(self, wr, cx, cy):
        """Dense treeline border."""
        pygame.draw.rect(self.wall_surface, (20, 45, 18), wr)
        for _ in range(5):
            ox = cx + random.randint(-10, 10)
            oy = cy + random.randint(-10, 10)
            r = random.randint(10, 16)
            col = random.choice([
                (25, 55, 20), (30, 60, 22), (22, 50, 18), (35, 65, 25),
            ])
            pygame.draw.circle(self.wall_surface, col, (ox, oy), r)
        for _ in range(2):
            pygame.draw.circle(self.wall_surface,
                               (45, 85, 35),
                               (cx + random.randint(-8, 8), cy + random.randint(-8, -2)),
                               random.randint(3, 5))

    def _draw_hedge_lane(self, tiles, direction):
        """Oggy-style cartoon hedge lane — smooth, rounded, bright green."""
        if direction == "horizontal":
            min_c = min(t[0] for t in tiles)
            max_c = max(t[0] for t in tiles)
            r = tiles[0][1]
            # Full hedge rectangle
            x1 = min_c * TILE_SIZE
            x2 = (max_c + 1) * TILE_SIZE
            y1 = r * TILE_SIZE
            lane_w = x2 - x1
            lane_h = TILE_SIZE
        else:
            min_r = min(t[1] for t in tiles)
            max_r = max(t[1] for t in tiles)
            c = tiles[0][0]
            x1 = c * TILE_SIZE
            y1 = min_r * TILE_SIZE
            lane_w = TILE_SIZE
            lane_h = (max_r - min_r + 1) * TILE_SIZE

        # Shadow underneath
        shadow = pygame.Surface((lane_w + 4, lane_h + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (10, 18, 8, 60), (0, 4, lane_w + 4, lane_h + 2),
                         border_radius=12)
        self.wall_surface.blit(shadow, (x1 - 2, y1 - 1))

        # Main hedge body — bright cartoon green
        hedge_body = (55, 140, 45)
        hedge_rect = pygame.Rect(x1, y1, lane_w, lane_h)
        pygame.draw.rect(self.wall_surface, hedge_body, hedge_rect, border_radius=10)

        # Darker green inner fill for depth
        inner = hedge_rect.inflate(-6, -6)
        pygame.draw.rect(self.wall_surface, (45, 120, 38), inner, border_radius=8)

        # Rounded bumps along the top/sides (cartoon hedge look)
        bump_col_light = (70, 165, 55)
        bump_col_mid = (58, 145, 48)
        bump_col_dark = (40, 110, 35)

        if direction == "horizontal":
            # Bumps along the top edge
            bump_x = x1 + 8
            while bump_x < x2 - 5:
                bw = random.randint(12, 20)
                bh = random.randint(6, 10)
                by = y1 - bh // 2
                col = random.choice([bump_col_light, bump_col_mid])
                pygame.draw.ellipse(self.wall_surface, col,
                                    (bump_x - bw//2, by, bw, bh + 4))
                bump_x += bw - 2
            # Bumps along the bottom
            bump_x = x1 + 12
            while bump_x < x2 - 5:
                bw = random.randint(10, 16)
                bh = random.randint(5, 8)
                by = y1 + lane_h - bh // 2 - 2
                pygame.draw.ellipse(self.wall_surface, bump_col_dark,
                                    (bump_x - bw//2, by, bw, bh + 2))
                bump_x += bw + 1
        else:
            # Bumps along left edge
            bump_y = y1 + 8
            while bump_y < y1 + lane_h - 5:
                bw = random.randint(6, 10)
                bh = random.randint(12, 20)
                bx = x1 - bw // 2
                col = random.choice([bump_col_light, bump_col_mid])
                pygame.draw.ellipse(self.wall_surface, col,
                                    (bx, bump_y - bh//2, bw + 4, bh))
                bump_y += bh - 2
            # Bumps along right edge
            bump_y = y1 + 12
            while bump_y < y1 + lane_h - 5:
                bw = random.randint(5, 8)
                bh = random.randint(10, 16)
                bx = x1 + lane_w - bw // 2 - 2
                pygame.draw.ellipse(self.wall_surface, bump_col_dark,
                                    (bx, bump_y - bh//2, bw + 2, bh))
                bump_y += bh + 1

        # Leaf detail spots
        for _ in range(len(tiles) * 3):
            lx = x1 + random.randint(4, lane_w - 4)
            ly = y1 + random.randint(4, lane_h - 4)
            leaf_col = random.choice([
                (65, 155, 50), (50, 130, 42), (72, 170, 58),
                (42, 115, 35), (60, 145, 48),
            ])
            pygame.draw.circle(self.wall_surface, leaf_col, (lx, ly),
                               random.randint(2, 4))

        # Outline
        pygame.draw.rect(self.wall_surface, (35, 90, 28), hedge_rect, 2,
                         border_radius=10)

    def _draw_tree(self, wr, cx, cy):
        """A tree with trunk and canopy."""
        # Shadow
        shadow = pygame.Surface((TILE_SIZE+4, TILE_SIZE+4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (10, 15, 8, 70),
                            (2, TILE_SIZE//2, TILE_SIZE, TILE_SIZE//2+2))
        self.wall_surface.blit(shadow, (wr.left-2, wr.top-2))

        # Trunk
        tw = random.randint(6, 10)
        trunk_col = random.choice([(70,50,30),(80,55,32),(65,45,28)])
        trunk_r = pygame.Rect(cx-tw//2, cy-2, tw, TILE_SIZE//2+6)
        pygame.draw.rect(self.wall_surface, trunk_col, trunk_r, border_radius=2)
        for i in range(2):
            by = trunk_r.top + random.randint(2, trunk_r.height-2)
            pygame.draw.line(self.wall_surface, tuple(max(0,x-15) for x in trunk_col),
                             (trunk_r.left+1, by), (trunk_r.right-1, by), 1)

        # Canopy
        greens = [(35,80,28),(45,95,35),(30,70,25),(50,100,38),(55,105,42)]
        for _ in range(random.randint(5, 7)):
            ox = cx + random.randint(-12, 12)
            oy = cy + random.randint(-14, -2)
            pygame.draw.circle(self.wall_surface, random.choice(greens),
                               (ox, oy), random.randint(8, 14))
        # Highlights
        for _ in range(2):
            pygame.draw.circle(self.wall_surface,
                               random.choice([(60,120,45),(70,130,50)]),
                               (cx+random.randint(-6,6), cy+random.randint(-12,-5)),
                               random.randint(3, 5))

    def _draw_single_bush(self, wr, cx, cy):
        """A single rounded cartoon bush."""
        # Shadow
        shadow = pygame.Surface((TILE_SIZE+2, TILE_SIZE+2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (10, 15, 8, 50),
                            (2, TILE_SIZE//3, TILE_SIZE-2, TILE_SIZE//2))
        self.wall_surface.blit(shadow, (wr.left-1, wr.top-1))

        # Main bush shape — bright green cartoon style
        main_col = (55, 140, 45)
        pygame.draw.ellipse(self.wall_surface, main_col,
                            (cx-16, cy-12, 32, 26))
        # Darker center
        pygame.draw.ellipse(self.wall_surface, (45, 120, 38),
                            (cx-10, cy-8, 20, 18))

        # Bumps
        for _ in range(4):
            bx = cx + random.randint(-10, 10)
            by = cy + random.randint(-10, 2)
            pygame.draw.circle(self.wall_surface,
                               random.choice([(65,155,50),(58,145,48),(70,160,55)]),
                               (bx, by), random.randint(4, 7))

        # Berry accents
        for _ in range(random.randint(0, 2)):
            bx = cx + random.randint(-8, 8)
            by = cy + random.randint(-6, 4)
            pygame.draw.circle(self.wall_surface,
                               random.choice([(180,60,60),(200,180,50),(220,140,60)]),
                               (bx, by), 2)

        # Outline
        pygame.draw.ellipse(self.wall_surface, (35, 90, 28),
                            (cx-16, cy-12, 32, 26), 2)

    def draw(self, surface):
        surface.blit(self.floor_surface, (0, 0))
        surface.blit(self.wall_surface, (0, 0))

    # ================================================================
    #  LAVA / NETHER THEME
    # ================================================================
    def _build_lava(self, w, h):
        """Volcanic nether floor with magma cracks and magma block walls."""
        # --- Ground: dark basalt with magma veins ---
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                rv = random.randint(-4, 4)
                if (r+c) % 2 == 0:
                    base = tuple(max(0, min(255, x+rv)) for x in self.floor1)
                else:
                    base = tuple(max(0, min(255, x+rv)) for x in self.floor2)
                px, py = c*TILE_SIZE, r*TILE_SIZE
                pygame.draw.rect(self.floor_surface, base, (px, py, TILE_SIZE, TILE_SIZE))

                tile = self.layout[r][c] if r < len(self.layout) and c < len(self.layout[0]) else 1
                if tile != TILE_WALL:
                    # Magma vein cracks on floor
                    if random.random() < 0.18:
                        vx = px + random.randint(4, TILE_SIZE-4)
                        vy = py + random.randint(4, TILE_SIZE-4)
                        vein_col = random.choice([
                            (160, 50, 10), (180, 70, 15), (140, 40, 8),
                            (200, 80, 20), (170, 60, 12),
                        ])
                        vl = random.randint(4, 10)
                        angle = random.uniform(-0.8, 0.8)
                        import math as _m
                        ex = vx + int(vl * _m.cos(angle))
                        ey = vy + int(vl * _m.sin(angle))
                        pygame.draw.line(self.floor_surface, vein_col,
                                         (vx, vy), (ex, ey), 1)

                    # Ember spark dots
                    if random.random() < 0.06:
                        ex = px + random.randint(3, TILE_SIZE-3)
                        ey = py + random.randint(3, TILE_SIZE-3)
                        pygame.draw.circle(self.floor_surface,
                                           random.choice([(255,140,30),(255,180,50),(220,100,20)]),
                                           (ex, ey), 1)

                    # Subtle basalt texture cracks
                    if random.random() < 0.10:
                        cx = px + random.randint(5, TILE_SIZE-5)
                        cy = py + random.randint(5, TILE_SIZE-5)
                        pygame.draw.circle(self.floor_surface,
                                           (25, 14, 10), (cx, cy), random.randint(1, 3))

        # Subtle floor grid overlay (basalt tile lines)
        grid_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                tile = self.layout[r][c] if r < len(self.layout) and c < len(self.layout[0]) else 1
                if tile != TILE_WALL:
                    px, py = c * TILE_SIZE, r * TILE_SIZE
                    pygame.draw.rect(grid_surf, (60, 30, 15, 18),
                                     (px, py, TILE_SIZE, TILE_SIZE), 1)
        self.floor_surface.blit(grid_surf, (0, 0))

        # --- Walls: magma blocks ---
        for wr in self.walls:
            c = wr.left // TILE_SIZE
            r = wr.top // TILE_SIZE
            is_border = (r == 0 or r == GRID_ROWS-1 or c == 0 or c == GRID_COLS-1)
            cx = wr.left + TILE_SIZE // 2
            cy = wr.top + TILE_SIZE // 2

            if is_border:
                self._draw_lava_border(wr, cx, cy)
            else:
                self._draw_magma_block(wr, cx, cy)

    def _draw_lava_border(self, wr, cx, cy):
        """Obsidian border plating with subtle magma glow."""
        # Dark basalt base
        pygame.draw.rect(self.wall_surface, (50, 28, 18), wr)
        # Edges
        pygame.draw.rect(self.wall_surface, (70, 40, 25), wr, 2)
        # Inner shadow
        inner = wr.inflate(-4, -4)
        pygame.draw.rect(self.wall_surface, (35, 18, 12), inner, 1)
        # Rivet-like magma dots at corners
        for corner in [(wr.left+5, wr.top+5), (wr.right-6, wr.top+5),
                        (wr.left+5, wr.bottom-6), (wr.right-6, wr.bottom-6)]:
            pygame.draw.circle(self.wall_surface, (180, 70, 20), corner, 2)
            pygame.draw.circle(self.wall_surface, (120, 45, 15), corner, 1)

    def _draw_magma_block(self, wr, cx, cy):
        """Lava block — bright molten flowing lava surface."""
        ts = TILE_SIZE

        # Bright orange lava base
        pygame.draw.rect(self.wall_surface, (220, 110, 15), wr)

        # Pixelated lava texture — mix of hot (yellow) and cool (deep orange) patches
        chunk = 5
        for py in range(0, ts, chunk):
            for px in range(0, ts, chunk):
                roll = random.random()
                if roll < 0.30:
                    # Hot bright yellow-orange
                    c = random.choice([
                        (255, 200, 50), (255, 180, 40), (255, 220, 70),
                        (250, 190, 45), (255, 210, 60),
                    ])
                elif roll < 0.65:
                    # Mid orange (main lava body)
                    c = random.choice([
                        (230, 120, 20), (240, 130, 25), (220, 110, 18),
                        (235, 125, 22), (225, 115, 20),
                    ])
                else:
                    # Darker orange (cooler lava spots)
                    c = random.choice([
                        (190, 80, 10), (200, 90, 15), (180, 75, 8),
                        (195, 85, 12), (185, 78, 10),
                    ])
                cw = min(chunk, ts - px)
                ch = min(chunk, ts - py)
                pygame.draw.rect(self.wall_surface,  c,
                                 (wr.left + px, wr.top + py, cw, ch))

        # Thin darker edge
        pygame.draw.rect(self.wall_surface, (160, 60, 5), wr, 1)

