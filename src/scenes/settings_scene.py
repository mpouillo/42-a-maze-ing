import os
import random
from dotenv import dotenv_values
from src.scenes import BaseScene
from src.views.renderers import BaseRenderer
from typing import Any, Callable, TypeAlias

BtnData: TypeAlias = list[tuple[str, str, Callable[[], None]]]


class SettingsScene(BaseScene):
    def __init__(self, app: Any) -> None:
        super().__init__(app)

        self.config: dict[str, str | None] = dotenv_values(
            self.app.config_file
        )
        self.bg_step: int = 0
        self.view: Any = BaseRenderer(self.app, self.model)

        self.draw_bg()
        self.setup_ui()

    def setup_ui(self) -> None:
        """Create buttons with default values"""
        self.view.clear_buttons()

        btn_data: BtnData = [
            ("width", "Width", self._cmd_update_width),
            ("height", "Height", self._cmd_update_height),
            ("entry", "Entry", self._cmd_update_entry),
            ("exit", "Exit", self._cmd_update_exit),
            ("perfect", "Perfect", self._cmd_update_perfect),
            ("hex", "Hex", self._cmd_update_hex),
            ("seed", "Seed", self._cmd_update_seed),
            ("walls", "Walls", self._cmd_update_wall_color)
        ]

        btn_width: int = self.view.ui_style.get("btn_width", 0)
        btn_height: int = self.view.ui_style.get("btn_height", 0)
        btn_spacing: int = ((self.app.window_height - self.view.pad_h
                            - btn_height * len(btn_data))
                            // (len(btn_data) + 1))

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

    def draw_bg(self) -> None:
        """Render background depending on current step value"""
        canvas: Any = self.view.layers.get("bg")
        height: int = self.app.window_height
        if self.bg_step == 2 * height:
            self.bg_step = 0
        progress: float = (self.bg_step / height) % 2.0

        for y in range(height):
            offset_y: float = y / height
            rmix: float = (offset_y + progress) % 2.0
            smix: float = 1.0 - abs(rmix - 1.0)
            color: int = self.view.get_gradient_color(
                self.app.colors.get("bg_1"),
                self.app.colors.get("bg_2"), smix
            )
            canvas.fill_rect(0, y, canvas.width, 1, color)

    def _cmd_update_width(self) -> None:
        """Rotate or reset os.environ width"""
        picks: list[int] = [10, 25, 50, 75, 100, 150]
        try:
            if not hasattr(self, "pick_width"):
                self.pick_width: int = 0
            else:
                if 65507 in self.app.keypresses:
                    config_width: str | None = self.config.get("WIDTH")
                    if config_width:
                        os.environ["WIDTH"] = config_width
                    else:
                        os.environ["WIDTH"] = "None"
                    return
                else:
                    self.pick_width += 1
                if self.pick_width >= len(picks):
                    self.pick_width = 0
            os.environ["WIDTH"] = str(picks[self.pick_width])
        except Exception:
            pass

    def _cmd_update_height(self) -> None:
        """Rotate or reset os.environ height"""
        picks: list[int] = [10, 25, 50, 75, 100, 150]
        try:
            if not hasattr(self, "pick_height"):
                self.pick_height: int = 0
            else:
                if 65507 in self.app.keypresses:
                    config_height: str | None = self.config.get("HEIGHT")
                    if config_height:
                        os.environ["HEIGHT"] = config_height
                    else:
                        os.environ["HEIGHT"] = "None"
                    return
                else:
                    self.pick_height += 1
                if self.pick_height >= len(picks):
                    self.pick_height = 0
            os.environ["HEIGHT"] = str(picks[self.pick_height])
        except Exception:
            pass

    def _cmd_update_entry(self) -> None:
        """Randomize or reset os.environ entry"""
        try:
            if 65507 in self.app.keypresses:
                config_entry: str | None = self.config.get("ENTRY")
                if config_entry:
                    os.environ["ENTRY"] = config_entry
                else:
                    os.environ["ENTRY"] = "None"
                return
        except Exception:
            pass
        while True:
            try:
                coords: str = (",".join([
                    str(random.randrange(0, int(os.environ.get("HEIGHT", 0)))),
                    str(random.randrange(0, int(os.environ.get("WIDTH", 0))))
                ]))
                os.environ["ENTRY"] = coords
                self.app.validate_config()
                break
            except ValueError:
                continue

    def _cmd_update_exit(self) -> None:
        """Randomize or reset os.environ exit"""
        try:
            if 65507 in self.app.keypresses:
                config_exit: str | None = self.config.get("EXIT")
                if config_exit:
                    os.environ["EXIT"] = config_exit
                else:
                    os.environ["EXIT"] = "None"
                return
        except Exception:
            pass
        while True:
            try:
                coords: str = (",".join([
                    str(random.randrange(0, int(os.environ.get("HEIGHT", 0)))),
                    str(random.randrange(0, int(os.environ.get("WIDTH", 0))))
                ]))
                os.environ["EXIT"] = coords
                self.app.validate_config()
                break
            except ValueError:
                continue

    def _cmd_update_perfect(self) -> None:
        """Toggle or reset os.environ perfect"""
        try:
            if 65507 in self.app.keypresses:
                config_perfect: str | None = self.config.get("PERFECT")
                if config_perfect:
                    os.environ["PERFECT"] = config_perfect
                else:
                    os.environ["PERFECT"] = "None"
                return
            if os.environ.get("PERFECT") in [True, "True", "true", 1, "1"]:
                os.environ["PERFECT"] = "False"
            else:
                os.environ["PERFECT"] = "True"
        except Exception:
            pass

    def _cmd_update_hex(self) -> None:
        """Toggle or reset os.environ hex"""
        try:
            if 65507 in self.app.keypresses:
                config_hex: str | None = self.config.get("HEX")
                if config_hex:
                    os.environ["HEX"] = config_hex
                else:
                    os.environ["HEX"] = "None"
                return
            if os.environ.get("HEX") in [True, "True", "true", 1, "1"]:
                os.environ["HEX"] = "False"
            else:
                os.environ["HEX"] = "True"
        except Exception:
            pass

    def _cmd_update_seed(self) -> None:
        """Toggle or reset os.environ seed"""
        try:
            if 65507 in self.app.keypresses:
                config_seed: str | None = self.config.get("CONFIG_SEED")
                if config_seed:
                    os.environ["CONFIG_SEED"] = config_seed
                else:
                    os.environ["CONFIG_SEED"] = "None"
                return
            os.environ["SEED"] = "Random"
        except Exception:
            pass

    def _cmd_update_wall_color(self) -> None:
        """Randomize or reset maze walls color"""
        if 65362 in self.app.keypresses:
            self.app.colors["walls"] = 0xffff006e
        else:
            self.app.colors["walls"] = random.randrange(0xFF000000, 0xFFFFFFFF)

    def update_height(self) -> None:
        """Update height button label with os.environ value"""
        btn: Any = self.view.buttons.get("height")
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

    def update_width(self) -> None:
        """Update width button label with os.environ value"""
        btn: Any = self.view.buttons.get("width")
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

    def update_entry(self) -> None:
        """Update entry button label with os.environ value"""
        btn: Any = self.view.buttons.get("entry")
        btn.label = "Entry:" + os.environ.get("ENTRY", "None")

    def update_exit(self) -> None:
        """Update exit button label with os.environ value"""
        btn: Any = self.view.buttons.get("exit")
        btn.label = "Exit:" + os.environ.get("EXIT", "None")

    def update_perfect(self) -> None:
        """Update perfect button label with os.environ value"""
        btn: Any = self.view.buttons.get("perfect")
        btn.label = "Perfect:" + os.environ.get("PERFECT", "False")

    def update_hex(self) -> None:
        """Update hex button label with os.environ value"""
        btn: Any = self.view.buttons.get("hex")
        btn.label = "Hex:" + os.environ.get("HEX", "False")

    def update_seed(self) -> None:
        """Update seed button label with os.environ value"""
        btn: Any = self.view.buttons.get("seed")
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

    def update_walls(self) -> None:
        """Update walls button label with app colors value"""
        btn: Any = self.view.buttons.get("walls")
        btn.label = "Walls:" + hex(self.app.colors.get("walls", 0) & 0xFFFFFF)

    def update(self) -> None:
        """Update maze display depending on current values"""
        self.draw_bg()
        self.bg_step += 10
        self.update_height()
        self.update_width()
        self.update_entry()
        self.update_exit()
        self.update_perfect()
        self.update_hex()
        self.update_seed()
        self.update_walls()

        super().update()

    def render(self) -> None:
        """Update current frame"""
        super().render()
