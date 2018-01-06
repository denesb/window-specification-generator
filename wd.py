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

def scale_size(spec):
    w = spec["width"]
    h = spec["height"]

    if w < h:
        return (int((w / h) * WINDOW_RECTANGLE_SIDE), WINDOW_RECTANGLE_SIDE)
    else:
        return (WINDOW_RECTANGLE_SIDE, int(h / w) * WINDOW_RECTANGLE_SIDE)


def draw_window(spec):
    w, h = scale_size(spec)

    image = Image.new(mode="RGBA", size=WINDOW_IMAGE_SIZE, color=(0xff, 0xff , 0xff, 0xff))
    draw = ImageDraw.Draw(image)
    draw.rectangle(WINDOW_OUTER_RECTANGLE, outline=WINDOW_COLOR)
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
