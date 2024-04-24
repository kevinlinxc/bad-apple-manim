import manim
from manim import *


class BadApple(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 960, 100],
            y_range=[0, 720, 100]
        ).add_coordinates()
        labels = ax.get_axis_labels("x", "y")
        self.play(Write(VGroup(ax, labels)))

        svg_group = []
        for i in range(6572):
            svg_path = f"svgs_border_2/{i}.svg"  # Assuming SVG files are named as "0.svg", "1.svg", etc. in the "svg_files" directory
            svg = (SVGMobject(svg_path, fill_color=None, stroke_color=manim.DARK_BLUE,stroke_width=2)
                   .scale_to_fit_height(ax.coords_to_point(960, 720)[1])).scale(2.1)
            # remove the rect around the svg, which is in every svg
            svg.move_to(ax.coords_to_point(960/2+25, 720/2+45))  # Offset by 50 in x and y
            svg = svg[:-1]

            svg_group.append(svg)

        self.play(Create(svg_group[0]))
        for index, svg in enumerate(svg_group):
            if index == 0:
                continue
            self.remove(svg_group[index-1])
            self.add(svg)
            self.wait(1/30)
            self.remove(svg)
