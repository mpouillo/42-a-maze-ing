import os
import sys
from src.models.maze import MazeModel
from src.views.ui_components import Button
from src.views.canvas import Canvas


class BaseRenderer:
    def __init__(self, app, model: MazeModel) -> None:
        self.app = app
        self.model = model

        self.pad_w = 20
        self.pad_h = 100

        self.layers = {
            "ui": self.create_canvas(0, 0, 0, self.app.window_width,
                                     self.app.window_height)
        }

        self.buttons = {}

        self.ui_style = {
            "btn_width": 300,
            "btn_height": self.pad_h // 2,
            "btn_spacing": 50,
            "btn_bg": 0xFF333333,
            "btn_text": 0xFFFFFFFF,
            "btn_border": 0xFF555555,
            "btn_hover": 0xFFFFAAAA,
            "btn_disabled": 0xFF404040,
            "btn_text": 0xFFFFFFFF,
            "btn_text_disabled": 0xFF7F7F7F,
            "border_weight": 4,
            "font_scale": 3
        }

        self.fonts_dir = "src/fonts"
        self.fonts_dict = self.parse_fonts(self.fonts_dir)
        self.font_scale = 3
        try:
            self.font_width = len(self.fonts_dict.get("a")[0])
            self.font_height = len(self.fonts_dict.get("a"))
        except Exception:
            sys.exit("Failed to parse fonts dictionnary")

    @staticmethod
    def parse_fonts(fonts_dir):
        fonts_dict = {}
        files = os.listdir(fonts_dir)

        for f in files:
            try:
                with open(fonts_dir + "/" + f) as font_file:
                    array = []
                    for line in font_file:
                        row = []
                        for c in line.strip():
                            row.append(int(c, 16))
                        array.append(row)
                    fonts_dict.update({chr(int(f)): array})
            except (ValueError, TypeError) as e:
                sys.exit("Error while parsing fonts:", e)

        return fonts_dict

    def create_canvas(self, x: int, y: int, z: int,
                      width: int, height: int) -> Canvas:
        return Canvas(self.app, x, y, z, width, height)

    def clear_canvas(self):
        for layer in self.layers.values():
            layer.clear()
        self.layers.clear()

    def update_color(self, name: str, new_color: int) -> None:
        if name in self.colors:
            self.colors[name] = new_color

    def get_gradient_color(self, color_1, color_2, mix):
        alpha_1 = (color_1 >> 24) & 0xFF
        red_1 = (color_1 >> 16) & 0xFF
        green_1 = (color_1 >> 8) & 0xFF
        blue_1 = color_1 & 0xFF

        alpha_2 = (color_2 >> 24) & 0xFF
        red_2 = (color_2 >> 16) & 0xFF
        green_2 = (color_2 >> 8) & 0xFF
        blue_2 = color_2 & 0xFF

        alpha = int(alpha_1 + (alpha_2 - alpha_1) * mix)
        red = int(red_1 + (red_2 - red_1) * mix)
        green = int(green_1 + (green_2 - green_1) * mix)
        blue = int(blue_1 + (blue_2 - blue_1) * mix)

        return (alpha << 24) | (red << 16) | (green << 8) | blue

    def draw_ui(self):
        canvas = self.layers.get("ui")
        canvas.clear()
        for button in self.buttons.values():
            self.draw_button(canvas, button)

    def add_button(self, name: str, label: str, x: int, y: int, z: int,
                   width: int, height: int, action: callable) -> None:
        button = Button(label, x, y, z, width, height, action)
        self.buttons.update({name: button})

    def clear_buttons(self, *buttons: str | None):
        if not buttons:
            self.buttons.clear()
            return

        for button in buttons:
            self.buttons.remove(button)

    def draw_button(self, canvas: Canvas, btn: Button):
        theme = self.ui_style
        bw = theme.get("border_weight")

        bg_color = (
            theme.get("btn_disabled") if not btn.enabled
            else theme.get("btn_hover") if btn.hover
            else theme.get("btn_bg")
        )

        text_color = (
            theme.get("btn_text_disabled") if not btn.enabled
            else theme.get("btn_text")
        )

        canvas.fill_rect(btn.x - bw, btn.y - bw, btn.width + bw * 2,
                         btn.height + bw * 2, theme.get("btn_border"))
        canvas.fill_rect(btn.x, btn.y, btn.width, btn.height, bg_color)

        if len(btn.label) == 0:
            return

        base_text_w = (len(btn.label) * (self.font_width + 1) - 1)
        max_scale = btn.width // base_text_w
        theme_scale = theme.get("font_scale", 1)
        font_scale = max(1, min(max_scale, theme_scale))

        text_w = (len(btn.label) * (self.font_width + 1) - 1) * font_scale
        text_h = self.font_height * font_scale
        text_x = btn.x + (btn.width - text_w) // 2
        text_y = btn.y + (btn.height - text_h) // 2

        self.draw_text(
            canvas, text_x, text_y, btn.label, text_color, font_scale
        )

    def draw_text(self, canvas: Canvas, start_x: int, start_y: int,
                  text: str, color: int, scale: int | None = None) -> None:
        char_offset = 0
        font_scale = (scale if scale is not None
                      else self.ui_style.get("font_scale", 1))
        for character in text.lower():
            if character in self.fonts_dict:
                char_data = self.fonts_dict.get(character)
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

    def refresh_layers(self):
        self.app.mlx.mlx_clear_window(self.app.mlx_ptr, self.app.win_ptr)
        for layer in self.layers.values():
            self.app.mlx.mlx_put_image_to_window(
                self.app.mlx_ptr, self.app.win_ptr, layer.ptr, layer.x, layer.y
            )
