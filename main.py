import manim
from manim import *
# make the video only, to be used in main_advanced.py


class BadApple1261Circles(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 960, 100],
            y_range=[0, 720, 100]
        ).add_coordinates()
        # labels = ax.get_axis_labels("x", "y")
        # self.play(Write(VGroup(ax, labels)))

        svg_group = []
        for i in range(6572):
            if 363 <= i <= 800:
                svg_path = f"svgs_border_circles/{i}.svg" # circle filled frames
            else:
                svg_path = f"svgs_border_2/{i}.svg"  # Assuming SVG files are named as "0.svg", "1.svg", etc. in the "svg_files" directory
            svg = (SVGMobject(svg_path, fill_color=None, stroke_color=manim.DARK_BLUE,stroke_width=2)
                   .scale_to_fit_height(ax.coords_to_point(960, 720)[1])).scale(2.57)
            # remove the rect around the svg, which is in every svg
            svg.move_to(ax.coords_to_point(960/2-14, 720/2-14))  # Offset by 50 in x and y
            svg = svg[:-1]

            svg_group.append(svg)

        self.play(Create(svg_group[0]))
        for index, svg in enumerate(svg_group):
            if index == 0:
                continue
            if 793 < index < 1261:
                self.play(Transform(svg_group[index - 1], svg, run_time=1 / 30))
            else:
                if index == 1261:
                    for i in range(793, 1261):
                        self.remove(svg_group[i])
                self.remove(svg_group[index-1])
                self.add(svg)
                self.wait(1/30)
                self.remove(svg)
