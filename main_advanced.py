import manim
from manim import *
import cv2
from dataclasses import dataclass
from PIL import Image, ImageOps
import random


@dataclass
class VideoStatus:
    time: float = 0
    videoObject: cv2.VideoCapture = None

    def __deepcopy__(self, memo):
        return self


class VideoMobject(ImageMobject):
    '''
    Following a discussion on Discord about animated GIF images.
    Modified for videos
    Parameters
    ----------
    filename
        the filename of the video file
    imageops
        (optional) possibility to include a PIL.ImageOps operation, e.g.
        PIL.ImageOps.mirror
    speed
        (optional) speed-up/slow-down the playback
    loop
        (optional) replay the video from the start in an endless loop
    https://discord.com/channels/581738731934056449/1126245755607339250/1126245755607339250
    2023-07-06 Uwe Zimmermann & Abulafia
    2024-03-09 Uwe Zimmermann
    '''

    def __init__(self, filename=None, imageops=None, speed=1.0, loop=False, **kwargs):
        self.filename = filename
        self.imageops = imageops
        self.speed = speed
        self.loop = loop
        self._id = id(self)
        self.status = VideoStatus()
        self.status.videoObject = cv2.VideoCapture(filename)

        self.status.videoObject.set(cv2.CAP_PROP_POS_FRAMES, 1)
        ret, frame = self.status.videoObject.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)

            if imageops != None:
                img = imageops(img)
        else:
            img = Image.fromarray(np.uint8([[63, 0, 0, 0],
                                            [0, 127, 0, 0],
                                            [0, 0, 191, 0],
                                            [0, 0, 0, 255]
                                            ]))
        super().__init__(img, **kwargs)
        if ret:
            self.add_updater(self.videoUpdater)

    def videoUpdater(self, mobj, dt):
        if dt == 0:
            return
        status = self.status
        status.time += 1000 * dt * mobj.speed
        self.status.videoObject.set(cv2.CAP_PROP_POS_MSEC, status.time)
        ret, frame = self.status.videoObject.read()
        if (ret == False) and self.loop:
            status.time = 0
            self.status.videoObject.set(cv2.CAP_PROP_POS_MSEC, status.time)
            ret, frame = self.status.videoObject.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)

            if mobj.imageops != None:
                img = mobj.imageops(img)
            mobj.pixel_array = change_to_rgba_array(
                np.asarray(img), mobj.pixel_array_dtype
            )


class MyScene(ThreeDScene):
    def construct(self):
        ax = Axes(
            x_range=[0, 960, 100],
            y_range=[0, 720, 100]
        ).add_coordinates()
        labels = ax.get_axis_labels("x", "y")
        self.play(Write(VGroup(ax, labels)))

        self.video1 = VideoMobject(
            filename="BadApple1261Circles.mp4",
            speed=1.0
        ).scale_to_fit_height(ax.coords_to_point(960, 720)[1]).scale(2.1)
        self.video1.move_to(ax.coords_to_point(960 / 2 + 25, 720 / 2 + 45))
        frame_count = Integer(number=0, color=YELLOW).move_to(RIGHT * 4.2 + UP * 2.5)

        # Update frame number on each frame
        def update_frame_text(mobject):
            mobject.set_value(int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30)

        frame_count.add_updater(update_frame_text)

        v1 = Group(self.video1, ax, labels, frame_count)

        self.add(v1)
        self.wait(440 / 30)
        self.play(Unwrite(VGroup(ax, labels), run_time=0.5))
        self.wait(0.5)
        # pivot the camera around
        # self.play(self.camera.theta_tracker.animate.set_value(20 * DEGREES), run_time=3
        #           )
        # self.play(
        #     self.camera.theta_tracker.animate.set_value((-90 + 10) * DEGREES), run_time=3
        # )
        # self.play(
        #     self.camera.theta_tracker.animate.set_value(2), run_time=3
        # )
        # self.play(
        #     self.camera.gamma_tracker.animate.set_value(0 * DEGREES),
        #     self.camera.phi_tracker.animate.set_value(0 * DEGREES),
        #     self.camera.theta_tracker.animate.set_value(-90 * DEGREES),
        #     self.camera.zoom_tracker.animate.set_value(1.3),
        #     self.video1.animate(rate_func=linear).move_to(ax.coords_to_point(960 / 2, 720 / 2 + 10)),
        #     run_time=3
        # )
        self.wait(27)
        # shrink the video and move it to the origin
        self.play(self.video1.animate.scale(0.3).move_to(ORIGIN + UP))

        # make a graph
        ax = Axes(
            x_range=[0, 10, 1],
            x_length=9,
            y_range=[0, 20, 5],
            y_length=6,
            axis_config={"include_numbers": True, "include_tip": False},

        ).to_edge(DL + RIGHT + UP, buff=1).scale(0.7)

        # add title "time spent on this stupid video"
        title = Text("Time spent on this stupid video", font_size=24).next_to(ax, UP)
        func = ax.plot(
            lambda x: 1 / 180 * x ** 2 * (x - 3) ** 2 * (x - 8) ** 2, x_range=[0, 10], color=BLUE
        )

        x = ValueTracker(7)
        dx = ValueTracker(2)
        secant = always_redraw(
            lambda: ax.get_secant_slope_group(x.get_value(), func, dx.get_value(),
                                              dx_line_color=GREEN,
                                              dy_line_color=RED,
                                              dx_label="dx",
                                              dy_label="dy",
                                              secant_line_color=YELLOW,
                                              secant_line_length=2)
        )
        dot1 = always_redraw(
            lambda: Dot().scale(0.7).move_to(ax.c2p(x.get_value(), func.underlying_function(x.get_value())))
        )
        dot2 = always_redraw(
            lambda: Dot().scale(0.7).move_to(
                ax.c2p(x.get_value() + dx.get_value(), func.underlying_function(x.get_value() + dx.get_value())))
        )
        self.play(Write(VGroup(ax, title)))
        self.play(Create(func))
        self.play(Create(dot1), Create(dot2), Create(secant))
        self.play(x.animate.set_value(0), dx.animate.set_value(0.001), run_time=4, rate_func=linear)
        # move video to be on the secant line and follow it
        self.play(self.video1.animate.move_to(ax.c2p(0, func.underlying_function(0))),
                  run_time=2
                  )
        # add updater so that the video follows the secant line
        self.video1.add_updater(lambda m: m.move_to(ax.c2p(x.get_value(), func.underlying_function(x.get_value()))))
        # update rotation based on atan2(dy, dx)
        self.last_rotation = 0

        def video_updater(m):
            curr_x = x.get_value()
            curr_dx = dx.get_value()
            curr_y = func.underlying_function(curr_x)
            curr_dy = func.underlying_function(curr_x + curr_dx) - curr_y
            angle = np.arctan2(curr_dy, curr_dx)
            m.rotate(angle - self.last_rotation)
            self.last_rotation = angle
            # add half the image's height to the axis perpendicular to the tangent point and move the image there
            m.move_to(ax.c2p(curr_x, curr_y))

        self.video1.add_updater(video_updater)
        self.play(x.animate.set_value(10), run_time=10, rate_func=linear)

        self.play(Uncreate(VGroup(ax, title, func, dot1, dot2, secant)))
        self.video1.clear_updaters()
        self.play(self.video1.animate.move_to(ORIGIN + 3 * RIGHT),
                  self.video1.animate.rotate(-PI / 2),
                  run_time=2)
        self.play(self.video1.animate.scale(3))
