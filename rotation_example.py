from manim import *

class MyScene(ThreeDScene):
    def construct(self):
        ax = Axes(
            x_range=[0, 10, 1],
            x_length=9,
            y_range=[0, 20, 5],
            y_length=6,
            axis_config={"include_numbers": True, "include_tip": False},

        ).to_edge(DL + RIGHT + UP, buff=1).scale(0.7)

        title = Text("My Function", font_size=24).next_to(ax, UP)
        func = ax.plot(
            lambda x: 1 / 180 * x ** 2 * (x - 3) ** 2 * (x - 8) ** 2, x_range=[0, 10], color=BLUE
        )

        x = ValueTracker(0)
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
        self.play(Write(VGroup(ax, title)))
        self.play(Create(func))
        self.play(Create(secant))
        self.play(x.animate.set_value(0), dx.animate.set_value(0.1), run_time=4, rate_func=linear)
        # move video to be on the secant line and follow it
        self.video1 = ImageMobject(
            filename_or_array="cat.png",
        ).scale(0.1)
        # self.play(self.video1.animate.move_to(ax.c2p(0, func.underlying_function(0))),
        #           run_time=2
        #           )
        # self.video1.add_updater(lambda m: m.move_to(ax.c2p(x.get_value(), func.underlying_function(x.get_value()))))
        def make_info_text():
            curr_x = x.get_value()
            curr_dx = 0.1
            curr_y = func.underlying_function(curr_x)
            curr_dy = func.underlying_function(curr_x + curr_dx) - curr_y
            angle = np.arctan2(curr_dy, curr_dx)
            ang_deg = angle * 180 / PI
            text = Text(f"{curr_x=}, {curr_y=}, {curr_dx=}, {curr_dy=} {ang_deg}", font_size=24)
            text.move_to(UP * 3)
            return text
        angle_text1 = always_redraw(
            make_info_text
        )
        self.add(angle_text1)
        def video_updater():
            video_1 = ImageMobject(
                filename_or_array="cat.png",
            ).scale(0.1)
            curr_x = x.get_value()
            curr_dx = 0.1
            curr_y = func.underlying_function(curr_x)
            curr_dy = func.underlying_function(curr_x + curr_dx) - curr_y
            angle = np.arctan2(curr_dy, curr_dx)
            video_1.rotate((angle))
            ang_deg = angle * 180 / PI
            # video_1.move_to(ax.c2p(curr_x, curr_y))
            return video_1

        def update_decimal(m):
            curr_x = x.get_value()
            curr_dx = 0.1
            curr_y = func.underlying_function(curr_x)
            curr_dy = func.underlying_function(curr_x + curr_dx) - curr_y
            angle = np.arctan2(curr_dy, curr_dx) * 180 / PI
            m.set_value(angle)

        angle_text1.add_updater(update_decimal)
        self.add(angle_text1)
        angle_text1.move_to(UP * 3)

        cat = always_redraw(video_updater)
        self.remove(self.video1)
        self.add(cat)
        self.play(x.animate.set_value(10), run_time=10, rate_func=linear)
