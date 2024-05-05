# Voice

Using https://github.com/voicepaw/so-vits-svc-fork to make 3B1B sing
Bad Apple in japanese.

Steps I took

1. Install https://github.com/Anjok07/ultimatevocalremovergui/releases/tag/v5.6
2. Download a 3b1b video and remove the background audio
3. Follow svc instructions: place the audio in dataset_raw_raw/3b1b/file_name.wav
4. Run `svc pre-split` to split the long file
5. 
```
svc pre-resample
svc pre-config
svc pre-hubert -fm crepe
svc train -t
```

```
python -m pip install --user pipx
python -m pipx ensurepath
pipx install so-vits-svc-fork --python=3.10
pipx inject so-vits-svc-fork torch torchaudio --pip-args="--upgrade" --index-url=https://download.pytorch.org/whl/cu121 # https://download.pytorch.org/whl/nightly/cu121
svcg
```

Extra notes:
  - The hubert `crepe` mode made my GPU crash during training, dio worked for some reason
  - Lowering the batch size may have helped with stability
  - Don't install using pipx, just use pip - pipx makes it harder to change the source files in my opinion
  - If you don't have a GPU, you could train on Colab, but I only trained 300 out of the 9999 epochs in a day so it would take forever
