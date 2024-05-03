
from manim import *
from main_advanced import VideoMobject
import json
import cv2
from PIL import Image


def get_intersect(a1, a2, b1, b2):
    """
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1, a2, b1, b2])  # s for stacked
    h = np.hstack((s, np.ones((4, 1))))  # h for homogeneous
    l1 = np.cross(h[0], h[1])  # get first line
    l2 = np.cross(h[2], h[3])  # get second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return None
    return x / z, y / z


def point_1_to_point_2_in_box(x1, y1, x2, y2, width, height):
    """
    If x2, y2 are in the box, return them.

    Otherwise, return a new x2, y2 that is the intersection of x1, y1 -> x2, y2 and the perimeter of the box
    """
    if 0 <= x2 <= width and 0 <= y2 <= height:
        return x2, y2
    else:
        # check which wall it intersects with
        left = get_intersect([x1, y1], [x2, y2], [0, 0], [0, height])
        if left:
            return left
        top = get_intersect([x1, y1], [x2, y2], [0, 0], [width, 0])
        if top:
            return top
        right = get_intersect([x1, y1], [x2, y2], [width, 0], [width, height])
        if right:
            return right
        bottom = get_intersect([x1, y1], [x2, y2], [0, height], [width, height])
        if bottom:
            return right
        raise Exception("No intersection found, what happened lol")
    
class MyScene(ThreeDScene):
    def wait_until_frame(self, frame_number):
        current_frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
        self.wait((frame_number - current_frame) / 30)

    def construct(self):
        # self.video1 = VideoMobject("videos/BadApple1261CirclesThickFillUnfillCentered.mp4", offset_frames=3340)
        self.video1 = VideoMobject("videos/BadApple1261CirclesThickFillUnfillCentered.mp4", offset_frames=0)

        self.video1.move_to(ORIGIN).scale_to_fit_height(3*1.6)
        self.add(self.video1)
        def frame_updater(mobj: VideoMobject, dt):
            """Update the video's frame every time the scene is rendered. Use self.renderer.time instead of dt
            because dt can be non-linear when the video is moving, possible due to the deepcopy of the VideoStatus"""
            if dt == 0:
                return
            status = mobj.status
            status.time = self.renderer.time
            closest_frame = int(status.time * mobj.status.videoObject.get(cv2.CAP_PROP_FPS))
            mobj.status.videoObject.set(cv2.CAP_PROP_POS_FRAMES, mobj.offset_frames + closest_frame)
            mobj.last_frame = mobj.frame
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

        # with open("centerofmasses.json", "r") as f:
        #     centerofmasses = json.load(f)
        # # create text and dot to show center of mass
        # top_right = self.video1.get_corner(UR)
        # bottom_left = self.video1.get_corner(DL)
        # min_x = bottom_left[0]
        # max_x = top_right[0]
        # min_y = bottom_left[1]
        # max_y = top_right[1]
        # com_dot = Dot().set_color(YELLOW)

        # left_crop_percent = 0.12239583333333333
        # right_crop_percent = 0.8520833333333333
        # top_crop_percent = 0.028703703703703703 
        # bottom_crop_percent = 0.9981481481481481
        # def video_coordinate_to_scene(cx, cy):
        #     x_length = max_x - min_x
        #     y_length = max_y - min_y
        #     video_x_min = min_x + left_crop_percent * x_length
        #     video_x_max = min_x + right_crop_percent * x_length
        #     video_y_min = min_y + top_crop_percent * y_length
        #     video_y_max = min_y + bottom_crop_percent * y_length
        #     x_normalized = cx / 960 * (video_x_max - video_x_min) + video_x_min
        #     y_normalized = (720 - cy) / 720 * (video_y_max - video_y_min) + video_y_min
        #     return x_normalized, y_normalized
        
        # def com_updater(m):
        #     frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
        #     cx = centerofmasses[str(frame)][0]
        #     cy = centerofmasses[str(frame)][1]
        #     cx, cy = video_coordinate_to_scene(cx, cy)
        #     m.move_to([cx, cy, 0])
        
        # def update_com_text():
        #     frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
        #     cx = centerofmasses[str(frame)][0]
        #     cy = centerofmasses[str(frame)][1]
        #     return Text(f"Center of mass: {cx:.1f} {cy:.1f}", font_size=24).to_edge(DOWN).set_color(YELLOW)
        
        # com_text = always_redraw(
        #     update_com_text
        # )
        
        # # # add updater to scene
        # com_dot.add_updater(com_updater)
        # self.play(Write(com_dot))
        # self.add(com_text)
        # self.wait_until_frame(4200-60)
        # self.play(Uncreate(com_text), Uncreate(com_dot), run_time=1)

        # grow the video
        self.play(self.video1.animate.scale_to_fit_height(8).move_to(ORIGIN))

        # LAST SECTION: ELECTRIC FIELD VECTORS
        # print bounds of the video
        down_left = self.video1.get_corner(DL)
        min_x, min_y = down_left[0], down_left[1]
        top_right = self.video1.get_corner(UR)
        max_x, max_y = top_right[0], top_right[1]
        print(f"{max_x=}\n{min_x=}\n{max_y=}\n{min_y=}")

        # adjust min_x and max_x because the video is 12.763466042154567 cropped in from the right and left
        # add dot at -6.5, 3.5
        vector_data = json.load(open("e_fields.json"))

        def get_vector_field():
            # vector fields are precomputed, see efield-precompute.py
            frame_number = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES))
            def get_vector_at_position(pos):
                
                x = pos[0]
                y = pos[1]
                # calculate the field contribution from every non-black pixel
                field = np.array(vector_data[str(frame_number)][f"({x}, {y})"])
                return field
                

            field = ArrowVectorField(
                lambda pos: get_vector_at_position(pos),
                x_range=[-7, 7, 1],
                y_range=[-4, 4, 1],
            )
            return field
        
        field = always_redraw(get_vector_field)
        self.play(Create(field), run_time=0.2)
        self.wait(15)




        