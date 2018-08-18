from enum import Enum
from functools import partial

import math
import random
import pyxel

class GameState(Enum):
    INTRO = 0
    HELP = 1
    PLAYING = 2

def is_within(x, y, pos):
    x1, y1, x2, y2 = pos
    return x >= x1 and x <= x2 and y >= y1 and y <= y2

class QuantumCatsweeperApp:
    def __init__(self, width=120, height=180):
        # Initialize game state
        self.game_state = GameState.INTRO

        self._main_cat_asset = 0        
        self._main_bg = 0

        self._width = width
        self._height = height

        self._play_button_pos = self.pyxel_button_centered('Play', 100)
        self._help_button_pos = self.pyxel_button_centered('Help', 115)
        self._help_back_button_pos = self.pyxel_button_centered('Back', 115)
        
        pyxel.init(self._width, self._height, caption='Quantum Catsweeper')

        pyxel.image(self._main_cat_asset).load(0, 0, 'assets/cat_16x16.png')

        # Sound
        pyxel.sound(self._main_bg).set(
            'e2e2c2g1 g1g1c2e2 d2d2d2g2 g2g2rr'
            'c2c2a1e1 e1e1a1c2 b1b1b1e2 e2e2rr', 'p', '6',
            'vffn fnff vffs vfnn', 25)
        pyxel.play(self._main_bg, [0, 1], loop=True)
        
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.game_state == GameState.INTRO:
            self.handle_intro_events()
        elif self.game_state == GameState.HELP:
            self.handle_help_events()

    def draw(self):
        self.clear_assets()

        if self.game_state == GameState.INTRO:
            self.draw_introscreen()

        elif self.game_state == GameState.HELP:
            self.draw_helpscreen()

    def clear_assets(self):
        pyxel.cls(self._main_cat_asset)

    #### Event handlers ####

    def handle_help_events(self):
        state_changed = False

        if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
            mouse_within = partial(is_within, pyxel.mouse_x, pyxel.mouse_y)

            if mouse_within(self._help_back_button_pos):
                state_changed = True
                self.game_state = GameState.INTRO
        
        if state_changed:
            pyxel.play(self._main_bg, [0, 1], loop=True)

    def handle_intro_events(self):
        state_changed = False

        if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
            mouse_within = partial(is_within, pyxel.mouse_x, pyxel.mouse_y)

            if mouse_within(self._play_button_pos):
                state_changed = True
                self.game_state = GameState.PLAYING

            if mouse_within(self._help_button_pos):
                state_changed = True
                self.game_state = GameState.HELP

        # If state changed we need to stop music
        if state_changed:
            pyxel.stop(self._main_bg)

    #### Screen Drawing ####

    def draw_helpscreen(self):
        self.pyxel_text_centered(42, 'HELP', pyxel.frame_count % 16)
        self.pyxel_button_centered('Back', 115)

    def draw_introscreen(self):
        # Draw Intro Text
        self.pyxel_text_centered(42, 'QUANTUM', pyxel.frame_count % 16)
        self.pyxel_text_centered(52, 'CATSWEEPER', pyxel.frame_count % 16)

        # Draw Quantum Cat
        cat_x = math.floor(self._width / 2) - 8
        cat_offset = math.sin(pyxel.frame_count * 0.1) * 2
        cat_flip = 1 if cat_offset >= 0 else -1
        pyxel.blt(cat_x + cat_offset, 62, self._main_cat_asset, 0, 0, 16 * cat_flip, 16, 5)

        # Draw button
        self.pyxel_button_centered('Play', 100)
        self.pyxel_button_centered('Help', 115)

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