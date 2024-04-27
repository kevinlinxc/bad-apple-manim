import manim
from manim import *
import cv2
from dataclasses import dataclass
from PIL import Image, ImageOps


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
        self.speed    = speed
        self.loop     = loop
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
        status.time += 1000*dt*mobj.speed
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

        video1 = VideoMobject(
            filename="BadApple-full-frame.mp4",
            speed=1.0
        ).scale_to_fit_height(ax.coords_to_point(960, 720)[1]).scale(2.1)
        video1.move_to(ax.coords_to_point(960/2+25, 720/2+45))
        v1 = Group(video1, ax, labels)
        # rotate them so that the z axis is up

        # move the camera
        self.add(v1)
        self.wait(440/30)
        self.play(Unwrite(VGroup(ax, labels), run_time=0.5))
        self.wait(0.5)
        self.play(self.camera.phi_tracker.animate.set_value(45 * DEGREES), run_time=3
                  )
        self.play(
            self.camera.theta_tracker.animate.set_value((-90 + 45) * DEGREES), run_time=3
        )
        self.play(
            self.camera.theta_tracker.animate.set_value(5), run_time=3
        )
        self.play(
            self.camera.gamma_tracker.animate.set_value(0 * DEGREES),
            self.camera.phi_tracker.animate.set_value(0 * DEGREES),
            self.camera.theta_tracker.animate.set_value(-90 * DEGREES), run_time=3
        )
        self.wait(20)






