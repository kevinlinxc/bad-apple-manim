import cv2
import numpy as np
import json
e_fields = {}

cap = cv2.VideoCapture("videos/BadApple1261CirclesThickFillCentered.mp4")
max_x = 7.111111111111112                                                                                                                                    
min_x = -7.111111111111112
max_y = 4.0
min_y = -4.0
positions = set()

for x in np.arange(-8.0, 8.0, 1.0):
    for y in np.arange(-4.0, 5.0, 1.0):
        positions.add((x, y))

index = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    all_field = {}
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Find coordinates where pixel values are not equal to zero
    non_black_pixels = np.column_stack(np.where(gray_frame != 0))
    # convert to floats
    non_black_pixels = non_black_pixels.astype(np.float64)
    non_black_pixels[:, 1] = non_black_pixels[:, 1] / 1920 * (max_x - min_x) + min_x
    non_black_pixels[:, 0] = (1080 - non_black_pixels[:, 0]) / 1080 * (max_y - min_y) + min_y
    for x, y in positions:
        field = np.array([0, 0], dtype=np.float64)
        dx = -(x - non_black_pixels[:, 1])
        dy = -(y - non_black_pixels[:, 0])

        distances = np.sqrt(dx ** 2 + dy ** 2)
        if np.any(distances < 0.01):
            all_field[f"({x}, {y})"] = field.tolist()
            continue
        field_contributions = 0.0001 * np.column_stack((dx, dy)) / distances[:, np.newaxis] ** 3

        field += np.sum(field_contributions, axis=0)
        fields_as_list = field.tolist()
        # reduce the precision of the floats
        fields_as_list = [round(x, 5) for x in fields_as_list]
        all_field[f"({x}, {y})"] = fields_as_list
    e_fields[index] = all_field
    index += 1
    if index % 10 == 0:
        print(index)
cap.release()
with open("e_fields.json", "w") as f:
    json.dump(e_fields, f)
        
