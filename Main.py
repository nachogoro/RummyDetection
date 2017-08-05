# import the necessary packages
import imutils
import argparse
import cv2
import DetectTiles
import DetectDigits
import ResultGenerator

show_steps = False
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)

def main():
    # Construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
                    help="Path to the image to be scanned")
    ap.add_argument('-m', '--mode', required=True, choices=['deck', 'table'],
                    help='Whether the image represents a player\'s deck or the'
                    ' table')
    ap.add_argument('-o', '--output', required=False,
                    help='The output directory. If none is specified, it'
                    ' outputs to the screen')
    ap.add_argument('-c', '--canon_dir', required=True,
                    help='The directory containing binary images of each digit')
    args = vars(ap.parse_args())

    bln_KNN_training_successful = DetectDigits.load_and_train_KNN()

    if not bln_KNN_training_successful:
        print('Error: KNN traning was not successful')
        return

    # Load the image and compute the ratio of the old height
    # to the new height, clone it, and resize it
    image = cv2.imread(args["image"])
    image = imutils.resize(image, height=500)

    if image is None:
        print('Error: image not read from file')
        return

    if show_steps:
        cv2.imshow('0', image)
        cv2.waitKey(0)

    tiles = DetectTiles.detect_tiles_in_image(image, args["canon_dir"])

    if args['mode'] == 'deck':
        ResultGenerator.write_deck(tiles, args['output'])
    else:
        ResultGenerator.write_table(tiles, args['output'])


if __name__ == '__main__':
    main()
