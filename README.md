# bad-apple-manim

## Making the video:
`video_to_svg.ipynb` does the following:
- Uses OpenCV to convert the original Bad Apple video into a series of PNG files.
- Uses PIL to convert the PNGs into bitmaps
- Uses potrace (not `pypotrace`, the Python library was a nightmare) to convert the bitmaps into SVGs
- Adds a rectangle around each SVG frame to fix Manim's auto-scaling

Then, `main.py` uses [Manim](https://github.com/ManimCommunity/manim) (3b1b's animation library) to render the SVGs into a video. The command to render is `manim -pqh main.py BadApple`


## Making the audio:
- I split Bad Apple's audio into Vocals using a combination of [mvsep.com](mvsep.com) and [Ultimate Vocal Remover](https://ultimatevocalremover.com/). Both are free.
- I created a model of 3b1b's voice using [so-vits-svc-fork](https://github.com/voicepaw/so-vits-svc-fork). This required my GPU and was a nightmare. Tips:
  - The hubert `crepe` mode made my GPU crash during training, dio worked for some reason
  - Lowering the batch size may have helped with stability
  - Don't install using pipx, just use pip - pipx makes it harder to change the source files in my opinion
  - If you don't have a GPU, you could train on Colab, but I only trained 300 out of the 9999 epochs in a day so it would take forever
