from manim import *
import cv2
from dataclasses import dataclass
from PIL import Image, ImageOps
import json
from pathlib import Path


@dataclass
class VideoStatus:
    time: float = 0
    videoObject: cv2.VideoCapture = None

    def __deepcopy__(self, memo):
        return self


class VideoMobject(ImageMobject):
    '''
    Video Manim Object
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

    def __init__(self, filename=None, imageops=None, speed=1.0, loop=False, offset_frames = 0, **kwargs):
        self.filename = filename
        self.imageops = imageops
        self.speed = speed
        self.loop = loop
        self._id = id(self)
        self.status = VideoStatus()
        self.status.videoObject = cv2.VideoCapture(filename)
        self.frame = None
        self.offset_frames = offset_frames

        self.status.videoObject.set(cv2.CAP_PROP_POS_FRAMES, offset_frames+1)
        ret, frame = self.status.videoObject.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame = frame
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



class MyScene(ThreeDScene):
    def wait_until_frame(self, frame_number):
        current_frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
        self.wait((frame_number - current_frame) / 30)

    def construct(self):
        # SECTION 1: JUST PLAY THE VIDEO
        ax = Axes(
            x_range=[0, 960, 100],
            y_range=[0, 720, 100]
        ).add_coordinates()
        labels = ax.get_axis_labels("x", "y")
        # self.play(Write(VGroup(ax, labels)))
        # math_level_text = Text("Kindergarten", font_size=24).to_edge(DL).set_color(YELLOW)
        # start playing video

        self.video1 = VideoMobject(
            filename= str(Path("videos") / "BadApple1261CirclesThickFillCentered.mp4"),
            speed=1.0
        ).scale_to_fit_height(ax.coords_to_point(960, 720)[1]).scale(2.1)

        def frame_updater(mobj: VideoMobject, dt):
            """Update the video's frame every time the scene is rendered. Use self.renderer.time instead of dt
            because dt can be non-linear when the video is moving, possible due to the deepcopy of the VideoStatus"""
            if dt == 0:
                return
            status = mobj.status
            status.time = self.renderer.time - 1
            closest_frame = int(status.time * mobj.status.videoObject.get(cv2.CAP_PROP_FPS))
            mobj.status.videoObject.set(cv2.CAP_PROP_POS_FRAMES, mobj.offset_frames + closest_frame)
            ret, frame = mobj.status.videoObject.read()
            if (ret == False) and mobj.loop:
                status.time = 0
                mobj.status.videoObject.set(cv2.CAP_PROP_POS_MSEC, status.time)
                ret, frame = mobj.status.videoObject.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mobj.frame = frame
                img = Image.fromarray(frame)

                if mobj.imageops != None:
                    img = mobj.imageops(img)
                mobj.pixel_array = change_to_rgba_array(
                    np.asarray(img), mobj.pixel_array_dtype
                )
        self.video1.add_updater(frame_updater)
        self.video1.move_to(ax.coords_to_point(960 / 2 + 25, 720 / 2 + 45))

        # frame number tracker for debugging purposes
        frame_count = Integer(number=0, color=YELLOW).move_to(RIGHT * 4.2 + UP * 2.5)

        def update_frame_text(mobject):
            mobject.set_value(int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30)
        frame_count.add_updater(update_frame_text)
        self.play(Create(VGroup(ax, labels)))
        v1 = Group(self.video1, frame_count)
        self.add(v1)
        self.wait(440 / 30)

        # hide axes for circle frames and trail frames
        self.play(Unwrite(VGroup(ax, labels), run_time=0.5))
        self.wait(0.5)

        self.wait(27)

        # SECTION 2: DIFFERENTIAL CALCULUS
        # make video follow a curve
        self.play(self.video1.animate.scale(0.3).move_to(ORIGIN + UP), run_time=1)
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
        # update rotation based on atan2(dy, dx)
        self.total_angle = 0

        def video_secant_updater(m):
            """
            Update video's position and rotation based on the secant line's slope.
            Note: use the secant line's slope, not the function's slope, they're difference if dimensions are not isotropic.
            """
            x1 = x.get_value()
            x2 = x1 + dx.get_value()
            y1 = func.underlying_function(x1)
            y2 = func.underlying_function(x2)
            point_1: np.ndarray = ax.c2p(x1, y1)
            graph_x1, graph_y1 = point_1[0], point_1[1]
            point_2 = ax.c2p(x2, y2)
            graph_x2, graph_y2 = point_2[0], point_2[1]
            angle = np.arctan2(graph_y2 - graph_y1, graph_x2 - graph_x1)
            m.rotate((angle - self.total_angle), about_point=m.get_center())
            self.total_angle += (angle - self.total_angle)

            m.move_to(ax.c2p(x1, y1) + (ax.c2p(x2, y2) - ax.c2p(x1, y1)) / 2)
            # add half the image's height to the axis perpendicular to the tangent point and move the image there

        self.video1.add_updater(video_secant_updater)
        self.play(x.animate.set_value(10), run_time=3, rate_func=rush_into)
        self.video1.clear_updaters()
        self.video1.add_updater(frame_updater)

        # SECTION 3: LAUNCHING THE VIDEO FOR FUN
        self.video1.set_x(100)
        self.video1.set_y(300)
        x.set_value(1000)
        # axes should disappear into bottom left to create sense of motion
        self.play(VGroup(ax, title, func, dot1, dot2, secant).animate.move_to(ax.c2p(-100, -4000)), run_time=0.5)
        # remove the always updates for dots and secant
        dot1.clear_updaters()
        dot2.clear_updaters()
        secant.clear_updaters()
        self.remove(dot1, dot2, secant)

        # rising
        self.play(self.video1.animate.move_to(ORIGIN + RIGHT * 2),
                  run_time=1, rate_func=rush_from)
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 2), run_time = 1.5, rate_func=there_and_back)
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 2), run_time=1.5, rate_func=smooth)

        # apex
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 1.5 + UP * 8), run_time=1.5, rate_func=smooth)
        self.play(self.video1.animate.rotate(-2 * self.total_angle),  run_time=0.075,
                  )
        self.play(self.video1.animate.move_to(ORIGIN + RIGHT * 1.5 + UP * 8), run_time=0.25, rate_func=smooth)
        self.play(self.video1.animate.move_to(ORIGIN + RIGHT * 2), run_time=1.5, rate_func=smooth)

        # descent
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 2), run_time=2, rate_func=there_and_back)
        self.play(self.video1.animate.move_to(ORIGIN ), run_time=1, rate_func=smooth)
        self.play(self.video1.animate.move_to(ORIGIN + LEFT * 1 + UP * 20), run_time=1.5, rate_func=smooth)
        self.play(self.video1.animate.move_to(ORIGIN + DOWN * 10), run_time=0.5)
        
        # back to origin
        self.play(self.video1.animate.move_to(ORIGIN), run_time=0.5, rate_func=rush_from)
        self.play(self.video1.animate.rotate(self.total_angle), run_time=0.5, rate_func=lingering)

        self.play(self.video1.animate.scale(3), run_time=1.5)
        self.wait_until_frame(2203)

        # SECTION 4: FOURIER SERIES
        # take a picture using a white rectangle
        rect = Rectangle(height=720, width=960, color=WHITE, fill_opacity=1)
        # take a snapshot and freeze it by clearing its updaters
        video_copy = self.video1.copy()
        video_copy.clear_updaters()
        video_copy.z_index = -1
        self.add(video_copy)
        self.add(rect)

        self.play(FadeOut(rect), run_time=0.5)
        
        self.play(self.video1.animate.move_to(ORIGIN + RIGHT * 5.5 + UP * 3 + OUT).scale_to_fit_width(3), run_time=1.5)
        self.play(video_copy.animate.move_to(ORIGIN + UP * 1.3).scale(0.75), run_time=1.5)
        # add axes centered at the video origin
        ax = Axes().add_coordinates().move_to(ORIGIN)
        labels = ax.get_axis_labels("x", "y")
        #print the locations of the corners on the axis coordinate system for fourier_series.ipynb
        print("fourier top left", ax.p2c(video_copy.get_corner(UL)))
        print("fourier bottom right", ax.p2c(video_copy.get_corner(DR)))
        self.play(Write(VGroup(ax, labels)))

        coordinates = json.load(open('coordinates.json'))
        coords_good = coordinates[25:-25]

        x, y = zip(*coords_good)
        x = np.array(x)
        y = np.array(y)
        tau = (max(x)-min(x))

        def cn(n):
            c = y*np.exp(-1j*2*n*np.pi*x/tau)
            return c.sum()/c.size

        def f(x, Nh):
            Nh = int(Nh)
            f = np.array([2*cn(i)*np.exp(1j*2*i*np.pi*x/tau) if i !=0 else cn(i)*np.exp(1j*2*i*np.pi*x/tau) for i in range(0,Nh+1)])
            return f.sum()
        
        num_fourier_terms = ValueTracker(0)
        current_plot = ax.plot(lambda x: f(x, 0), x_range=[min(x), max(x)], color=YELLOW)
        fourier_status = always_redraw(
            lambda: Text(f"# Fourier Series terms: {int(num_fourier_terms.get_value())}", font_size=24, color=YELLOW).move_to(ORIGIN + DOWN * 3 + LEFT * 5)
        )
        self.play(Create(current_plot), Write(fourier_status))
        for i in range(1, 61):
            num_fourier_terms.set_value(i)
            # animate the colour from #FFFF00 to #FF0000
            green_value = 255 - int(255 * i / 60)
            to_hex = lambda x: f"{x:02X}"
            colour = f"#FF{to_hex(green_value)}00"
            next_plot = ax.plot(lambda x: f(x, i), x_range=[min(x), max(x)], color=colour)
            self.play(ReplacementTransform(current_plot, next_plot, run_time=2/(i+1)))
            current_plot = next_plot
            self.wait(2/(i+1))
        
        self.play(Uncreate(fourier_status), FadeOut(video_copy))
        self.play(VGroup(ax, labels, current_plot).animate.move_to(ORIGIN).scale(1.5), run_time=1.5)
        

        # add riemann rectangles and decrease their width to calculate the integral
        dx = ValueTracker(1)
        # add the riemann rectangles
        riemann = ax.get_riemann_rectangles(
            current_plot,
            x_range=[min(x), max(x)],
            dx=1
        )
        riemann.add_updater(
            lambda m: m.become(ax.get_riemann_rectangles(
                current_plot,
                x_range=[min(x), max(x)],
                dx=dx.get_value()
            ))
        )
        self.play(Write(riemann))
        self.play(dx.animate.set_value(0.05), run_time = 3)
        self.wait(1.5)

        # remove the graph, show the integral
        self.play(Uncreate(riemann), run_time=1)
        integral = ax.get_area(current_plot, x_range=[min(x), max(x)])
        self.play(Create(integral), run_time=1)
        self.wait(2)
        self.play(Uncreate(integral), run_time=1)
        self.wait(1)

        # unload all the axes and graph
        self.play(Unwrite(VGroup(ax, labels, current_plot)), run_time=1)
        # bring the video back
        self.play(self.video1.animate.move_to(ORIGIN).scale_to_fit_width(11), run_time=1.5)
        # print top right and bottom left corner

        # SECTION 5: center of masses
        print("top right", self.video1.get_corner(UR))
        print("bottom left", self.video1.get_corner(DL))
        # values calculated in center_of_masses.ipynb
        left_crop_percent = 0.12763466042154567 
        right_crop_percent = 0.8723653395784543
        top_crop_percent = 0.0020833333333333333
        bottom_crop_percent = 0.9958333333333333
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

        def video_coordinate_to_scene(cx, cy):
            x_length = max_x - min_x
            y_length = max_y - min_y
            video_x_min = min_x + left_crop_percent * x_length
            video_x_max = min_x + right_crop_percent * x_length
            video_y_min = min_y + top_crop_percent * y_length
            video_y_max = min_y + bottom_crop_percent * y_length
            x_normalized = cx / 960 * (video_x_max - video_x_min) + video_x_min
            y_normalized = (720 - cy) / 720 * (video_y_max - video_y_min) + video_y_min
            return x_normalized, y_normalized
        
        def com_updater(m):
            frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 29
            cx = centerofmasses[str(frame)][0]
            cy = centerofmasses[str(frame)][1]
            cx, cy = video_coordinate_to_scene(cx, cy)
            m.move_to([cx, cy, 0])
        
        def update_com_text():
            frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 29
            cx = centerofmasses[str(frame)][0]
            cy = centerofmasses[str(frame)][1]
            return Text(f"Center of mass: {cx:.1f} {cy:.1f}", font_size=24).to_edge(DOWN).set_color(YELLOW)
        
        com_text = always_redraw(
            update_com_text
        )
        
        # # add updater to scene
        com_dot.add_updater(com_updater)
        self.play(Write(com_dot))
        self.add(com_text)

        self.wait_until_frame(4200-60)
        self.play(Uncreate(com_text), Uncreate(com_dot), run_time=1)

        # grow the video
        self.play(self.video1.animate.scale_to_fit_height(8))

        # LAST SECTION: ELECTRIC FIELD VECTORS
        down_left = self.video1.get_corner(DL)
        min_x, min_y = down_left[0], down_left[1]
        top_right = self.video1.get_corner(UR)
        max_x, max_y = top_right[0], top_right[1]

        # adjust min_x and max_x because the video is 12.763466042154567 cropped in from the right and left
        # add dot at -6.5, 3.5
        def get_vector_field():
            frame = self.video1.frame.copy()
            # Find coordinates where pixel values are not equal to zero, these are to be treated as point charges
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            non_black_pixels = np.column_stack(np.where(gray_frame != 0))
            non_black_pixels = non_black_pixels.astype(np.float64) # if I don't do this, it will be ints and the rounding ruins everything
            non_black_pixels[:, 1] = non_black_pixels[:, 1] / 1920 * (max_x - min_x) + min_x
            non_black_pixels[:, 0] = (1080 - non_black_pixels[:, 0]) / 1080 * (max_y - min_y) + min_y


            def get_vector_at_position(pos):
                
                x = pos[0]
                y = pos[1]

                # calculate the field contribution from every non-black pixel
                field = np.array([0, 0], dtype=np.float64)
                dx = -(x - non_black_pixels[:, 1])
                dy = -(y - non_black_pixels[:, 0])

                # Find indices where both dx and dy are not zero, because ohterwise field would be infinite
                valid_indices = np.where((dx != 0) | (dy != 0))

                if len(valid_indices[0]) == 0:
                    return field

                dx = dx[valid_indices]
                dy = dy[valid_indices]
                distances = np.sqrt(dx ** 2 + dy ** 2)

                field_contributions = 0.0001 * np.column_stack((dx, dy)) / distances[:, np.newaxis] ** 3

                field += np.sum(field_contributions, axis=0)
                return field
                

            field = ArrowVectorField(
                lambda pos: get_vector_at_position(pos),
            )
            return field
        
        field = always_redraw(get_vector_field)
        self.play(Create(field), run_time=0.2)
        self.wait_until_frame(6572)
        