#!/usr/bin/env python3

from PIL import Image
import math
import os

# ============================================================
# AGRICULTURAL FIELD MAP
# ============================================================

resolution = 0.05

# World limits
xmin = -3.0
xmax = 3.0
ymin = -3.5
ymax = 3.5

width = int(round((xmax - xmin) / resolution))
height = int(round((ymax - ymin) / resolution))

# Start with completely free space
# PGM:
# 254 = free
# 0   = occupied
img = Image.new("L", (width, height), 254)
pixels = img.load()


def world_to_pixel(x, y):
    px = int(round((x - xmin) / resolution))
    py = height - 1 - int(round((y - ymin) / resolution))
    return px, py


def fill_rectangle(x1, y1, x2, y2, value=0):

    px1, py1 = world_to_pixel(x1, y1)
    px2, py2 = world_to_pixel(x2, y2)

    left = max(0, min(px1, px2))
    right = min(width - 1, max(px1, px2))

    top = max(0, min(py1, py2))
    bottom = min(height - 1, max(py1, py2))

    for py in range(top, bottom + 1):
        for px in range(left, right + 1):
            pixels[px, py] = value


# ============================================================
# FIELD BOUNDARIES
# ============================================================

boundary_thickness = 0.10

# Left boundary
fill_rectangle(
    xmin,
    ymin,
    xmin + boundary_thickness,
    ymax
)

# Right boundary
fill_rectangle(
    xmax - boundary_thickness,
    ymin,
    xmax,
    ymax
)

# Front boundary
fill_rectangle(
    xmin,
    ymin,
    xmax,
    ymin + boundary_thickness
)

# Back boundary
fill_rectangle(
    xmin,
    ymax - boundary_thickness,
    xmax,
    ymax
)


# ============================================================
# CROP ROWS
# ============================================================

crop_rows = [-2.4, -1.2, 1.2, 2.4]

crop_xmin = -2.5
crop_xmax = 2.5

crop_width = 0.15

for row_y in crop_rows:

    fill_rectangle(
        crop_xmin,
        row_y - crop_width / 2,
        crop_xmax,
        row_y + crop_width / 2
    )


# ============================================================
# SAVE MAP
# ============================================================

map_directory = os.path.expanduser(
    "~/agri_rover_ws/src/agri_rover_gazebo/maps"
)

os.makedirs(map_directory, exist_ok=True)

pgm_file = os.path.join(
    map_directory,
    "agri_field_map.pgm"
)

yaml_file = os.path.join(
    map_directory,
    "agri_field_map.yaml"
)

img.save(pgm_file)

with open(yaml_file, "w") as f:

    f.write(
        "image: agri_field_map.pgm\n"
        f"resolution: {resolution}\n"
        f"origin: [{xmin}, {ymin}, 0.0]\n"
        "negate: 0\n"
        "occupied_thresh: 0.65\n"
        "free_thresh: 0.196\n"
        "mode: trinary\n"
    )

print()
print("========================================")
print(" AGRICULTURAL FIELD MAP CREATED")
print("========================================")
print(f"Map size : {width} x {height} cells")
print(f"Resolution: {resolution} m/cell")
print(f"X range  : {xmin} to {xmax} m")
print(f"Y range  : {ymin} to {ymax} m")
print()
print(f"PGM : {pgm_file}")
print(f"YAML: {yaml_file}")
print("========================================")
