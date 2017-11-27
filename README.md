# RummyDetection
## Introduction
RummyDetection is a Python tool which can automatically detect rummikub tiles
in an image. Its purpose is to use it to automatically generate the input files
for [RummySolver](https://github.com/nachogoro/RummySolver).

It can generate both types of input files, and attempts to detect whether
something looks off to make sure the user double-checks the results.

## Acknowledgements
This tool draws heavily from [this
tutorial](https://github.com/MicrocontrollersAndMore/OpenCV_3_License_Plate_Recognition_Python)
on detecting license plates by `MicrocontrollersAndMore`.

## Building the tool
This project requires the Python bindings for OpenCV 3. It is highly
recommended to use virtual environments for this. A very thorough guide to
install OpenCV for Python in Ubuntu can be found in
[PyImageSearch](https://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/).

Once that is set up, clone this git directory and ensure it has access to
OpenCV by creating a symbolic link for the OpenCV shared object from the base
OpenCV environment's site-packages into this one's. Then, install the necessary
libraries from `requirements.txt` with `pip install -r requirements.txt` and
you are ready to go!

## Using the tool
```
python3 Main.py [-h] -i IMAGE -m {deck,table} [-o OUTPUT] -c CANON_DIR

Optional arguments:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        Path to the image to be scanned
  -m {deck,table}, --mode {deck,table}
                        Whether the image represents a player's deck or the
                        table
  -o OUTPUT, --output OUTPUT
                        The output directory. If none is specified, it outputs
                        to the screen
  -c CANON_DIR, --canon_dir CANON_DIR
                        The directory containing binary images of each digit
```

The script requires three mandatory arguments:
* `--image`: the image to be scanned for tiles.
* `--mode`: whether the image represents a player's deck or the table. It will
  define the format of the output.
* `--canon_dir`: a directory containing a binarized version of each digit. It
  is used to increase the accuracy of the estimates.

Some sample images are provided in `examples/`.

If the user in interested in the intermediate steps leading to the final
result, they can be visualized by setting `show_steps` to `True` inside
`Main.py`.

For more information on the output format, refer to
[RummySolver](https://github.com/nachogoro/RummySolver).

## About KNN
This repository contains some precomputed training data for KNN, so it can be
used off-the-shelf. However, retraining is possible by using `GenerateData.py`,
which requires a binarized image containing all characters that need to be
detected. See [this
tutorial](https://github.com/MicrocontrollersAndMore/OpenCV_3_KNN_Character_Recognition_Python)
for more information.
