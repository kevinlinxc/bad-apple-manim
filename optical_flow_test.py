from manim import *
import cv2
import numpy as np

class OpticalFlowAnimation(Scene):
    def construct(self):
        # Grid parameters
        rows = 10
        cols = 10
        grid_spacing = 0.2
        grid_size = 5

        # Load frames
        frames = [cv2.imread(f'frames/{i}.png', cv2.IMREAD_GRAYSCALE) for i in range(6572)]

        # Iterate over frames and compute optical flow
        for i in range(len(frames) - 1):
            flow = cv2.calcOpticalFlowFarneback(frames[i], frames[i + 1], None, 0.5, 3, 15, 3, 5, 1.2, 0)
            
            # Create grid of points
            points = []
            for r in range(rows):
                for c in range(cols):
                    points.append([grid_size * (r - rows / 2), grid_size * (c - cols / 2), 0])

            # Compute optical flow at grid points
            flow_vectors = []
            for p in points:
                x, y = int(p[0] + rows / 2), int(p[1] + cols / 2)
                dx, dy = flow[y, x]
                flow_vectors.append((p, [p[0] + dx * grid_spacing, p[1] + dy * grid_spacing, 0]))

            # Create vectors
            vectors = VGroup(*[Arrow(start=v[0], end=v[1], color=BLUE) for v in flow_vectors])

            # Create scene and add vectors
            self.add(vectors)
            self.wait(0.1)  # Adjust speed of animation as needed
            self.remove(vectors)

