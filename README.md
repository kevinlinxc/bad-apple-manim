# bad-apple-manim

Recreating Bad Apple in the style of a 3Blue1Brown video.

## Making the video:
`video_to_svg.ipynb` does the following:
- Uses OpenCV to convert the original Bad Apple video into a series of PNG files.
- Uses PIL to convert the PNGs into bitmaps
- Uses potrace (not `pypotrace`, the Python library was a nightmare) to convert the bitmaps into SVGs
- Adds a rectangle around each SVG frame to fix Manim's auto-scaling

Then, `based_video` uses [Manim](https://github.com/ManimCommunity/manim) (3b1b's animation library) to render the SVGs into a video. 

The command to render is `manim -pqh base_video.py BadApple1261CirclesThickFillUnfillCentered --disable_caching`.

This renders a preliminary video, to save time with processing for the greater video which has other effects.

The other video is rendered from `main_advanced.py`, using `manim -pqh main_advanced.py MyScene`, this is the one with all the mathematical effects like the 
differentiation, integration, fourier series, and vector fields.

Some other files:
-`center_of_masses.ipynb`: used to pre-compute the center of masses of every frame to use in the main video
-`fourier_series.ipynb`: used to test the Fourier Series using the coordinate system of the video


## Making the audio:
- I split Bad Apple's audio into Vocals using a combination of [mvsep.com](mvsep.com) and [Ultimate Vocal Remover](https://ultimatevocalremover.com/). Both are free.
- I created a model of 3b1b's voice using [so-vits-svc-fork](https://github.com/voicepaw/so-vits-svc-fork). This required my GPU and was a nightmare. Tips:
  - The hubert `crepe` mode made my GPU crash during training, dio worked for some reason
  - Lowering the batch size may have helped with stability
  - Don't install using pipx, just use pip - pipx makes it harder to change the source files in my opinion
  - If you don't have a GPU, you could train on Colab, but I only trained 300 out of the 9999 epochs in a day so it would take forever
