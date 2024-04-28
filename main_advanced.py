from manim import *
import cv2
from dataclasses import dataclass
from PIL import Image, ImageOps
import json


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
        status.time += 1000 * dt
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

    def clear_updaters(self, recursive: bool = True):
        super().clear_updaters(recursive)
        self.add_updater(self.videoUpdater)



class MyScene(ThreeDScene):
    def construct(self):
        # create axes
        ax = Axes(
            x_range=[0, 960, 100],
            y_range=[0, 720, 100]
        ).add_coordinates()
        labels = ax.get_axis_labels("x", "y")
        self.play(Write(VGroup(ax, labels)))
        # math_level_text = Text("Kindergarten", font_size=24).to_edge(DL).set_color(YELLOW)
        # start playing video
        self.video1 = VideoMobject(
            filename="BadApple1261CirclesThickFill.mp4",
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

        # hide axes and show some interesting visuals
        self.play(Unwrite(VGroup(ax, labels), run_time=0.5))
        self.wait(0.5)

        self.wait(27)

        # make video follow a curve
        self.play(ScaleInPlace(self.video1, 0.3), run_time=1)
        self.play(self.video1.animate.move_to(ORIGIN + UP), run_time=1)


        # make a graph
        ax = Axes(
            x_range=[0, 10, 1],
            x_length=9,
            y_range=[0, 20, 5],
            y_length=6,
            axis_config={"include_numbers": True, "include_tip": False},

        ).to_edge(DL + RIGHT + UP, buff=1).scale(0.7)

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
        self.play(x.animate.set_value(0), dx.animate.set_value(0.001), run_time=2, rate_func=linear)
        # move video to be on the secant line and follow it
        self.play(self.video1.animate.move_to(ax.c2p(0, func.underlying_function(0))),
                  run_time=2
                  )
        # add updater so that the video follows the secant line
        # update rotation based on atan2(dy, dx)
        self.total_angle = 0

        def video_updater(m):
            x1 = x.get_value()
            x2 = x1 + dx.get_value()
            y1 = func.underlying_function(x1)
            y2 = func.underlying_function(x2)
            point_1: np.ndarray = ax.c2p(x1, y1)
            graph_x1, graph_y1 = point_1[0], point_1[1]
            point_2 = ax.c2p(x2, y2)
            graph_x2, graph_y2 = point_2[0], point_2[1]
            angle = np.arctan2(graph_y2 - graph_y1, graph_x2 - graph_x1)

            # angle_multiplier = 1 if self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES) - 30 < 1996 else 1
            # m.move_to(ax.c2p(x1, y1))
            m.rotate((angle - self.total_angle), about_point=m.get_center())
            self.total_angle += (angle - self.total_angle)

            m.move_to(ax.c2p(x1, y1) + (ax.c2p(x2, y2) - ax.c2p(x1, y1)) / 2)
            # add half the image's height to the axis perpendicular to the tangent point and move the image there

        self.video1.add_updater(video_updater)
        self.play(x.animate.set_value(10), run_time=3, rate_func=rush_into)
        self.video1.clear_updaters()
        self.video1.set_x(100)
        self.video1.set_y(300)
        x.set_value(1000)
        # axes should disappear into bottom left to create sense of motion
        self.play(VGroup(ax, title, func, dot1, dot2, secant).animate.move_to(ax.c2p(-100, -4000)), run_time=0.5)
        # self.play(Uncreate(VGroup(ax, title, func, dot1, dot2, secant)), run_time=0.5)
        # land after jumping into the air
        # ascent
        self.play(self.video1.animate.move_to(ORIGIN + RIGHT * 2),
                  run_time=2, rate_func=rush_from)
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 2), run_time = 1, rate_func=there_and_back)
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 2), run_time=1, rate_func=smooth)

        # apex
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 1.5 + UP * 8), run_time=1, rate_func=smooth)
        self.play(self.video1.animate.rotate(-2 * self.total_angle),  run_time=0.05,
                  )
        self.play(self.video1.animate.move_to(ORIGIN + RIGHT * 1.5 + UP * 8), run_time=0.25, rate_func=smooth)
        self.play(self.video1.animate.move_to(ORIGIN + RIGHT * 2), run_time=1, rate_func=smooth)

        # descent
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 2), run_time=1.5, rate_func=there_and_back)
        self.play(self.video1.animate.move_to(ORIGIN), run_time=1, rate_func=smooth)
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 1 + UP * 20), run_time=1, rate_func=smooth)
        self.play(self.video1.animate.move_to(ORIGIN + DOWN * 10), run_time=0.5)
        
        # back to origin
        self.play(self.video1.animate.move_to(ORIGIN), run_time=0.5, rate_func=rush_from)
        self.play(self.video1.animate.rotate(self.total_angle), run_time=0.5, rate_func=lingering)

        self.play(self.video1.animate.scale(3), run_time=1.5)

        # show center of mass of the video
        # load centers of mass from centerofmasses.json

        # after
        with open("centerofmasses.json", "r") as f:
            centerofmasses = json.load(f)
        # create text and dot to show center of mass
        top_right = self.video1.get_corner(UR)
        bottom_left = self.video1.get_corner(DL)
        min_x = bottom_left[0]
        max_x = top_right[0]
        min_y = bottom_left[1]
        max_y = top_right[1]
        com_dot = Dot().set_color(YELLOW)
        
        def com_updater(m):
            frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
            cx = centerofmasses[str(frame)][0]
            cy = centerofmasses[str(frame)][1]
            # convert cx and cy to coordinates according to the video's coordinates
            # get origin of the video
        
            # convert cx and cy to coordinates in the video's coordinate system
            x_normalized = cx / 960
            y_normalized = (720 - cy) / 720
            cx = x_normalized * (max_x - min_x) + min_x
            cy = y_normalized * (max_y - min_y) + min_y
            m.move_to([cx, cy, 0])
        
        def update_com_text():
            frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
            cx = centerofmasses[str(frame)][0]
            cy = centerofmasses[str(frame)][1]
            return Text(f"Center of mass: {cx:.1f} {cy:.1f}", font_size=24).to_edge(DL).set_color(YELLOW)
        
        com_text = always_redraw(
            update_com_text
        )
        
        # # add updater to scene
        com_dot.add_updater(com_updater)
        self.play(Write(com_dot))
        self.add(com_text)
        # move the dot to the center of mass
        # create updater to move the dot and update the text based on the current frame of the video
        
        
        self.wait(50)
