# bad-apple-manim

Recreating Bad Apple in the style of a 3Blue1Brown video.

Final video: https://www.youtube.com/watch?v=t0N0dZTsn-w

## Making the video:
`video_to_svg.ipynb` does the following:
- Uses OpenCV to convert the original Bad Apple video into a series of PNG files.
- Uses PIL to convert the PNGs into bitmaps
- Uses potrace (not `pypotrace`, the Python library was a nightmare) to convert the bitmaps into SVGs
- Adds a rectangle around each SVG frame to fix Manim's auto-scaling

Then, `base_video.py` uses [Manim](https://github.com/ManimCommunity/manim) (3b1b's animation library) to render the SVGs into a video. 

The command to render is `manim -pqh base_video.py BadApple1261CirclesThickFillCentered --disable_caching`.

This renders a preliminary video, to save time with processing for the greater video which has other effects.

The other video is rendered from `main_advanced.py`, using `manim -pqh main_advanced.py MyScene`, this is the one with all the mathematical effects like the 
differentiation, integration, fourier series, and vector fields.

Some other stuff in the order that they were used:
- I used https://github.com/xnx/circle-packing to generate the circle packing for level 2.
- `quote.py`: used to render the quote at the beginning of the video
- `center_of_masses.ipynb`: used to pre-compute the center of masses of every frame to use in level 5
- `fourier_series.ipynb`: used to test the Fourier Series using the coordinate system of the video, for level 4
- `efield-precompute.py`: used to precompute the electric field vectors for the main video in level 6.
- `lorentz-coulomb.ipynb` and `lorentz-coulomb.py`: used to render the last section of the video, level 7. This particular section made me use finite difference methods and the Lienard-Wiechart potentials from Griffith's Electrodynamics book, which was simultaneously really fun and really hard.
- I tried doing a section with optical flow (`optical_flow_test.py`), but the algorithms didn't work well with the two-colored videos.

## Making the audio:
- I split Bad Apple's audio into Vocals using a combination of [mvsep.com](mvsep.com) and [Ultimate Vocal Remover](https://ultimatevocalremover.com/). Both are free.
- I created a model of 3b1b's voice using [so-vits-svc-fork](https://github.com/voicepaw/so-vits-svc-fork). 
- Slapped it all together in Premiere Pro.