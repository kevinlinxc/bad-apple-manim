from manim import *

class MyScene(Scene):
    def construct(self):
        # Create first line
        line1 = Text("\"夢見てる？なにも見てない\n 語るも無駄な 自分の言葉?\"", font="Meiryo", t2c={"語るも無駄な 自分の言葉?": BLUE}).scale(0.5)
        line1.move_to(UP*2)

        # Create second line
        line2 = Text("\"Am I dreaming? Do I see nothing? \nIs it just useless to speak my words?\"", font="Times New Roman",
                     t2c={"Is it just useless to speak my words?": BLUE}).scale(0.5)
        line2.move_to(UP*0.7)

        # Add lines to scene
        self.add(line1)
        self.wait(1)
        self.play(Write(line2))
        self.wait(1)

        # Create placeholder name
        name = Text("- A.I. 3Blue1Brown", font="Arial", color=YELLOW).scale(0.5)
        name.next_to(line2, DOWN)

        # Add name to scene
        self.play(Write(name, run_time=0.5))
        self.wait(1)