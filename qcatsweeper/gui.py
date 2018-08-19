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
    WON = 5


def is_within(x, y, pos):
    x1, y1, x2, y2 = pos
    return x >= x1 and x <= x2 and y >= y1 and y <= y2


class QuantumCatsweeperApp:
    def __init__(self, width=153, height=170, debugging=False):
        # Initialize game state
        self.game_state = GameState.INTRO

        self.debugging = debugging

        self._main_cat_asset = 0
        self._exploding_cat_asset = 1
        self._golden_cat_asset = 2

        self._main_bg = 1
        self._playing_bg = 2
        self._losing_bg = 3

        self._width = width
        self._height = height

        self._grid_size = 12
        self._grid_start_x = 5
        self._grid_start_y = 22
        self._grid_draw_size = 12

        self.game_grid = []
        self.game_grid_evaled = {}  # What string to display
        self.elapsed_frames = 0
        self.clicked_tiles = {}
        self.clicked_group_times = {}
        self.reveal_groups = {}
        self.golden_cat_x = -1
        self.golden_cat_y = -1

        self._play_real_button_pos = self.pyxel_button_centered(
            'Play', 100)
        self._help_button_pos = self.pyxel_button_centered(
            'Help', 120)
        self._help_back_button_pos = self.pyxel_button_centered('Back', 135)
        self._playing_real_back_button = self.pyxel_button('Back', 5, 5)
        self._replay_button = self.pyxel_button_centered('Play Again', 80)
        self._won_playagain_button = self.pyxel_button_centered(
            'Play Again', 100)

        pyxel.init(self._width, self._height, caption='Quantum Catsweeper')

        pyxel.image(self._main_cat_asset).load(0, 0, 'assets/cat_16x16.png')
        pyxel.image(self._exploding_cat_asset).load(
            0, 0, 'assets/explo_cat_31x25.png')
        pyxel.image(self._golden_cat_asset).load(
            0, 0, 'assets/golden_cat_16x16.png')

        # Sound
        pyxel.sound(self._main_bg).set(
            'e2e2c2g1 g1g1c2e2 d2d2d2g2 g2g2rr'
            'c2c2a1e1 e1e1a1c2 b1b1b1e2 e2e2rr', 'p', '6',
            'vffn fnff vffs vfnn', 25)
        pyxel.sound(self._playing_bg).set(
            'f0c1f0c1 g0d1g0d1 c1g1c1g1 a0e1a0e1'
            'f0c1f0c1 f0c1f0c1 g0d1g0d1 g0d1g0d1', 't', '7', 'n', 25)
        pyxel.sound(self._losing_bg).set(
            'c1g1c1g1 c1g1c1g1 b0g1b0g1 b0g1b0g1'
            'a0e1a0e1 a0e1a0e1 g0d1g0d1 g0d1g0d1', 't', '7', 'n', 25)

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
            self.handle_playing_events()

        elif self.game_state == GameState.LOST:
            self.handle_lostgame_events()

        elif self.game_state == GameState.WON:
            self.handle_wongame_events()

    def draw(self):
        self.clear_assets()

        if self.game_state == GameState.INTRO:
            self.draw_introscreen()

        elif self.game_state == GameState.HELP:
            self.draw_helpscreen()

        elif self.game_state == GameState.PLAYING_REAL:
            self.draw_playscreen()

        elif self.game_state == GameState.LOST:
            self.draw_lostscreen()

        elif self.game_state == GameState.WON:
            self.draw_winscreen()

    def clear_assets(self):
        pyxel.cls(self._main_cat_asset)

    #### Event handlers ####

    def handle_wongame_events(self):
        if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
            mouse_within = partial(is_within, pyxel.mouse_x, pyxel.mouse_y)

            if mouse_within(self._won_playagain_button):
                self.game_state = GameState.PLAYING_REAL
                self.reset_game()
                pyxel.stop(self._main_bg)
                pyxel.play(self._playing_bg, [2, 3], loop=True)

            if mouse_within(self._playing_real_back_button):
                self.game_state = GameState.INTRO

    def handle_lostgame_events(self):
        if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
            mouse_within = partial(is_within, pyxel.mouse_x, pyxel.mouse_y)

            if mouse_within(self._playing_real_back_button):
                self.game_state = GameState.INTRO
                pyxel.stop(self._losing_bg)
                pyxel.play(self._main_bg, [0, 1], loop=True)

            elif mouse_within(self._replay_button):
                self.game_state = GameState.PLAYING_REAL
                self.reset_game()
                pyxel.stop(self._losing_bg)
                pyxel.play(self._playing_bg, [2, 3], loop=True)

    def handle_playing_events(self):
        if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
            mouse_within = partial(is_within, pyxel.mouse_x, pyxel.mouse_y)

            if mouse_within(self._playing_real_back_button):
                self.game_state = GameState.INTRO
                pyxel.stop(self._playing_bg)
                pyxel.play(self._main_bg, [0, 1], loop=True)

            # If user is clicking
            if pyxel.mouse_x > self._grid_start_x and pyxel.mouse_y > self._grid_start_y:
                row, col = self.get_grid_row_col_from_xy(
                    pyxel.mouse_x, pyxel.mouse_y)

                if row < 0 or row >= self._grid_size or col < 0 or col >= self._grid_size:
                    return

                clicked_tile = self.game_grid[row][col]

                if ((row, col) not in self.clicked_tiles) and clicked_tile not in self.reveal_groups:
                    self.clicked_tiles[(row, col)] = True

                    if clicked_tile is ql.TileItems.BLANKS:
                        return

                    if clicked_tile is ql.TileItems.GOLDEN_CAT:
                        self.game_state = GameState.WON
                        pyxel.stop(self._playing_bg)
                        pyxel.play(self._main_bg, [0, 1], loop=True)

                    if clicked_tile not in self.clicked_group_times:
                        self.clicked_group_times[clicked_tile] = 1

                    # Call quantum computer to see if we reveal of nah
                    reveal_state = ql.onclick(
                        clicked_tile, self.clicked_group_times[clicked_tile]
                    )

                    # Move golden cat away from item
                    if reveal_state is ql.TileItems.NEG_EVAL:
                        offset_x = -1 if self.golden_cat_x < col else 1
                        offset_x = 0 if self.golden_cat_x == col else offset_x

                        offset_y = -1 if self.golden_cat_y < row else 1
                        offset_y = 0 if self.golden_cat_y == row else offset_y

                        # Move cat if the destination position is not clicked
                        if not self.swap_golden_cat_with(self.golden_cat_x + offset_x, self.golden_cat_y):
                            self.swap_golden_cat_with(
                                self.golden_cat_x, self.golden_cat_y + offset_y)

                    if reveal_state is ql.TileItems.POS_EVAL or \
                            reveal_state is ql.TileItems.REVEAL_GROUP or \
                            reveal_state is ql.TileItems.BOMB_DEFUSED:
                        # TODO: Move golden cat towards item
                        offset_x = 1 if self.golden_cat_x < col else -1
                        offset_x = 0 if self.golden_cat_x == col else offset_x

                        offset_y = 1 if self.golden_cat_y < row else -1
                        offset_y = 0 if self.golden_cat_y == row else offset_y

                        # Move cat if the destination position is not clicked
                        if not self.swap_golden_cat_with(self.golden_cat_x + offset_x, self.golden_cat_y):
                            self.swap_golden_cat_with(
                                self.golden_cat_x, self.golden_cat_y + offset_y)

                    if reveal_state is None or reveal_state is ql.TileItems.NEG_EVAL:
                        self.game_grid_evaled[(row, col)] = str(
                            abs(clicked_tile.value)) + '!'
                        return

                    if reveal_state is ql.TileItems.POS_EVAL:
                        self.clicked_group_times[clicked_tile] += 1

                    if reveal_state is ql.TileItems.REVEAL_GROUP:
                        self.reveal_groups[clicked_tile] = ql.TileItems.REVEAL_GROUP

                    # When bomb doesn't explode it turns into blank
                    if reveal_state is ql.TileItems.BOMB_DEFUSED:
                        self.game_grid[row][col] = ql.TileItems.BOMB_DEFUSED

                    if reveal_state is ql.TileItems.BOMB_EXPLODED:
                        self.game_grid[row][col] = ql.TileItems.BOMB_EXPLODED
                        self.game_state = GameState.LOST
                        pyxel.stop(self._playing_bg)
                        pyxel.play(self._losing_bg, 4, loop=True)

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
                pyxel.play(self._playing_bg, [2, 3], loop=True)

            if mouse_within(self._help_button_pos):
                self.game_state = GameState.HELP

    #### Screen Drawing ####

    def draw_winscreen(self):
        self.draw_grid()
        self.pyxel_button('Back', 5, 5)
        self.pyxel_text_centered(8, '       CONGRATULATIONS YOU WON', 3)
        # self.pyxel_text_centered(0, 'YOU WON!', 3)
        self.pyxel_button_centered('Play Again', 100)

    def draw_lostscreen(self):
        self.draw_grid()
        self.pyxel_button('Back', 5, 5)
        self.pyxel_button_centered('Play Again', 80)
        pyxel.blt(60, 52, self._exploding_cat_asset, 0, 0, 31, 25, 8)
        pyxel.text(60, 8, 'GAMEOVER', 8)

    def draw_grid(self):
        for row in range(len(self.game_grid)):
            for col in range(len(self.game_grid[row])):
                _x, _y = self.get_grid_xy_from_row_col(col, row)

                cur_tile = self.game_grid[row][col]

                if self.clicked_tiles.get((row, col), -1) == True or \
                        self.reveal_groups.get(cur_tile) == ql.TileItems.REVEAL_GROUP:

                    display_tile_text = "_empty"

                    if (row, col) in self.game_grid_evaled:
                        display_tile_text = self.game_grid_evaled[(row, col)]
                    else:
                        display_tile_text = str(
                            abs(self.game_grid[row][col].value))

                    if cur_tile is ql.TileItems.BLANKS:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 6)

                    elif cur_tile is ql.TileItems.GROUP1:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 3)
                        pyxel.text(_x + 2, _y + 2, display_tile_text, 7)

                    elif cur_tile is ql.TileItems.GROUP2:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 11)
                        pyxel.text(_x + 2, _y + 2, display_tile_text, 0)

                    elif cur_tile is ql.TileItems.GROUP3:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 9)
                        pyxel.text(_x + 2, _y + 2, display_tile_text, 0)

                    elif cur_tile is ql.TileItems.GROUP4:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 10)
                        pyxel.text(_x + 2, _y + 2, display_tile_text, 0)

                    elif cur_tile is ql.TileItems.GROUP5:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 13)
                        pyxel.text(_x + 2, _y + 2, display_tile_text, 0)

                    elif cur_tile is ql.TileItems.GROUP6:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 1)
                        pyxel.text(_x + 2, _y + 2, display_tile_text, 7)

                    # Golden Cat
                    elif cur_tile is ql.TileItems.GOLDEN_CAT:
                        pyxel.blt(_x, _y, self._golden_cat_asset,
                                  0, 0, self._grid_draw_size - 1, self._grid_draw_size - 1, 4)

                    # Bomb defused
                    elif cur_tile is ql.TileItems.BOMB_DEFUSED:
                        pyxel.blt(_x, _y, self._main_cat_asset,
                                  0, 0, self._grid_draw_size - 1, self._grid_draw_size - 1, 4)

                    # Bomb exploded
                    elif cur_tile is ql.TileItems.BOMB_EXPLODED:
                        pyxel.blt(_x, _y, self._main_cat_asset,
                                  0, 0, self._grid_draw_size - 1, -1 * (self._grid_draw_size - 1), 8)

                else:
                    # Golden Cat (debug)
                    if cur_tile is ql.TileItems.GOLDEN_CAT and self.debugging:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 1)
                        pyxel.text(_x + 2, _y + 2, 'G', 12)

                    else:
                        pyxel.rect(_x, _y, _x + self._grid_draw_size -
                                   2, _y - 2 + self._grid_draw_size, 5)

    def draw_playscreen(self):
        self.draw_grid()

        # Top bar stuff
        self.pyxel_button('Back', 5, 5)
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
        # Information
        self.pyxel_text_centered(40, 'Don\'t explode the cats!', 7)
        self.pyxel_text_centered(50, 'Numbers indicate number of', 7)
        self.pyxel_text_centered(60, 'tiles needed to reveal', 7)
        self.pyxel_text_centered(70, 'the whole group. If there is', 7)
        self.pyxel_text_centered(80, 'a ! then your click doesn\'t', 7)
        self.pyxel_text_centered(90, 'count. Find the golden cat', 7)
        self.pyxel_text_centered(100, 'to win!', 7)
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
        self.pyxel_button_centered('Play', 100)
        self.pyxel_button_centered('Help', 120)

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
    def swap_golden_cat_with(self, x, y):
        if x == self.golden_cat_x and y == self.golden_cat_y:
            return False

        if x >= 0 and x < self._grid_size and y >= 0 and y < self._grid_size:
            if (y, x) not in self.clicked_tiles:
                if self.game_grid[y][x] not in self.reveal_groups:
                    _tmp = self.game_grid[y][x]
                    self.game_grid[y][x] = ql.TileItems.GOLDEN_CAT
                    self.game_grid[self.golden_cat_y][self.golden_cat_x] = _tmp

                    self.golden_cat_x = x
                    self.golden_cat_y = y
                    return True
        return False

    def reset_game(self):
        self.elapsed_frames = 0
        self.clicked_group_times = {}
        self.clicked_tiles = {}
        self.reveal_groups = {}

        self.game_grid_evaled = {}
        self.game_grid = ql.new_game_grid(self._grid_size, bomb_no=20)

        for r in range(self._grid_size):
            for c in range(self._grid_size):
                if self.game_grid[r][c] == ql.TileItems.GOLDEN_CAT:
                    self.golden_cat_x = c
                    self.golden_cat_y = r
                    break
