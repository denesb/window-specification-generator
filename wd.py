#!/usr/bin/env python3

import json
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4

BOX_PADDING = (2*cm, 5*cm, 5*cm, 2*cm)
TOP = 0
RIGHT = 1
BOTTOM = 2
LEFT = 3
BOX = (A4[0], A4[1] / 2)

WINDOW_COLOR=(0, 0, 0)


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
        return (self.top_left[0], self.top_left[1], self.size[0], self.size[1])

    def bottom_line(self):
        y = self.top_left[1] + self.height
        return (self.top_left[0], y, self.bottom_right[0], y)

    def right_line(self):
        x = self.top_left[0] + self.width
        return (x, self.top_left[1], x, self.bottom_right[1])

    def __repr__(self):
        return str([self.top_left, self.size])


def scale(spec):
    box_w, box_h = BOX
    box_w = box_w - BOX_PADDING[LEFT] - BOX_PADDING[RIGHT]
    box_h = box_h - BOX_PADDING[TOP] - BOX_PADDING[BOTTOM]
    w = spec["width"] * cm
    h = spec["height"] * cm

    return min(box_h / h, box_w / w)


def translate(spec, sf, index_on_page):
    box_w, box_h = BOX

    w = spec["width"] * cm * sf
    h = spec["height"] * cm * sf

    t_x = (box_w - w) / 2
    t_y = box_h * index_on_page + (box_h - h) / 2

    return (t_x, t_y)


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


def draw_division(c, spec):
    t = spec.get("type", None)
    if t is None:
        return

    pieces = spec["pieces"]
    for i, d in enumerate(pieces):
        r = d["rect"]
        if i == len(pieces) - 1:
            break

        if t == "vertical":
            c.line(*r.bottom_line())
        else:
            c.line(*r.right_line())

        draw_division(c, d)


def draw_window(c, spec, index_on_page):
    c.saveState()

    sf = scale(spec)

    c.translate(*translate(spec, sf, index_on_page))
    c.scale(sf, sf)
    c.setStrokeColorRGB(*WINDOW_COLOR)

    w, h = spec["width"] * cm, spec["height"] * cm
    r = Rect((0, 0), (w, h))

    # Outer rectangle
    c.rect(*r.to_drawable())

    spec["division"]["rect"] = r
    calculate_division_rects(spec["division"])
    draw_division(c, spec["division"])

    c.restoreState()

def draw_windows(spec):
    c = canvas.Canvas(spec["name"] + ".pdf", pagesize=A4)
    for i, window in enumerate(spec["windows"]):
        draw_window(c, window, i % 2)
        if i > 1 and i % 2 == 0:
            c.showPage()
    c.save()


parser = argparse.ArgumentParser(
        description="Draw window size specifications")

parser.add_argument("specification", help="The window specification file", type=str)

args = parser.parse_args()

with open(args.specification, "r") as f:
    draw_windows(json.load(f))
