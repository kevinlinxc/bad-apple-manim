import cv2
import numpy as np
import atexit

import sys

# def trace(frame, event, arg):
#     print("%s, %s:%d" % (event, frame.f_code.co_filename, frame.f_lineno))
#     return trace

# sys.settrace(trace)


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
    

def add_red_gradient_to_image(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold the grayscale image to get a binary mask of the black pixels
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

    # Create a red gradient image
    red_gradient = cv2.imread("red_gradient.png")

    # Apply the binary mask to the red gradient image
    red_gradient[mask != 0] = [0, 0, 0]  # Set non-black pixels to black in the red gradient image

    # Combine the original image and the red gradient image
    result = cv2.add(image, red_gradient)

    return result

def dense_optical_flow(method, video_path, params=[], to_gray=True):
    index = 0
    cap = cv2.VideoCapture(video_path)
    ret, old_frame = cap.read()
    print(old_frame)
    fps = cap.get(cv2.CAP_PROP_FPS)
    height, width = old_frame.shape[:2]
    # resulting video with arrows
    out = cv2.VideoWriter("opt_flow_lucas_arrow_big.mp4", cv2.VideoWriter_fourcc(*"mp4v"), int(fps / 4),
                          (width * 2, height))
    atexit.register(out.release)
    # Preprocessing for exact method
    if to_gray:
        old_frame = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    
    while True:
        index += 1
        print(index)
        ret, new_frame = cap.read()
        # new_frame_red = add_red_gradient_to_image(new_frame)
        # old_frame_red = add_red_gradient_to_image(old_frame)


        frame_copy = new_frame
        if not ret:
            break
        frame_copy_raw = frame_copy.copy()
        # Preprocessing for exact method
        if to_gray:
            new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
        # Calculate Optical Flow
        # invert the images befroe calculating flow
        old_frame_i = cv2.bitwise_not(old_frame)
        new_frame_i = cv2.bitwise_not(new_frame)

        flow = cv2.calcOpticalFlowFarneback(old_frame, new_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # prepare to average flows to get an estimate

        samples = 0
        for x in range(0, width, 30):
            for y in range(0, height, 30):
                samples += 1
                # print(f"start point: {x, y}")
                scale = 1
                # clamp so it doesnt try to draw a line outside of frame, intersection would be better
                end_x = x + scale * flow[y, x, 0]
                end_y = y + scale * flow[y, x, 1]
                # only show the arrow if the start point was not black in the last frame and the end point is not black in this frame
                if 0 < end_x < width and 0 < end_y < height:
                    if np.all(old_frame[y, x] != [0, 0, 0]) and np.all(new_frame[int(end_y), int(end_x)] != [0, 0, 0]):

                        end_x, end_y = point_1_to_point_2_in_box(x, y, end_x, end_y, width, height)
                        end_point = (int(end_x), int(end_y))
                        # print(f"end point: {end_point}")
                        # if you want to see the individual vectors uncommen this
                        # print(f"end point: {end_point}")
                        try:
                            frame_copy = cv2.arrowedLine(frame_copy, (x, y), end_point, (0, 0, 255), 1)
                        except:
                            continue
        # center = width//2, height//2
        # averaged_arrow_scale = 4
        # averaged_x = int(total_x / samples)
        # averaged_y = int(total_y / samples)
        # end_point = (center[0] + averaged_arrow_scale * averaged_x, center[1] + averaged_arrow_scale * averaged_y)
        # end_point = point_1_to_point_2_in_box(*center, *end_point, width, height)
        # frame_copy = cv2.arrowedLine(frame_copy, center, end_point, (0, 0, 255), 1)
        # write magnitude and angle as text on frame_copy
        # magnitude = np.sqrt(averaged_x ** 2 + averaged_y ** 2)
        # cv2.putText(frame_copy, f"mag: {magnitude}", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        # write to video

        show = np.hstack((frame_copy_raw, frame_copy))
        # shrink frame and show it
        show = cv2.resize(show, (int(show.shape[1]), int(show.shape[0])))
        out.write(show)
        # cv2.imshow("frame", show)
        # k = cv2.waitKey(25) & 0xFF
        # if k == 27:
        #     break
        old_frame = new_frame
    out.release()

if __name__ == "__main__":
    video_path = "/Users/kevinlinxc/src/bad-apple-manim/videos/BadApple1261CirclesThickFillUnfillCentered.mp4"
    method = cv2.optflow.calcOpticalFlowSparseToDense
    dense_optical_flow(method, video_path)