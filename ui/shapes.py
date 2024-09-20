import imgui
import time

from dataclasses import dataclass
from typing import Union

from sdk.entity import Entity

number = Union[int, float]

@dataclass(eq=True, frozen=True)
class Circle: 
    x: number
    y: number
    r: number
    id: int
    ttl: float
    updated_at: float = 0

    @staticmethod
    def new(x, y, r, id, ttl = 1.0):
        return Circle(x, y, r, id, ttl, time.time())

    def draw(self, draw_list):
        draw_list.add_circle_filled(self.x, self.y, self.r, imgui.get_color_u32_rgba(1, 0, 0, 1))

@dataclass(eq=True, frozen=True)
class Line:
    x1: number
    y1: number
    x2: number
    y2: number
    id: int
    ttl: float
    updated_at: float = 0

    @staticmethod
    def new(x1: number, y1: number, x2: number, y2: number, id: int, ttl = 1.0):
        return Line(x1, y1, x2, y2, id, ttl, time.time())

    def draw(self, draw_list):
        draw_list.add_line(self.x1, self.y1, self.x2, self.y2, imgui.get_color_u32_rgba(1, 0, 0, 1))

class ShapeManager:
    def __init__(self):
        self.shapes = dict()

    def add(self, shape: Union[Circle, Line]):
        shape_type = str(type(shape))

        if not shape_type in self.shapes:
            self.shapes[shape_type] = dict()

        self.shapes[shape_type][shape.id] = shape

    def draw(self, draw_list):
        for shapes in self.shapes.values():
            for shape in shapes.values():
                shape.draw(draw_list)

                if time.time() - shape.updated_at > shape.ttl:
                    del shapes[shape.id]

    def remove(self, id: int):
        for shapes in self.shapes.values():
            if id in shapes:
                del shapes[id]

    def __iter__(self):
        return iter(self.shapes)

    def __len__(self):
        return len(self.shapes)

shapes = ShapeManager()