# creates bezier curves from bad apple frames. Copied from Junferno's code - ok, doesn't really
# produce the output I want, see video_to_svg.ipynb
import cv2
import potrace
import numpy as np
from PIL import Image
from pathlib import Path
import os
import json

frames_path = Path("frames")
svg_path = Path("svg")
if not svg_path.exists():
    svg_path.mkdir()


def png_to_np_array(filename):
    img = Image.open(filename)
    data = np.array(img.getdata()).reshape(img.size[1], img.size[0], 3)
    bindata = np.zeros((img.size[1], img.size[0]), np.uint32)
    for i, row in enumerate(data):
        for j, byte in enumerate(row):
            bindata[img.size[1]-i-1, j] = 1 if sum(byte) < 127*3 else 0
        #     print('###' if bindata[i, j] == 1 else '   ', end='')
        # print()
    return bindata


def png_to_svg(filename):
    data = png_to_np_array(filename)
    bmp = potrace.Bitmap(data)
    path = bmp.trace()
    return path


frame_curves = {}

for i in range(6572):

    curves = []

    path = png_to_svg(f'frames/{i}.png')

    for curve in path.curves:
        segments = curve.segments
        start = curve.start_point
        for segment in segments:
            x0, y0 = start
            if segment.is_corner:
                x1, y1 = segment.c
                x2, y2 = segment.end_point
                curves.append(f'((1-t){x0}+t{x1},(1-t){y0}+t{y1})')
                curves.append(f'((1-t){x1}+t{x2},(1-t){y1}+t{y2})')
            else:
                x1, y1 = segment.c1
                x2, y2 = segment.c2
                x3, y3 = segment.end_point
                curves.append(
                    f'((1-t)((1-t)((1-t){x0:f}+t{x1:f})+t((1-t){x1:f}+t{x2:f}))+t((1-t)((1-t){x1:f}+t{x2:f})+t((1-t){x2:f}+t{x3:f})),\
                (1-t)((1-t)((1-t){y0:f}+t{y1:f})+t((1-t){y1:f}+t{y2:f}))+t((1-t)((1-t){y1:f}+t{y2:f})+t((1-t){y2:f}+t{y3:f})))')
            start = segment.end_point
    print(i)
    frame_curves[i] = curves

# save to json
with open('frame_coords.json', 'w') as f:
    json.dump(frame_curves, f)

