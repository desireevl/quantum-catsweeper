from enum import Enum
from functools import partial

import qcatsweeper.quantum_logic as ql
import math
import random
import pyxel


class GameState(Enum):
    INTRO = 0
    HELP = 1
    PLAYING_REAL = 2
    PLAYING_SIMULATED = 3
    LOST = 4
    COMPUTING = 42


def is_within(x, y, pos):
    x1, y1, x2, y2 = pos
    return x >= x1 and x <= x2 and y >= y1 and y <= y2


class QuantumCatsweeperApp:
    def __init__(self, width=153, height=170):
        # Initialize game state
        self.game_state = GameState.INTRO

        self._main_cat_asset = 0

        self._main_bg = 1
        self._PLAYING_REAL_bg = 2
        self._bomb_explode_sound = 3

        self._width = width
        self._height = height

        self._grid_size = 12
        self._grid_start_x = 5
        self._grid_start_y = 22
        self._grid_draw_size = 12

        self.game_grid = []
        self.elapsed_frames = 0
        self.clicked_tiles = {}
        self.clicked_group_times = {}
        self.reveal_groups = {}

        self._play_real_button_pos = self.pyxel_button_centered(
            'Play (Real)     ', 100)
        self._play_simulated_button_pos = self.pyxel_button_centered(
            'Play (Simulated)', 115)
        self._help_button_pos = self.pyxel_button_centered(
            '      Help      ', 130)
        self._help_back_button_pos = self.pyxel_button_centered('Back', 135)
        self._PLAYING_REAL_back_buttom_pos = self.pyxel_button('Back', 5, 5)

        pyxel.init(self._width, self._height, caption='Quantum Catsweeper')

        pyxel.image(self._main_cat_asset).load(0, 0, 'assets/cat_16x16.png')

        # Sound
        pyxel.sound(self._main_bg).set(
            'e2e2c2g1 g1g1c2e2 d2d2d2g2 g2g2rr'
            'c2c2a1e1 e1e1a1c2 b1b1b1e2 e2e2rr', 'p', '6',
            'vffn fnff vffs vfnn', 25)
        pyxel.sound(self._PLAYING_REAL_bg).set(
            'f0c1f0c1 g0d1g0d1 c1g1c1g1 a0e1a0e1'
            'f0c1f0c1 f0c1f0c1 g0d1g0d1 g0d1g0d1', 't', '7', 'n', 25)
        pyxel.play(self._main_bg, [0, 1], loop=True)

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.game_state == GameState.INTRO:
            self.handle_intro_events()

        elif self.game_state == GameState.HELP:
            self.handle_help_events()

        elif self.game_state == GameState.PLAYING_REAL:
            self.handle_PLAYING_REAL_events()

    def draw(self):
        self.clear_assets()

        if self.game_state == GameState.INTRO:
            self.draw_introscreen()

        elif self.game_state == GameState.HELP:
            self.draw_helpscreen()

        elif self.game_state == GameState.PLAYING_REAL:
            self.draw_playscreen()

    def clear_assets(self):
        pyxel.cls(self._main_cat_asset)

    #### Event handlers ####

    def handle_PLAYING_REAL_events(self):
        if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
            mouse_within = partial(is_within, pyxel.mouse_x, pyxel.mouse_y)

            if mouse_within(self._PLAYING_REAL_back_buttom_pos):
                self.game_state = GameState.INTRO
                pyxel.stop(self._PLAYING_REAL_bg)
                pyxel.play(self._main_bg, [0, 1], loop=True)

            # If user is clicking
            if pyxel.mouse_x > self._grid_start_x and pyxel.mouse_y > self._grid_start_y:
                row, col = self.get_grid_row_col_from_xy(
                    pyxel.mouse_x, pyxel.mouse_y)

                clicked_tile = self.game_grid[row][col]

                if ((row, col) not in self.clicked_tiles):                    
                    self.clicked_tiles[(row, col)] = True

                    if clicked_tile is ql.TileItems.BLANKS:                    
                        return

                    if clicked_tile not in self.clicked_group_times:
                        self.clicked_group_times[clicked_tile] = 0
                    self.clicked_group_times[clicked_tile] += 1

                    # Call quantum computer to see if we reveal of nah
                    reveal_state = ql.onclick(clicked_tile, self.clicked_group_times[clicked_tile])

                    if reveal_state is None:
                        return
                    
                    if reveal_state is ql.TileItems.REVEAL_GROUP:
                        print('reveal')
                        self.reveal_groups[clicked_tile] = ql.TileItems.REVEAL_GROUP
                    
                    # TODO: What do when bomb explodes
                    if reveal_state is ql.TileItems.BOMB_EXPLODED:
                        print('game loss')
                        return
                    
                    # When bomb doesn't explode it turns into blank
                    if reveal_state is ql.TileItems.BOMB_UNEXPLODED:
                        self.game_grid[row][col] = ql.TileItems.BLANKS

    def handle_help_events(self):
        if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
            mouse_within = partial(is_within, pyxel.mouse_x, pyxel.mouse_y)

            if mouse_within(self._help_back_button_pos):
                self.game_state = GameState.INTRO

    def handle_intro_events(self):
        if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
            mouse_within = partial(is_within, pyxel.mouse_x, pyxel.mouse_y)

            if mouse_within(self._play_real_button_pos):
                self.reset_game()
                self.game_state = GameState.PLAYING_REAL

                pyxel.stop(self._main_bg)
                pyxel.play(self._PLAYING_REAL_bg, [2, 3], loop=True)

            if mouse_within(self._help_button_pos):
                self.game_state = GameState.HELP

    #### Screen Drawing ####

    def draw_grid(self):
        for row in range(len(self.game_grid)):
            for col in range(len(self.game_grid[row])):
                _x, _y = self.get_grid_xy_from_row_col(col, row)
                
                pyxel.rect(_x, _y, _x + self._grid_draw_size -
                           2, _y - 2 + self._grid_draw_size, 5)

                cur_tile = self.game_grid[row][col]

                if self.clicked_tiles.get((row, col), -1) == True or \
                    self.reveal_groups.get(cur_tile) == ql.TileItems.REVEAL_GROUP:
                    pyxel.text(_x + 2, _y + 2,
                               str(abs(self.game_grid[row][col].value)), 3)

    def draw_playscreen(self):
        self.pyxel_button('Back', 5, 5)

        self.draw_grid()

        # Top bar stuff
        pyxel.text(50, 8, 'CATSWEEPER 9000', 7)

        # Convert text to "00:00" format
        display_mins = int(self.elapsed_frames / (60 * 30))  # 30 FPS
        display_mins = '0' + \
            str(display_mins) if display_mins < 10 else str(display_mins)
        display_sec = int(self.elapsed_frames / 30 % 60)
        display_sec = '0' + \
            str(display_sec) if display_sec < 10 else str(display_sec)
        pyxel.text(125, 8, '{}:{}'.format(display_mins, display_sec), 8)

        self.elapsed_frames = self.elapsed_frames + 1

    def draw_helpscreen(self):
        self.pyxel_text_centered(20, 'HELP', pyxel.frame_count % 16)
        # TODO: Information
        self.pyxel_text_centered(30, 'Don\'t explode the cats!', 7)
        self.pyxel_text_centered(40, 'Numbers indicate number of', 7)
        self.pyxel_text_centered(50, 'unearthed tiles needed to', 7)
        self.pyxel_text_centered(50, 'reveal the group of numbers', 7)
        self.pyxel_button_centered('Back', 135)

    def draw_introscreen(self):
        # Draw Intro Text
        self.pyxel_text_centered(42, 'QUANTUM', pyxel.frame_count % 16)
        self.pyxel_text_centered(52, 'CATSWEEPER', pyxel.frame_count % 16)

        # Draw Quantum Cat
        cat_x = math.floor(self._width / 2) - 8
        cat_offset = math.sin(pyxel.frame_count * 0.1) * 2
        cat_flip = 1 if cat_offset >= 0 else -1
        pyxel.blt(cat_x + cat_offset, 62, self._main_cat_asset,
                  0, 0, 16 * cat_flip, 16, 5)

        # Draw button
        self.pyxel_button_centered('Play (Real)     ', 100)
        self.pyxel_button_centered('Play (Simulated)', 115)
        self.pyxel_button_centered('      Help      ', 130)

    #### Pyxel Function Wrappers ####

    def pyxel_text_centered(self, y, t, col=None):
        # Font is 4 pixels width
        offset = math.ceil(len(t) * 4 / 2)
        x = math.floor(self._width / 2) - offset
        pyxel.text(x, y, t, col)

    def pyxel_blt_centered(self, y, img, sx, sy, w, h, colrow):
        offset = math.ceil((w - sx) / 2)
        x = math.floor(self._width / 2) - offset
        pyxel.blt(x, y, img, sx, sy, w, h, colrow)

    def pyxel_button(self, text, x, y):
        x_offset = (len(text) * 4) + 6
        y_offset = 8
        # Doing this so I can just get position of my buttons easily
        try:
            pyxel.rect(x, y, x + x_offset, y + y_offset, 14)
            pyxel.text(x + 4, y + 2, text, 0)
        except AttributeError as e:
            pass
        return (x, y, x + x_offset, y + y_offset)

    def pyxel_button_centered(self, text, y):
        offset = math.ceil(len(text) * 4 / 2) + 3
        x = math.floor(self._width / 2) - offset
        return self.pyxel_button(text, x, y)

    def get_grid_xy_from_row_col(self, x, y):
        gx = self._grid_start_x + (self._grid_draw_size * x)
        gy = self._grid_start_y + (self._grid_draw_size * y)
        return gx, gy

    def get_grid_row_col_from_xy(self, x, y):
        col = (x - self._grid_start_x) / self._grid_draw_size
        row = (y - self._grid_start_y) / self._grid_draw_size
        return int(row), int(col)

    #### Game State ####
    def reset_game(self):
        self.elapsed_frames = 0
        self.clicked_group_times = {}
        self.clicked_tiles = {}
        self.reveal_groups = {}

        self.game_grid = ql.new_game_grid(self._grid_size, bomb_no=20)
