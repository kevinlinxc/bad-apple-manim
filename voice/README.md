# Voice

Using https://github.com/voicepaw/so-vits-svc-fork to make 3B1B sing
Bad Apple in japanese.

Steps I took:

1. Install svc (I had trouble with their pipx installation, so I instaleld it manually
2. Install https://github.com/Anjok07/ultimatevocalremovergui/releases/tag/v5.6
3. Download a 3b1b video and remove the background audio
4. Follow svc instructions: place the audio in dataset_raw_raw/3b1b/file_name.wav
5. Run `svc pre-split` to split the long file
6. Run the rest of the commands (crepe mode for hubert while training crashed my GPU)
```
svc pre-resample
svc pre-config
svc pre-hubert -fm dio
svc train -t
```
7. Run inference: disable automatic f0 prediction, use crepe for the f0 prediction mode, I think. I set the pitch 
to -12 to lower the octave into 3b1b's probable singing range.

Extra notes:
  - The hubert `crepe` mode made my GPU crash during training, dio worked for some reason
  - Lowering the batch size may have helped with stability
  - Don't install using pipx, just use pip - pipx makes it harder to change the source files in my opinion
  - If you don't have a GPU, you could train on Colab, but I only trained 300 out of the 9999 epochs in a day so it would take forever

