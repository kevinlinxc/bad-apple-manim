from manim import *

class MyScene(ThreeDScene):
    def construct(self):
        self.video1 = ImageMobject(
                filename_or_array="cat.png",
            ).scale_to_fit_height(3)
        ax = Axes(
            x_range=[0, 10, 1],
            x_length=9,
            y_range=[0, 20, 5],
            y_length=6,
            axis_config={"include_numbers": True, "include_tip": False},

        ).to_edge(DL + RIGHT + UP, buff=1).scale(0.7)
        labels = ax.get_axis_labels()

        self.play(Create(VGroup(ax, labels)))
        self.play(FadeIn(self.video1))
        self.wait(3)
        self.move_camera(phi=0*DEGREES, theta= -90 * DEGREES, zoom= 0.7, run_time=0.4, gamma=0*DEGREES)

        self.begin_ambient_camera_rotation(90 * DEGREES / 3, about='phi')
        self.begin_ambient_camera_rotation(90 * DEGREES / 3, about='theta')
        self.wait(3)