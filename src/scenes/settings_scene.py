from src.scenes import BaseScene
from src.views.renderers import BaseRenderer
import os
import random
from dotenv import dotenv_values


class SettingsScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.config = dotenv_values(self.app.config_file)
        self.bg_step = 0
        self.view = BaseRenderer(self.app, self.model)
        self.draw_bg()
        self.setup_ui()

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["width", "Width", self._cmd_update_width],
            ["height", "Height", self._cmd_update_height],
            ["entry", "Entry", self._cmd_update_entry],
            ["exit", "Exit", self._cmd_update_exit],
            ["perfect", "Perfect", self._cmd_update_perfect],
            ["hex", "Hex", self._cmd_update_hex],
            ["seed", "Seed", self._cmd_update_seed]
        ]

        btn_width = self.view.ui_style.get("btn_width", 0)
        btn_height = self.view.ui_style.get("btn_height", 0)
        btn_spacing = ((self.app.window_height - self.view.pad_h
                        - btn_height * len(btn_data)) // (len(btn_data) + 1))

        for i, b in enumerate(btn_data):
            self.view.add_button(
                b[0], b[1], (self.app.window_height - btn_width) // 2,
                (i+1) * btn_spacing + (i * btn_height) + self.view.pad_h // 2,
                9999, btn_width, btn_height, b[2]
            )

        self.view.add_button(
            "back", "Back",
            self.view.pad_w,
            self.app.window_height - (self.view.pad_h + btn_height) // 2,
            9999, btn_width, btn_height, self._cmd_open_menu
        )

    def draw_bg(self):
        canvas = self.view.layers.get("bg")
        height = self.app.window_height
        if self.bg_step == 2 * height:
            self.bg_step = 0
        progress = (self.bg_step / height) % 2.0

        for y in range(height):
            offset_y = y / height
            rmix = (offset_y + progress) % 2.0
            smix = 1.0 - abs(rmix - 1.0)
            color = self.view.get_gradient_color(0xffffbe0b, 0xffff006e, smix)
            canvas.fill_rect(0, y, canvas.width, 1, color)

    def _cmd_update_width(self):
        picks = [10, 25, 50, 75, 100, 150]
        try:
            if not hasattr(self, "pick_width"):
                self.pick_width = 0
            else:
                if 65507 in self.app.keypresses:
                    os.environ["WIDTH"] = self.config.get("WIDTH")
                    return
                else:
                    self.pick_width += 1
                if self.pick_width >= len(picks):
                    self.pick_width = 0
            os.environ["WIDTH"] = str(picks[self.pick_width])
        except Exception:
            pass

    def _cmd_update_height(self):
        picks = [10, 25, 50, 75, 100, 150]
        try:
            if not hasattr(self, "pick_height"):
                self.pick_height = 0
            else:
                if 65507 in self.app.keypresses:
                    os.environ["HEIGHT"] = self.config.get("HEIGHT")
                    return
                else:
                    self.pick_height += 1
                if self.pick_height >= len(picks):
                    self.pick_height = 0
            os.environ["HEIGHT"] = str(picks[self.pick_height])
        except Exception:
            pass

    def _cmd_update_entry(self):
        try:
            if 65507 in self.app.keypresses:
                os.environ["ENTRY"] = self.config.get("ENTRY")
                return
        except Exception:
            pass
        while True:
            try:
                coords = (",".join([
                    str(random.randrange(0, int(os.environ.get("HEIGHT", 0)))),
                    str(random.randrange(0, int(os.environ.get("WIDTH", 0))))
                ]))
                os.environ["ENTRY"] = coords
                self.app.validate_config()
                break
            except ValueError:
                continue

    def _cmd_update_exit(self):
        try:
            if 65507 in self.app.keypresses:
                os.environ["EXIT"] = self.config.get("EXIT")
                return
        except Exception:
            pass
        while True:
            try:
                coords = (",".join([
                    str(random.randrange(0, int(os.environ.get("HEIGHT", 0)))),
                    str(random.randrange(0, int(os.environ.get("WIDTH", 0))))
                ]))
                os.environ["EXIT"] = coords
                self.app.validate_config()
                break
            except ValueError:
                continue

    def _cmd_update_perfect(self):
        try:
            if 65507 in self.app.keypresses:
                os.environ["PERFECT"] = self.config.get("PERFECT", "True")
                return
            if os.environ.get("PERFECT") in [True, "True", "true", 1, "1"]:
                os.environ["PERFECT"] = "False"
            else:
                os.environ["PERFECT"] = "True"
        except Exception:
            pass

    def _cmd_update_hex(self):
        try:
            if 65507 in self.app.keypresses:
                os.environ["HEX"] = self.config.get("HEX", "False")
                return
            if os.environ.get("HEX") in [True, "True", "true", 1, "1"]:
                os.environ["HEX"] = "False"
            else:
                os.environ["HEX"] = "True"
        except Exception:
            pass

    def _cmd_update_seed(self):
        try:
            if 65507 in self.app.keypresses:
                os.environ["SEED"] = self.config.get("SEED", None)
                return
            os.environ["SEED"] = "Random"
        except Exception:
            pass

    def update_height(self):
        btn = self.view.buttons.get("height")
        try:
            if btn.is_hovered(*self.app.get_mouse_pos()):
                if 65362 in self.app.keypresses:
                    if int(os.environ["HEIGHT"]) == 200:
                        return
                    os.environ["HEIGHT"] = str(int(os.environ["HEIGHT"]) + 1)
                    self.app.keypresses.remove(65362)
                elif 65364 in self.app.keypresses:
                    if int(os.environ["HEIGHT"]) == 0:
                        return
                    os.environ["HEIGHT"] = str(int(os.environ["HEIGHT"]) - 1)
                    self.app.keypresses.remove(65364)
        except Exception:
            pass
        btn.label = "Height:" + str(os.environ.get("HEIGHT", "None"))

    def update_width(self):
        btn = self.view.buttons.get("width")
        try:
            if btn.is_hovered(*self.app.get_mouse_pos()):
                if 65362 in self.app.keypresses:
                    if int(os.environ["WIDTH"]) == 200:
                        return
                    os.environ["WIDTH"] = str(int(os.environ["WIDTH"]) + 1)
                    self.app.keypresses.remove(65362)
                elif 65364 in self.app.keypresses:
                    if int(os.environ["WIDTH"]) == 0:
                        return
                    os.environ["WIDTH"] = str(int(os.environ["WIDTH"]) - 1)
                    self.app.keypresses.remove(65364)
        except Exception:
            pass
        btn.label = "Width:" + os.environ.get("WIDTH", "None")

    def update_entry(self):
        btn = self.view.buttons.get("entry")
        btn.label = "Entry:" + os.environ.get("ENTRY", "None")

    def update_exit(self):
        btn = self.view.buttons.get("exit")
        btn.label = "Exit:" + os.environ.get("EXIT", "None")

    def update_perfect(self):
        btn = self.view.buttons.get("perfect")
        btn.label = "Perfect:" + os.environ.get("PERFECT", "False")

    def update_hex(self):
        btn = self.view.buttons.get("hex")
        btn.label = "Hex:" + os.environ.get("HEX", "False")

    def update_seed(self):
        btn = self.view.buttons.get("seed")
        try:
            if btn.is_hovered(*self.app.get_mouse_pos()):
                if 65362 in self.app.keypresses:
                    os.environ["SEED"] = str(
                        int(os.environ.get("SEED", 0)) + 1
                    )
                    self.app.keypresses.remove(65362)
                elif 65364 in self.app.keypresses:
                    os.environ["SEED"] = str(
                        max(0, int(os.environ.get("SEED", 0)) - 1)
                    )
                    self.app.keypresses.remove(65364)
        except Exception:
            pass
        btn.label = "Seed:" + os.environ.get("SEED", "Random")

    def update(self):
        self.draw_bg()
        self.bg_step += 10
        self.update_height()
        self.update_width()
        self.update_entry()
        self.update_exit()
        self.update_perfect()
        self.update_hex()
        self.update_seed()

        super().update()

    def render(self):
        super().render()
