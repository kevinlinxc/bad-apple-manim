import cv2

vid = cv2.VideoCapture("bad-apple.mp4")
ret, image = vid.read()

frame_num = 0
while ret:
    # write as pngs to frames directory
    if frame_num % 10 == 0 or frame_num == 0 or frame_num == (vid.get(cv2.CAP_PROP_FRAME_COUNT) - 1):
        print(f"frame_num = {frame_num}")
    cv2.imwrite(f"frames/{frame_num}.png", image)
    ret, image = vid.read()
    frame_num += 1
