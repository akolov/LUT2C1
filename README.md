# LUT2C1

### Prerequisite

Before using this tool, ensure you have [OpenColorIO](https://opencolorio.org/) installed. You can install it via Homebrew with the following command:

```sh
brew install opencolorio
```

### Film Curve Options

The film curves used with the `--fcrv` argument can be found in the following directory (for macOS users):

```sh
ls /Applications/Capture\ One.app/Contents/Frameworks/ImageProcessing.framework/Versions/A/Resources/FilmCurves
```

### Example

```sh
python3 lut2c1.py --fcrv "FujiGFX100II-Film Standard" ~/Downloads/LUTs
```
