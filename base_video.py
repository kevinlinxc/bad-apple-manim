import manim
from manim import *
# make the video only, to be used in main_advanced.py


class BadApple1261CirclesThickFillCentered(Scene):
    def construct(self):
        svg_group = []
        for i in range(6572):
            if 363 <= i <= 800:
                svg_path = f"svgs_border_circles/{i}.svg" # circle filled frames
            else:
                svg_path = f"svgs_border_2/{i}.svg"
            if i > 1261:
                stroke_width = 5
            else:
                stroke_width = 2
            if 3329 <= i:
                fill_color = manim.DARK_BLUE
            else:
                fill_color = None
            svg = SVGMobject(svg_path, fill_color=fill_color, stroke_color=manim.DARK_BLUE,stroke_width=stroke_width).scale_to_fit_height(7.9)
            svg.move_to(ORIGIN)
            # remove the rect around the svg, which is in every svg
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
