from manim import *

class MyScene(ThreeDScene):

    def construct(self):
        axes = ThreeDAxes()
        labels = axes.get_axis_labels()
        self.add(axes)

        self.begin_ambient_camera_rotation(90 * DEGREES , about='phi')
        self.begin_ambient_camera_rotation(90 * DEGREES / 3, about='theta')
        self.wait(0.7)
        self.stop_ambient_camera_rotation("phi")
        self.stop_ambient_camera_rotation("theta")
        self.wait(10)