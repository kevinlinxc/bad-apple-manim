from manim import *
import json
import cv2

class MyScene(ThreeDScene):

    def construct(self):
        axes = ThreeDAxes()
        # values calculated in center_of_masses.ipynb
        left_crop_percent = 0.12763466042154567 
        right_crop_percent = 0.8723653395784543
        top_crop_percent = 0.0020833333333333333
        bottom_crop_percent = 0.9958333333333333
        # add invisible rotating square
        min_x= -6.75555555555557                                                                                                                                                                  
        max_x=6.75555555555557
        min_y=-3.8
        max_y=3.8
        
        # placeholder_rectangle = Rectangle(width=max_x-min_x, height=max_y-min_y)

        # self.add(placeholder_rectangle)
        with open("centerofmasses.json", "r") as f:
            centerofmasses = json.load(f)
        # create text and dot to show center of mass
        # top_right = placeholder_rectangle.get_corner(UR)
        # bottom_left = placeholder_rectangle.get_corner(DL)
        # min_x = bottom_left[0]
        # max_x = top_right[0]
        # min_y = bottom_left[1]
        # max_y = top_right[1]

        # print(f"min_x={min_x}\nmax_x={max_x}\nmin_y={min_y}\nmax_y={max_y}")
        # com_dot = Dot().set_color(YELLOW)
        # vel_arrow = Arrow(ORIGIN, RIGHT).set_color(YELLOW)
        pos_vel_acc = json.load(open("pos_vel_acc_z_sin.json", "r"))
        university_status = Text("Level 7: 4th Year Uni", font_size=20).to_edge(DL).set_color(YELLOW)
        self.add_fixed_in_frame_mobjects(university_status)


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
            time = self.renderer.time
            frame = int(time * 30)
            position = pos_vel_acc[str(frame)]["position"]
            cx = position[0]
            cy = position[1]
            cz = position[2]
            m.move_to([cx, cy, cz])
        
        
        def update_com_text():
            time = self.renderer.time
            frame = int(time * 30)
            cx = centerofmasses[str(frame)][0]
            cy = centerofmasses[str(frame)][1]
            return Text(f"Frame: {frame} Center of mass: {cx:.1f} {cy:.1f}", font_size=24).to_edge(DOWN).set_color(YELLOW)
        
        # com_text = always_redraw(
        #     update_com_text
        # )
        
        # # # add updater to scene
        # com_dot.add_updater(com_updater)
        # # self.add(com_text)
        # self.add(com_dot)
        self.add(axes)
        # self.add(vel_arrow)

        self.begin_ambient_camera_rotation(90 * DEGREES , about='phi')
        self.begin_ambient_camera_rotation(90 * DEGREES / 3, about='theta')
        self.wait(0.7)
        self.stop_ambient_camera_rotation("phi")
        self.stop_ambient_camera_rotation("theta")

        ####
        pos_vel_acc = json.load(open("pos_vel_acc_z_sin.json", "r"))
        c_light = 4 # ah yes
        k = 8.9875517873681764e9
        q_charge = 5.60217662e-11 # fake
        def E(x, y, t):
            # Electric field due to moving point charge, following Griffiths eq 10.72
            distance = np.sqrt(x**2 + y**2)
            retarded_time = t - distance / c_light
            # interpolate between the two closest points
            ceil_index = int(np.ceil(retarded_time  * 30))
            floor_index = int(np.floor(retarded_time * 30))
            ceil_index = str(ceil_index)
            floor_index = str(floor_index)
            try:
                if ceil_index == floor_index:
                    position = np.array(pos_vel_acc[floor_index]["position"])
                    velocity = np.array(pos_vel_acc[floor_index]["velocity"])
                    acceleration = np.array(pos_vel_acc[floor_index]["acceleration"])
                else:
                    position = 1/2 * (np.array(pos_vel_acc[floor_index]["position"]) + np.array(pos_vel_acc[ceil_index]["position"]))
                    velocity = 1/2 * (np.array(pos_vel_acc[floor_index]["velocity"]) + np.array(pos_vel_acc[ceil_index]["velocity"]))
                    acceleration = 1/2 * (np.array(pos_vel_acc[floor_index]["acceleration"]) + np.array(pos_vel_acc[ceil_index]["acceleration"]))
            except KeyError:
                # time is before first frame
                position = np.array(pos_vel_acc["0"]["position"])
                velocity = np.array(pos_vel_acc["0"]["velocity"])
                acceleration = np.array(pos_vel_acc["0"]["acceleration"])
            w = np.array(position)
            v = np.array(velocity)
            a = np.array(acceleration)

            curly_r = np.array([x, y, 0]) - w
            curly_r_hat = curly_r / np.linalg.norm(curly_r)
            u = c_light * curly_r_hat - v
            curly_r_norm = np.linalg.norm(curly_r)
            # divide by dot product of curly r and u cubed
            constant_out_front = k * q_charge * curly_r_norm / np.dot(curly_r, u)**3
            v_magnitude = np.linalg.norm(v)
            vector_term = (c_light**2 - v_magnitude**2) * u + np.cross(curly_r, np.cross(u, a))
            return constant_out_front * vector_term
        ####

        def get_e_vector(pos):
            x, y, _ = pos
            e_field = E(x, y, self.renderer.time + 5472/30)
            # print(e_field)
            return e_field
    
        def get_vector_field():
            return ArrowVectorField(get_e_vector,
                                    x_range=[-15, 8, 0.5], y_range=[-8, 17, 0.5],
                                    )

        vec_field = always_redraw(get_vector_field)
        self.add(vec_field)
        # self.wait(10, frozen_frame=False)
        self.wait((6700-5472)/30, frozen_frame=False)
        # self.wait(10, frozen_frame=False)