import manim
from manim import *
import cv2
from dataclasses import dataclass
from PIL import Image, ImageOps
#
# @dataclass
# class VideoStatus:
#     time: float = 0
#     videoObject: cv2.VideoCapture = None
#     def __deepcopy__(self, memo):
#         return self
#
# class VideoMobject(ImageMobject):
#     '''
#     Following a discussion on Discord about animated GIF images.
#     Modified for videos
#     Parameters
#     ----------
#     filename
#         the filename of the video file
#     imageops
#         (optional) possibility to include a PIL.ImageOps operation, e.g.
#         PIL.ImageOps.mirror
#     speed
#         (optional) speed-up/slow-down the playback
#     loop
#         (optional) replay the video from the start in an endless loop
#     https://discord.com/channels/581738731934056449/1126245755607339250/1126245755607339250
#     2023-07-06 Uwe Zimmermann & Abulafia
#     2024-03-09 Uwe Zimmermann
#     '''
#     def __init__(self, filename=None, imageops=None, speed=1.0, loop=False, **kwargs):
#         self.filename = filename
#         self.imageops = imageops
#         self.speed    = speed
#         self.loop     = loop
#         self._id = id(self)
#         self.status = VideoStatus()
#         self.status.videoObject = cv2.VideoCapture(filename)
#
#         self.status.videoObject.set(cv2.CAP_PROP_POS_FRAMES, 1)
#         ret, frame = self.status.videoObject.read()
#         if ret:
#             img = Image.fromarray(frame)
#
#             if imageops != None:
#                 img = imageops(img)
#         else:
#             img = Image.fromarray(np.uint8([[63, 0, 0, 0],
#                                         [0, 127, 0, 0],
#                                         [0, 0, 191, 0],
#                                         [0, 0, 0, 255]
#                                         ]))
#         super().__init__(img, **kwargs)
#         if ret:
#             self.add_updater(self.videoUpdater)
#
#     def videoUpdater(self, mobj, dt):
#         if dt == 0:
#             return
#         status = self.status
#         status.time += 1000*dt*mobj.speed
#         self.status.videoObject.set(cv2.CAP_PROP_POS_MSEC, status.time)
#         ret, frame = self.status.videoObject.read()
#         if (ret == False) and self.loop:
#             status.time = 0
#             self.status.videoObject.set(cv2.CAP_PROP_POS_MSEC, status.time)
#             ret, frame = self.status.videoObject.read()
#         if ret:
#             img = Image.fromarray(frame)
#
#             if mobj.imageops != None:
#                 img = mobj.imageops(img)
#             mobj.pixel_array = change_to_rgba_array(
#                 np.asarray(img), mobj.pixel_array_dtype
#             )

class MyScene(ThreeDScene):
    def construct(self):
        ax = Axes(
            x_range=[0, 960, 100],
            y_range=[0, 720, 100]
        ).add_coordinates()
        labels = ax.get_axis_labels("x", "y")
        self.play(Write(VGroup(ax, labels)))

        svg_group = []
        for i in range(1200):
            if i < 442:
                # set stroke width to oscillate between 1 and 3 using a sine function
                stroke_width = 2 + np.sin(i / 10)
            else:
                stroke_width = 2
            if 900 < i < 1500:
                fill_color = manim.DARK_BLUE
            else:
                fill_color = None
            svg_path = f"svgs_border_2/{i}.svg"  # Assuming SVG files are named as "0.svg", "1.svg", etc. in the "svg_files" directory
            svg = (SVGMobject(svg_path, fill_color=fill_color, stroke_color=manim.DARK_BLUE, stroke_width=stroke_width)
                   .scale_to_fit_height(ax.coords_to_point(960, 720)[1])).scale(2.1)
            svg.move_to(ax.coords_to_point(960/2+25, 720/2+45))
            # remove the rect around the svg, which is in every svg
            svg = svg[:-1]

            svg_group.append(svg)

        self.play(Create(svg_group[0]))
        for index, svg in enumerate(svg_group):
            if index == 0:
                continue
            if index <= 442:

                self.remove(svg_group[index-1])
                self.add(svg)
                self.wait(1/30)
                self.remove(svg)
            elif 442 < index < 900:
                # move the camera so that we are tilted to the side
                # self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=0.5)
                self.play(Transform(svg_group[index-1], svg, run_time=1/30))
            else:
                if index == 900:
                    for i in range(442, 900):
                        self.remove(svg_group[i])
                self.play(ReplacementTransform(svg_group[index-1], svg, run_time=1/30))



