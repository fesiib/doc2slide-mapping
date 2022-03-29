import os
import cv2
import numpy as np
import imutils
import json

from scipy import ndimage as ndi

from skimage.metrics import structural_similarity as compare_ssim
from skimage.filters import threshold_otsu, threshold_sauvola, sobel, scharr, rank
from skimage.segmentation import watershed
from skimage import morphology

RESIZE_WIDTH = 500
MIN_AREA = 1000

def __transform_slide_image(slide_image, mask = 1):
    gray = imutils.resize(slide_image, width=RESIZE_WIDTH)
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    #gray = cv2.GaussianBlur(gray, (21, 21), 0)
    gray = gray * mask
    return gray

def __calc_thresh(frame, threshold=25):
    thresh = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)[1]
    return cv2.dilate(thresh, None, iterations=2)

def __detect_contours(thresh):
    cnts = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = cnts[0]
    valid_cnts = []
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < MIN_AREA:
            continue
        valid_cnts.append(c)
    return valid_cnts


def get_slides_segmentation(path, slide_info):

    mask = 1
    th_path = os.path.join(path, "talkingHeadMask.json")

    if os.path.isfile(th_path):
        with open(th_path, "r") as th_file:
            th_json = json.load(fp=th_file)
            mask_rects = th_json["talkingHeadMaskRects"]
            image_size = th_json["imageSize"]["height"], th_json["imageSize"]["width"]
            mask = np.ones(image_size, np.uint8)
            for mask_rect in mask_rects:
                for i in range(mask_rect["top"], mask_rect["bottom"] + 1):
                    for j in range(mask_rect["left"], mask_rect["right"] + 1):
                        mask[i][j] = 0
            mask = imutils.resize(mask, width=RESIZE_WIDTH)

    prev_gray = None

    segments = []
    last_segment_end = -1


    cropped_path = os.path.join(path, 'cropped')
    os.makedirs(cropped_path, exist_ok=True)

    for i, slide in enumerate(slide_info):
        image_path = os.path.join(path, 'images', str(i) + '.jpg')
        slide_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        gray = __transform_slide_image(slide_image)

        h, w = gray.shape

        if prev_gray is None:
            prev_gray = gray
            continue

        score, delta = compare_ssim(gray, prev_gray, full=True)
        delta = (delta * 255).astype(np.uint8)

        # otsu_thresh = threshold_otsu(delta)
        # thresh = delta < otsu_thresh
        # thresh = cv2.threshold(delta, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        thresh = sobel(delta)
        markers = np.zeros_like(delta)
        markers[delta < 30] = 1
        markers[delta > 150] = 2
        thresh = watershed(thresh, markers)
        thresh = (thresh == 1)
        thresh = thresh * mask

        # sauvola_thresh = threshold_sauvola(prev_gray, window_size=15, k=0.2)
        # prev_thresh = prev_gray < sauvola_thresh
        # prev_thresh = prev_thresh * mask

        prev_thresh = sobel(prev_gray)
        # markers = np.zeros_like(prev_thresh)
        # markers[prev_gray < 30] = 1
        # markers[prev_gray > 150] = 2

        # prev_thresh = markers
        # prev_thresh = watershed(prev_thresh, markers)
        prev_thresh = prev_thresh * mask

        total = prev_thresh * thresh

        thresh = (thresh * 255).astype(np.uint8)
        prev_thresh = (prev_thresh * 255).astype(np.uint8)
        total_img = (total * 255).astype(np.uint8)

        cv2.imwrite(os.path.join(cropped_path, "thresh_" + str(i) + '.jpg'), thresh)
        cv2.imwrite(os.path.join(cropped_path, str(i) + '.jpg'), total_img)
        cv2.imwrite(os.path.join(cropped_path, "prev_" + str(i) + '.jpg'), prev_thresh * mask)
        # cv2.imwrite(os.path.join(cropped_path, str(i) + '.jpg'), o_prev)

        total = morphology.erosion(total_img, morphology.disk(1))

        if cv2.countNonZero(total) > 0:
            segments.append({
                "sectionTitle": "Segment #" + str(len(segments)),
                "startSlideIndex": last_segment_end + 1,
                "endSlideIndex": i - 1,
            })
            last_segment_end = i - 1
        prev_gray = gray

    segments.append({
        "sectionTitle": "Segment #" + str(len(segments)),
        "startSlideIndex": last_segment_end + 1,
        "endSlideIndex": len(slide_info) - 1,
    })
    return segments