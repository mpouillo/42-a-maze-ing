import os
import sys
from src.mlx import Mlx
from src.models.maze_model import MazeModel
from src.views.ui_components import Button
from src.views.canvas import Canvas
from typing import Any


class MazeView:
    def __init__(self, mlx: Mlx, mlx_ptr: Any, win_ptr: Any,
                 window_width: int, window_height: int,
                 model: MazeModel) -> None:
        self.mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.win_w = window_width
        self.win_h = window_height
        self.model = model

        self.pad_w = 20
        self.pad_h = 250
        self.wall_size = 3
        self.compute_scales()

        self.path_gen = self.render_path()
        self.last_path_update = 0
        self.update_interval = 0.2

        self.layers = {
            "maze": self.create_canvas(self.offset_x, self.offset_y,
                                       0, self.maze_w, self.maze_h),
            "path": self.create_canvas(self.offset_x, self.offset_y,
                                       1, self.maze_w, self.maze_h),
            "ui": self.create_canvas(0, 0, 10, self.win_w, self.win_h)
        }

        self.buttons = {}

        self.colors = {
            "logo": 0xFFF0000FF,
            "entry": 0xFF00FF00,
            "exit": 0xFFFF0000,
            "path_1": 0xFF00FF00,
            "path_2": 0xFFFF0000,
            "walls": 0xFFFFFFFF
        }

        self.ui_style = {
            "btn_width": 300,
            "btn_height": 50,
            "btn_spacing": 50,
            "btn_bg": 0xFF333333,
            "btn_text": 0xFFFFFFFF,
            "btn_border": 0xFF555555,
            "btn_hover": 0xFF00AAFF,
            "btn_text": 0xFFFFFFFF,
            "border_weight": 4,
            "corner_radius": 5,
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
        return Canvas(self.mlx, self.mlx_ptr, x, y, z, width, height)

    def compute_scales(self):
        available_w = self.win_w - self.pad_w * 2 - self.wall_size
        available_h = self.win_h - self.pad_h * 2 - self.wall_size
        cols = self.model.width
        rows = self.model.height

        self.node_size = min(available_w // cols, available_h // rows)
        self.maze_w = cols * self.node_size + self.wall_size
        self.maze_h = rows * self.node_size + self.wall_size
        self.offset_x = (self.win_w - self.maze_w) // 2
        self.offset_y = (self.win_h - self.maze_h) // 2

    def update_color(self, name: str, new_color: int) -> None:
        if name in self.colors:
            self.colors[name] = new_color

    def render_maze(self):
        canvas = self.layers.get("maze")
        canvas.clear()
        color = self.colors.get("walls")
        node = self.node_size
        wall = self.wall_size

        for y, row in enumerate(self.model.grid):
            for x, cell in enumerate(row):
                pos_x = x * self.node_size
                pos_y = y * self.node_size

                if cell & 1:   # Top
                    canvas.fill_rect(pos_x, pos_y, node + wall, wall, color)
                if cell & 2:   # Right
                    canvas.fill_rect(pos_x + node, pos_y, wall, node + wall,
                                     color)
                if cell & 4:   # Bottom
                    canvas.fill_rect(pos_x, pos_y + node, node + wall, wall,
                                     color)
                if cell & 8:   # Left
                    canvas.fill_rect(pos_x, pos_y, wall, node + wall, color)
                if cell == 0xF:    # 42 Logo
                    canvas.fill_rect(pos_x + wall, pos_y + wall, node - wall,
                                     node - wall, self.colors.get("logo"))

    def draw_endpoints(self):
        path = self.layers.get("path")
        color_entry = self.colors.get("entry")
        color_exit = self.colors.get("exit")
        node = self.node_size
        wall = self.wall_size

        path.fill_rect(self.model.entry[1] * node + wall,
                       self.model.entry[0] * node + wall,
                       node - wall, node - wall, color_entry)
        path.fill_rect(self.model.exit[1] * node + wall,
                       self.model.exit[0] * node + wall,
                       node - wall, node - wall, color_exit)

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

    def render_path(self):
        while self.model.path_step < len(self.model.path):
            self.draw_path_to_step(self.model.path_step)
            self.model.path_step += 1
            yield

    def draw_path_to_step(self, step: int = 0):
        canvas = self.layers.get("path")
        node = self.node_size
        wall = self.wall_size
        curr_y, curr_x = self.model.entry

        for i in range(step):
            if i >= len(self.model.path):
                break

            direction = self.model.path[i]
            color = self.get_gradient_color(
                self.colors.get("path_1"),
                self.colors.get("path_2"),
                i / max(1, len(self.model.path) - 1)
            )

            match direction:
                case "N": curr_y -= 1
                case "S": curr_y += 1
                case "W": curr_x -= 1
                case "E": curr_x += 1

            draw_x = curr_x * node + wall   # x position of rectangle
            draw_y = curr_y * node + wall   # y position of rectangle
            draw_w = node - wall            # width of rectangle
            draw_h = node - wall            # height of rectangle

            match direction:
                case "N":
                    draw_h += wall
                case "S":
                    draw_y -= wall
                    draw_h += wall
                case "W":
                    draw_w += wall
                case "E":
                    draw_x -= wall
                    draw_w += wall

            canvas.fill_rect(draw_x, draw_y, draw_w, draw_h, color)

            if (curr_y, curr_x) == self.model.exit:
                self.draw_endpoints()
                return

    def refresh(self):
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        for layer in self.layers.values():
            self.mlx.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, layer.ptr, layer.x, layer.y
            )

    def render_ui(self):
        canvas = self.layers.get("ui")
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
        bg_color = (
            theme.get("btn_hover") if btn.hover else theme.get("btn_bg")
        )
        bw = theme.get("border_weight")
        font_scale = theme.get("font_scale")

        canvas.fill_rect(btn.x - bw, btn.y - bw, btn.width + bw * 2,
                         btn.height + bw * 2, theme.get("btn_border"))
        canvas.fill_rect(btn.x, btn.y, btn.width, btn.height, bg_color)

        text_w = (len(btn.label) * (self.font_width + 1) - 1) * font_scale
        text_h = self.font_height * font_scale
        text_x = btn.x + (btn.width - text_w) // 2
        text_y = btn.y + (btn.height - text_h) // 2
        self.draw_text(canvas, text_x, text_y,
                       btn.label, theme.get("btn_text"))

    def draw_text(self, canvas: Canvas, start_x: int, start_y: int,
                  text: str, color: int) -> None:
        char_offset = 0
        font_scale = self.ui_style.get("font_scale")
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
