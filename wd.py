#!/usr/bin/env python3

import collections
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
INDICATOR_HEIGHT = 0.4 * cm

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

    def to_drawable(self, sf):
        return (self.top_left[0] * cm * sf, #x1
                self.top_left[1] * cm * sf, #x2
                self.size[0] * cm * sf, #width
                self.size[1] * cm * sf) #height

    def bottom_line(self, sf):
        y = self.bottom_right[1] * cm * sf
        return (self.top_left[0] * cm * sf,
                y,
                self.bottom_right[0] * cm * sf,
                y)

    def right_line(self, sf):
        x = self.bottom_right[0] * cm * sf
        return (x,
                self.top_left[1] * cm * sf,
                x,
                self.bottom_right[1] * cm * sf)

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
                s = w / n
                d["rect"] = Rect((r.top_left[0] + i * s, r.top_left[1]), (s, h))
            elif t == "horizontal":
                s = h / n
                d["rect"] = Rect((r.top_left[0], r.top_left[1] + i * s), (w, s))
            else:
                raise Exception("Invalid division type: `{}'".format(t))

            if "type" in d:
                calculate_division_rects(d)


def draw_division(c, spec, sf):
    t = spec.get("type", None)
    if t is None:
        return

    pieces = spec["pieces"]
    for i, d in enumerate(reversed(pieces)):
        r = d["rect"]
        if i == 0:
            continue

        if t == "vertical":
            c.line(*r.right_line(sf))
        else:
            c.line(*r.bottom_line(sf))

        draw_division(c, d, sf)


def calculate_division_sizes(spec, v, h, l):
    for i, p in enumerate(spec["pieces"]):
        r = p["rect"]
        if spec["type"] == "vertical":
            v[l].append(r.width)
        else:
            h[l].append(r.height)
        if "type" in p:
            calculate_division_sizes(p, v, h, l + 1)


def calculate_sizes(spec):
    h = collections.defaultdict(list)
    v = collections.defaultdict(list)
    h[0] = [spec["height"]]
    v[0] = [spec["width"]]

    if "division" in spec:
        calculate_division_sizes(spec["division"], v, h, 1)

    return h, v


def draw_horizontal_sizes(c, spec, h, sf):
    c.saveState()
    c.rotate(90)
    c.translate(0, -spec["width"] * cm * sf -1 * cm)
    i = 0
    for l in reversed(sorted(h.keys())):
        c.translate(0, -i * 0.4 * cm)
        if len(h[l]) == 0:
            continue

        i = i + 1
        c.saveState()
        for size in h[l]:
            draw_size(c, size, sf)
            c.translate(size * cm * sf, 0)
        c.restoreState()

    c.restoreState()


def draw_size(c, size, sf):
    text = "{:.2f}".format(size)
    text_width = c.stringWidth(text)

    s = size * cm * sf
    x = s / 2 - text_width / 2
    c.drawString(x, 0, text)
    c.line(0, 0.05 * cm, 0, INDICATOR_HEIGHT  - 0.05 * cm)
    c.line(s, 0.05 * cm, s, INDICATOR_HEIGHT  - 0.05 * cm)
    c.line(0, INDICATOR_HEIGHT / 2, x - 0.05 * cm, INDICATOR_HEIGHT / 2)
    c.line(x + text_width + 0.05 * cm, INDICATOR_HEIGHT / 2, s, INDICATOR_HEIGHT / 2)


def draw_vertical_sizes(c, v, sf):
    c.saveState()
    c.translate(0, -1 * cm)
    i = 0
    for l in reversed(sorted(v.keys())):
        c.translate(0, -i * 0.4 * cm)
        if len(v[l]) == 0:
            continue

        i = i + 1
        c.saveState()
        for size in v[l]:
            draw_size(c, size, sf)
            c.translate(size * cm * sf, 0)
        c.restoreState()

    c.restoreState()


def draw_sizes(c, spec, sf):
    h, v = calculate_sizes(spec)

    draw_horizontal_sizes(c, spec, h, sf)
    draw_vertical_sizes(c, v, sf)


def draw_window(c, spec, index_on_page):
    c.saveState()

    sf = scale(spec)

    c.translate(*translate(spec, sf, index_on_page))
    c.setStrokeColorRGB(*WINDOW_COLOR)

    r = Rect((0, 0), (spec["width"], spec["height"]))

    # Outer rectangle
    c.rect(*r.to_drawable(sf))

    spec["division"]["rect"] = r
    calculate_division_rects(spec["division"])
    draw_division(c, spec["division"], sf)

    draw_sizes(c, spec, sf)

    c.restoreState()

def draw_windows(spec):
    c = canvas.Canvas(spec["name"] + ".pdf", pagesize=A4)
    for i, window in enumerate(spec["windows"]):
        if i > 1 and i % 2 == 0:
            c.showPage()
        draw_window(c, window, 1 - (i % 2))
    c.save()


parser = argparse.ArgumentParser(
        description="Draw window size specifications")

parser.add_argument("specification", help="The window specification file", type=str)

args = parser.parse_args()

with open(args.specification, "r") as f:
    draw_windows(json.load(f))
