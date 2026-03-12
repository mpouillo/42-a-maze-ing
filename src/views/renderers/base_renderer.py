import os
import sys
from src.views.ui_components import Button
from src.views.canvas import Canvas
from typing import Any, Callable, TypeAlias

FontsDict: TypeAlias = dict[str, list[list[int]]]


class BaseRenderer:
    def __init__(self, app: Any, model: Any) -> None:
        self.app: Any = app
        self.model: Any = model
        self.pad_w: int = 40
        self.pad_h: int = 150
        self.layers: dict[str, Canvas] = {}
        self.buttons: dict[str, Button] = {}

        self.ui_style: dict[str, int] = {
            "btn_width": 300,
            "btn_height": self.pad_h // 5 * 2,
            "btn_spacing": 50,
            "btn_bg": 0xFF333333,
            "btn_text": 0xFFFFFFFF,
            "btn_border": 0xFF555555,
            "btn_hover": 0xff94167f,
            "btn_disabled": 0xFF404040,
            "btn_text": 0xFFFFFFFF,
            "btn_text_disabled": 0xFF7F7F7F,
            "border_weight": 4,
            "font_scale": 3
        }

        self.add_layer("bg", 0, 0, 0, self.app.window_width,
                       self.app.window_height)
        self.add_layer("ui", 0, 0, 10, self.app.window_width,
                       self.app.window_height)
        self.add_layer("popup", 0, 0, 99, self.app.window_width,
                       self.app.window_height)

        self.fonts_dir: str = "src/fonts"
        self.fonts_dict: FontsDict = self.parse_fonts(
            self.fonts_dir
        )
        self.font_scale: int = 3
        try:
            a_data: list[list[int]] | None = self.fonts_dict.get("a")
            if not a_data:
                raise ValueError
            self.font_width: int = len(a_data[0])
            self.font_height: int = len(a_data)
        except Exception:
            sys.exit("Failed to parse fonts dictionary")

    @staticmethod
    def parse_fonts(fonts_dir: str) -> FontsDict:
        """Parse fonts from font fils and return them as a dict"""
        fonts_dict: FontsDict = {}
        files: list[str] = os.listdir(fonts_dir)

        for f in files:
            try:
                with open(fonts_dir + "/" + f) as font_file:
                    array: list[list[int]] = []
                    for line in font_file:
                        row: list[int] = []
                        for c in line.strip():
                            row.append(int(c, 16))
                        array.append(row)
                    fonts_dict.update({chr(int(f)): array})
            except (ValueError, TypeError) as e:
                sys.exit(f"Error while parsing fonts: {e}")

        return fonts_dict

    def create_canvas(self, x: int, y: int, z: int,
                      width: int, height: int) -> Canvas:
        """Create and return a canvas"""
        return Canvas(self.app, x, y, z, width, height)

    def add_layer(self, name: str, x: int, y: int, z: int,
                  width: int, height: int) -> Canvas:
        """Create a canvas and add it to self.layers dict"""
        canvas = self.create_canvas(x, y, z, width, height)
        self.layers.update({name: canvas})
        return canvas

    def clear_layers(self, *names: str) -> None:
        """Clear a list of layers fetched by name"""
        if not names:
            for lay in self.layers.values():
                lay.clear()
        else:
            for name in names:
                layer: Canvas | None = self.layers.get(name)
                if layer:
                    layer.clear()

    def delete_layers(self, *names: str) -> None:
        """Delete a list of layers fetched by name from self.layers"""
        to_delete: list[str] = []

        if not names:
            for name, layer in self.layers.items():
                layer.destroy()
                to_delete.append(name)
        else:
            for name, layer in self.layers.items():
                if name in names:
                    layer.destroy()
                    to_delete.append(name)

        for name in to_delete:
            self.layers.pop(name)

    def get_gradient_color(self, color_1: int, color_2: int,
                           mix: float) -> int:
        """Return a mix between two colors"""
        alpha_1: int = (color_1 >> 24) & 0xFF
        red_1: int = (color_1 >> 16) & 0xFF
        green_1: int = (color_1 >> 8) & 0xFF
        blue_1: int = color_1 & 0xFF

        alpha_2: int = (color_2 >> 24) & 0xFF
        red_2: int = (color_2 >> 16) & 0xFF
        green_2: int = (color_2 >> 8) & 0xFF
        blue_2: int = color_2 & 0xFF

        alpha: int = int(alpha_1 + (alpha_2 - alpha_1) * mix)
        red: int = int(red_1 + (red_2 - red_1) * mix)
        green: int = int(green_1 + (green_2 - green_1) * mix)
        blue: int = int(blue_1 + (blue_2 - blue_1) * mix)

        return (alpha << 24) | (red << 16) | (green << 8) | blue

    def add_button(self, name: str, label: str, x: int, y: int,
                   z: int, width: int, height: int,
                   action: Callable[[], None]) -> None:
        """Create and add a button to self.buttons"""
        button: Button = Button(label, x, y, z, width, height, action)
        self.buttons.update({name: button})

    def clear_buttons(self, *buttons: str) -> None:
        """Remove buttons by name from self.buttons"""
        if not buttons:
            self.buttons.clear()
            return

        for button in buttons:
            self.buttons.pop(button)

    def draw_button(self, canvas: Canvas, btn: Button) -> None:
        """Draw a button to a canvas"""
        theme: dict[str, int] = self.ui_style
        bw: int = theme.get("border_weight", 1)

        bg_color: int = (
            theme.get("btn_disabled", 0xFF404040) if not btn.enabled
            else theme.get("btn_hover", 0xFF7F7F7F) if btn.hover
            else theme.get("btn_bg", 0xFF333333)
        )

        text_color: int = (
            theme.get("btn_text_disabled", 0xFF404040) if not btn.enabled
            else theme.get("btn_text", 0xFFFFFFFF)
        )

        canvas.fill_rect(
            btn.x - bw, btn.y - bw, btn.width + bw * 2, btn.height + bw * 2,
            theme.get("btn_border", 0xFF555555)
        )
        canvas.fill_rect(btn.x, btn.y, btn.width, btn.height, bg_color)

        if len(btn.label) == 0:
            return

        base_text_w: int = (len(btn.label) * (self.font_width + 1) - 1)
        max_scale: int = btn.width // base_text_w
        theme_scale: int = theme.get("font_scale", 1)
        font_scale: int = max(1, min(max_scale, theme_scale))

        text_w: int = (len(btn.label) * (self.font_width + 1) - 1) * font_scale
        text_h: int = self.font_height * font_scale
        text_x: int = btn.x + (btn.width - text_w) // 2
        text_y: int = btn.y + (btn.height - text_h) // 2

        self.draw_text(
            canvas, text_x, text_y, btn.label, text_color, font_scale
        )

    def redraw_ui(self) -> None:
        """Clear ui canvas and redraw all buttons"""
        canvas: Any = self.layers.get("ui")
        canvas.clear()
        for button in self.buttons.values():
            self.draw_button(canvas, button)

    def draw_text(self, canvas: Canvas, start_x: int, start_y: int,
                  text: str, color: int, scale: int | None = None) -> None:
        """Draw text to a canvas"""
        char_offset: int = 0
        font_scale: int = (scale if scale is not None
                           else self.ui_style.get("font_scale", 1))

        for character in text.lower():
            char_data = self.fonts_dict.get(character)
            if not char_data:
                char_offset += (self.font_width + 1) * font_scale
                continue
            for y, row in enumerate(char_data):
                y *= font_scale
                for x, value in enumerate(row):
                    x *= font_scale
                    if value == 1:
                        canvas.fill_rect(
                            start_x + x + char_offset, start_y + y,
                            font_scale, font_scale, color
                        )
            char_offset += (self.font_width + 1) * font_scale

    def refresh_layers(self) -> None:
        """Refresh layers im z_index order"""
        self.app.mlx.mlx_clear_window(self.app.mlx_ptr, self.app.win_ptr)
        for layer in sorted(
            self.layers.values(), key=lambda layer: layer.z,
        ):
            self.app.mlx.mlx_put_image_to_window(
                self.app.mlx_ptr, self.app.win_ptr, layer.ptr, layer.x, layer.y
            )
