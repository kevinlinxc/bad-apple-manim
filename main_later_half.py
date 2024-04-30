
from manim import *
from main_advanced import VideoMobject
import json
import cv2
from PIL import Image

class MyScene(ThreeDScene):
    def wait_until_frame(self, frame_number):
        current_frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
        self.wait((frame_number - current_frame) / 30)

    def construct(self):
        self.video1 = VideoMobject("videos/BadApple1261CirclesThickFillUnfillCentered.mp4", offset_frames=3340)
        self.video1.move_to(ORIGIN).scale_to_fit_height(3.09375*2)
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

        left_crop_percent = 0.12239583333333333
        right_crop_percent = 0.8520833333333333
        top_crop_percent = 0.028703703703703703 
        bottom_crop_percent = 0.9981481481481481
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
            frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
            cx = centerofmasses[str(frame)][0]
            cy = centerofmasses[str(frame)][1]
            cx, cy = video_coordinate_to_scene(cx, cy)
            m.move_to([cx, cy, 0])
        
        def update_com_text():
            frame = int(self.video1.status.videoObject.get(cv2.CAP_PROP_POS_FRAMES)) - 30
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
        self.wait_until_frame(4200-30)
        self.play(Uncreate(com_text), Uncreate(com_dot), run_time=1)

        # grow the video
        self.play(self.video1.animate.scale_to_fit_height(8.2).move_to(ORIGIN + UP *0.125))
        self.wait(10)

        # LAST SECTION: OPTICAL FLOW
        last_frame = self.video1.frame
        # print bounds of the video
        print(self.video1.get_corner(UL))
        print(self.video1.get_corner(DR))

        def get_vector_field():
            frame = self.video1.frame
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            flow = cv2.optflow.calcOpticalFlowSparseToDense(
                last_frame, frame, None
            )



        