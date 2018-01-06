#!/usr/bin/env python3

import json
import argparse
from PIL import Image


def draw_windows(jwindows):
    print(jwindows)


parser = argparse.ArgumentParser(
        description="Draw window size specifications")

parser.add_argument("specification", help="The window specification file", type=str)

args = parser.parse_args()

with open(args.specification, "r") as f:
    draw_windows(json.load(f))
