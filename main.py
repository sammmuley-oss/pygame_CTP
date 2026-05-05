"""
main.py - Hunter Assassin Stealth Game
"""

import pygame
import sys
import time
import math

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    STATE_MENU, STATE_MAP_SELECT, STATE_PLAYING,
    STATE_GAME_OVER, STATE_LEVEL_CLEAR, STATE_WIN,
    BLACK, MAP_PACKS
)
from player import Player
from zombie import Guard
from map_manager import GameMap
from ui import UI
from sound_manager import SoundManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.sound = SoundManager()
        self.ui = UI()
        self.state = STATE_MENU
        self.running = True

        # Map pack selection
        self.selected_pack = 0
        self.active_pack = None  # set when game starts
        self.active_levels = []
        self.active_theme = None

        self.current_level = 0
        self.game_map = None
        self.player = None
        self.guards = []
        self.start_time = 0
        self.elapsed_time = 0
        self.total_time = 0

    def _init_level(self, level_idx):
        level_data = self.active_levels[level_idx]
        self.game_map = GameMap(level_data, theme=self.active_theme)
        spawn_col, spawn_row = self.game_map.player_spawn
        self.player = Player(spawn_col, spawn_row,
                             theme_style=self.active_theme.get("style", "space"))
        self.guards = []
        for gdef in level_data["guards"]:
            g = Guard(
                patrol_points=gdef["patrol"],
                speed=gdef["speed"],
                vision_dist=gdef.get("vision", None),
                theme_style=self.active_theme.get("style", "space")
            )
            self.guards.append(g)
        self.start_time = time.time()
        self.elapsed_time = 0

    def _start_game(self):
        """Start a game with the selected map pack."""
        pack = MAP_PACKS[self.selected_pack]
        self.active_pack = pack
        self.active_levels = pack["levels"]
        self.active_theme = pack["theme"]
        self.current_level = 0
        self.total_time = 0
        self.state = STATE_PLAYING
        self._init_level(0)

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key):
        # --- Menu ---
        if self.state == STATE_MENU:
            if key == pygame.K_ESCAPE:
                self.running = False
            elif key == pygame.K_RETURN:
                self.state = STATE_MAP_SELECT
                self.ui.anim_timer = 0
            return

        # --- Map Selection ---
        if self.state == STATE_MAP_SELECT:
            if key == pygame.K_ESCAPE:
                self.state = STATE_MENU
                self.ui.anim_timer = 0
            elif key == pygame.K_LEFT:
                self.selected_pack = max(0, self.selected_pack - 1)
            elif key == pygame.K_RIGHT:
                self.selected_pack = min(len(MAP_PACKS) - 1, self.selected_pack + 1)
            elif key == pygame.K_RETURN:
                self._start_game()
            return

        # --- Global escape ---
        if key == pygame.K_ESCAPE:
            self.running = False
            return

        # --- Game Over: retry same level ---
        if self.state == STATE_GAME_OVER and key == pygame.K_r:
            self.state = STATE_PLAYING
            self._init_level(self.current_level)
            return

        # --- Level Clear: next level or win ---
        if self.state == STATE_LEVEL_CLEAR and key == pygame.K_RETURN:
            self.current_level += 1
            if self.current_level >= len(self.active_levels):
                self.state = STATE_WIN
                self.ui.anim_timer = 0
            else:
                self.state = STATE_PLAYING
                self._init_level(self.current_level)
            return

        # --- Win screen: play again goes to map select ---
        if self.state == STATE_WIN and key == pygame.K_r:
            self.state = STATE_MAP_SELECT
            self.ui.anim_timer = 0
            return

    def _update(self):
        self.ui.update()
        if self.state != STATE_PLAYING:
            return
        self.elapsed_time = time.time() - self.start_time
        keys = pygame.key.get_pressed()
        dx, dy = self.player.handle_input(keys)
        self.player.move(dx, dy, self.game_map.walls)
        self.player.update()
        alive_guards = [g for g in self.guards if g.alive]
        for guard in alive_guards:
            guard.update(self.game_map.walls)
            if guard.can_see_player(self.player.x, self.player.y, self.game_map.walls):
                self.state = STATE_GAME_OVER
                self.player.alive = False
                self.ui.anim_timer = 0
                self.sound.play("lose")
                return
            if guard.get_rect().colliderect(self.player.get_rect()):
                if guard.is_player_behind(self.player.x, self.player.y):
                    kill_x, kill_y = guard.x, guard.y
                    guard.alive = False
                    self.player.kills += 1
                    self.sound.play("pickup")
                    # Alert nearest alive guard to investigate
                    self._alert_nearest_guard(kill_x, kill_y)
                else:
                    self.state = STATE_GAME_OVER
                    self.player.alive = False
                    self.ui.anim_timer = 0
                    self.sound.play("lose")
                    return
        if all(not g.alive for g in self.guards):
            self.total_time += self.elapsed_time
            self.state = STATE_LEVEL_CLEAR
            self.ui.anim_timer = 0
            self.sound.play("win")

    def _draw(self):
        self.screen.fill(BLACK)
        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen)
        elif self.state == STATE_MAP_SELECT:
            self.ui.draw_map_select(self.screen, self.selected_pack)
        elif self.state == STATE_PLAYING:
            self._draw_gameplay()
        elif self.state == STATE_GAME_OVER:
            self._draw_gameplay()
            self.ui.draw_game_over(self.screen, self.elapsed_time)
        elif self.state == STATE_LEVEL_CLEAR:
            self._draw_gameplay()
            self.ui.draw_level_clear(self.screen, self.current_level + 1, self.elapsed_time)
        elif self.state == STATE_WIN:
            self.ui.draw_win(self.screen, self.total_time, len(self.active_levels))
        pygame.display.flip()

    def _alert_nearest_guard(self, kx, ky):
        """Alert the nearest alive guard to investigate a kill position."""
        best = None
        best_dist = float('inf')
        for g in self.guards:
            if g.alive:
                d = math.sqrt((g.x - kx)**2 + (g.y - ky)**2)
                if d < best_dist:
                    best_dist = d
                    best = g
        if best:
            best.alert_to(kx, ky)

    def _draw_gameplay(self):
        self.game_map.draw(self.screen)
        layout = self.game_map.layout
        for g in self.guards:
            g.draw_vision(self.screen, layout)
        for g in self.guards:
            g.draw(self.screen)
        self.player.draw(self.screen)
        enemies_left = sum(1 for g in self.guards if g.alive)
        self.ui.draw_hud(self.screen, self.current_level + 1,
                         enemies_left, self.elapsed_time)


if __name__ == "__main__":
    game = Game()
    game.run()
