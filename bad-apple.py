from manim import *
from manim_svg_animations import *


VMobject.set_default(color=BLACK)


class SceneExample(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        ax = Axes().add_coordinates()
        labels = ax.get_axis_labels("x", "y")
        vg = VGroup(ax, labels)
        parsed = HTMLParsedVMobject(vg, self)
        self.play(Write(VGroup(ax, labels)))
        graph = ax.plot(
            np.log,
            x_range=[np.exp(-4), 7],
            color=RED
        )
        vg.add(graph)
        self.play(Create(graph))
        riemann = ax.get_riemann_rectangles(
            graph,
            x_range=[1, 6],
            dx=1
        )
        vg.add(riemann)
        self.play(Write(riemann))
        dx = ValueTracker(1)
        riemann.add_updater(
            lambda m: m.become(ax.get_riemann_rectangles(
                graph,
                x_range=[1, 6],
                dx=dx.get_value()
            ))
        )
        self.play(dx.animate.set_value(0.1))
        self.wait()
        riemann.clear_updaters()
        self.play(FadeOut(vg))
        banner = ManimBanner(dark_theme=False)
        vg.remove(*vg)
        vg.add(banner)
        self.play(banner.create())
        self.play(banner.expand())
        parsed.finish()