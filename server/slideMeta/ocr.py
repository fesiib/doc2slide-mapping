# import the necessary packages
import pytesseract
import argparse
import cv2
# construct the argument parser and parse the arguments}
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
            help="path to input image to be OCR'd")
args = vars(ap.parse_args())

# load the input image and convert it from BGR to RGB channel
# ordering}
image = cv2.imread(args["image"])
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# use Tesseract to OCR the image
text = pytesseract.image_to_data(image)
print(text)


