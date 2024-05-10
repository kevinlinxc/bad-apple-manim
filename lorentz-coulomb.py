"""
Create a 3D scene with the Electric field vector field of a moving point charge, using the centroid
of the video as the moving charge. Uses finite difference approximations for velocity, acceleration, and then
the Lienard-Wiechert derived E-field to calculate the field due to a point charge.
"""
from manim import *
import json

class MyScene(ThreeDScene):

    def construct(self):
        axes = ThreeDAxes()
        # use pos, vel, acc calculated in lorentz-coulomb.ipynb using finite difference methods
        pos_vel_acc = json.load(open("pos_vel_acc_z_sin.json", "r"))
        university_status = Text("Level 7: 4th Year Uni", font_size=20).to_edge(DL).set_color(YELLOW)
        self.add_fixed_in_frame_mobjects(university_status)

        self.add(axes)

        self.begin_ambient_camera_rotation(90 * DEGREES, about='phi')
        self.begin_ambient_camera_rotation(90 * DEGREES / 3, about='theta')
        self.wait(0.7)
        self.stop_ambient_camera_rotation("phi")
        self.stop_ambient_camera_rotation("theta")

        pos_vel_acc = json.load(open("pos_vel_acc_z_sin.json", "r"))
        c_light = 4  # ah yes, the speed of light, 4
        k = 8.9875517873681764e9
        q_charge = 5.60217662e-11  # fake, adjusted to get the desired visuals

        def E(x, y, t):
            # Electric field due to moving point charge, at any observation point x, y, at time t,
            # following Griffiths eq 10.72
            distance = np.sqrt(x**2 + y**2)
            retarded_time = t - distance / c_light
            # interpolate between the two closest points
            ceil_index = int(np.ceil(retarded_time  * 30))
            floor_index = int(np.floor(retarded_time * 30))
            ceil_index = str(ceil_index)
            floor_index = str(floor_index)
            # find the closest index in time, interpolate if needed
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
        self.wait((6700-5472)/30, frozen_frame=False)
