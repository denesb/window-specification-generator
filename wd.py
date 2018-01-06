#!/usr/bin/env python3

import json
import argparse
from PIL import Image, ImageDraw

WINDOW_PADDING = (10, 10, 10, 10)
TOP = 0
RIGHT = 1
BOTTOM = 2
LEFT = 3
WINDOW_RECTANGLE_SIDE = 500
WINDOW_RECTANGLE_SIZE = (WINDOW_RECTANGLE_SIDE, WINDOW_RECTANGLE_SIDE)
WINDOW_IMAGE_SIZE = (WINDOW_RECTANGLE_SIZE[0] + WINDOW_PADDING[LEFT] + WINDOW_PADDING[RIGHT], WINDOW_RECTANGLE_SIZE[1] + WINDOW_PADDING[TOP] + WINDOW_PADDING[BOTTOM])
WINDOW_OUTER_RECTANGLE = [(WINDOW_PADDING[LEFT], WINDOW_PADDING[TOP]), (WINDOW_PADDING[LEFT] + WINDOW_RECTANGLE_SIDE, WINDOW_PADDING[TOP] + WINDOW_RECTANGLE_SIDE)]
WINDOW_COLOR=(0x00, 0x00, 0x00, 0xff)


class Rect():
    def __init__(self, top_left, size):
        self.top_left = top_left
        self.size = size
        self.bottom_right = (self.top_left[0] + self.size[0],
                self.top_left[1] + self.size[1])

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def to_drawable(self):
        return [self.top_left, self.bottom_right]

    def bottom_line(self):
        y = self.top_left[1] + self.height
        return [(self.top_left[0], y), (self.bottom_right[0], y)]

    def right_line(self):
        x = self.top_left[0] + self.width
        return [(x, self.top_left[1]), (x, self.bottom_right[1])]

    def __repr__(self):
        return str([self.top_left, self.size])


def scale_size(spec):
    w = spec["width"]
    h = spec["height"]

    if w < h:
        sf = int(WINDOW_RECTANGLE_SIDE / h)
        return (w * sf, h * sf, sf)
    else:
        sf = int(WINDOW_RECTANGLE_SIDE / w)
        return (w * sf, h *sf, sf)


def any_size_defined(pieces):
    for p in pieces:
        if "size" in p:
            return True

    return False


def calculate_division_rects(spec):
    r = spec["rect"]
    t = spec["type"]
    pieces = spec["pieces"]

    if not any_size_defined(pieces):
        n = len(pieces)
        for i, d in enumerate(pieces):
            w, h = r.size
            if t == "vertical":
                s = h / n
                d["rect"] = Rect((r.top_left[0], r.top_left[1] + i * s), (w, s))
            elif t == "horizontal":
                s = w / n
                d["rect"] = Rect((r.top_left[0] + i * s, r.top_left[1]), (s, h))
            else:
                raise Exception("Invalid division type: `{}'".format(t))

            if "type" in d:
                calculate_division_rects(d)


def draw_division(draw, spec):
    t = spec.get("type", None)
    if t is None:
        return

    pieces = spec["pieces"]
    for i, d in enumerate(pieces):
        r = d["rect"]
        if i == len(pieces) - 1:
            break

        if t == "vertical":
            draw.line(r.bottom_line(), fill=WINDOW_COLOR)
        else:
            draw.line(r.right_line(), fill=WINDOW_COLOR)

        draw_division(draw, d)


def draw_window(spec):
    w, h = spec["width"], spec["height"]
    wpad = WINDOW_PADDING[LEFT] + WINDOW_PADDING[RIGHT]
    hpad = WINDOW_PADDING[TOP] + WINDOW_PADDING[BOTTOM]

    image = Image.new(mode="RGBA", size=(w + wpad, h + hpad), color=(0xff, 0xff , 0xff, 0xff))
    draw = ImageDraw.Draw(image)

    r = Rect((WINDOW_PADDING[LEFT], WINDOW_PADDING[TOP]), (w, h))

    # Outer rectangle
    draw.rectangle(r.to_drawable(), outline=WINDOW_COLOR)

    spec["division"]["rect"] = r
    calculate_division_rects(spec["division"])
    draw_division(draw, spec["division"])

    image.save(spec["name"] + ".png", format="PNG")


def draw_windows(spec):
    for window in spec["windows"]:
        draw_window(window)


parser = argparse.ArgumentParser(
        description="Draw window size specifications")

parser.add_argument("specification", help="The window specification file", type=str)

args = parser.parse_args()

with open(args.specification, "r") as f:
    draw_windows(json.load(f))
