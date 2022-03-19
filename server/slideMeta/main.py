import time
import datetime
import os
import argparse
import cv2
import numpy as np
import imutils
import img2pdf
import json

import changedetection
import duplicatehandler

from scenedetect import open_video
from scenedetect import SceneManager
from scenedetect import StatsManager
from scenedetect.detectors import ContentDetector


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", dest="video", required=True,
                    help="the path to your video file to be analyzed")
parser.add_argument("-o", "--output", dest="output", default="slides.pdf",
                    help="the output pdf file where the extracted slides will be saved")
parser.add_argument("-s", "--step-size", dest="step-size", default=10,
                    help="the amount of frames skipped in every iteration")
parser.add_argument("-p", "--progress-interval", dest="progress-interval", default=1,
                    help="how many percent should be skipped between each progress output")
parser.add_argument("-d", "--debug", dest="debug", default=False, action="store_true",
                    help="the path to your video file to be analyzed")
parser.add_argument("--use-stored-mask", dest="use-stored-mask", default=False, action="store_true",
                    help="if already stored masks should be used for processing")

args = vars(parser.parse_args())


class Main:
    def __init__(self, debug, vidpath, output, step_size, progress_interval, use_stored_mask):
        self.slide_counters = {}
        self.vidpath = vidpath
        self.output = output
        self.start_time = 0
        self.detection = changedetection.ChangeDetection(
            step_size, progress_interval, debug)
        self.dup_handler = duplicatehandler.DuplicateHandler(1)
        self.use_stored_mask = use_stored_mask

    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

    # crop image to slide size
    def __crop_image(self, frame):
        return frame

        min_area = (frame.shape[0] * frame.shape[1]) * (2 / 3)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if imutils.is_cv2() else contours[1]

        for cnt in contours:
            if cv2.contourArea(cnt) > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                crop = frame[y:y+h, x:x+w]
                return crop

    def check_ratio(self, frame, min, max):
        ratio = frame.shape[1] / frame.shape[0]
        return ratio >= min and ratio <= max

    def onTrigger(self, frame, title=""):
        frame = self.__crop_image(frame)
        if frame is not None:
            if self.dup_handler.check(frame):
                print("Found a new slide!")
            self.save_slide(frame, title)

    def save_slide(self, slide, title=""):
        parent_path = os.path.join(self.output, "images")
        #parent_path = self.output
        os.makedirs(parent_path, exist_ok=True)

        if not title in self.slide_counters:
            self.slide_counters[title] = 0
        cur_slide = self.slide_counters[title]
        self.slide_counters[title] += 1

        img_path = os.path.join(parent_path, title + str(cur_slide) + ".jpg")
        print("Saving slide " + str(cur_slide) + " to " + img_path + " ...\n")
        cv2.imwrite(img_path, slide)

    def onProgress(self, percent, pos):
        elapsed = time.time() - self.start_time
        eta = (elapsed / percent) * (100 - percent)
        fps = pos / elapsed
        etaString = self.strfdelta(datetime.timedelta(seconds=eta),
                                   "{hours}h {minutes}min {seconds}s")
        print("progress: ~%d%% @ %d fps | about %s left" %
              (percent, fps, etaString))

    def convertToPDF(self):
        imgs = []
        cnt = 0

        for i in self.dup_handler.entries:
            imgs.append(cv2.imencode('.jpg', i)[1].tostring())

        with open(self.output, "wb") as f:
            f.write(img2pdf.convert(imgs))

    def find_scenes(self, threshold=30.0):
        # Create our video & scene managers, then add the detector.
        video_stream = open_video(path=self.vidpath.strip())
        stats_manager = StatsManager()
        scene_manager = SceneManager(stats_manager)
        scene_manager.add_detector(
            ContentDetector(threshold=threshold))

        stats_file_path = os.path.join(self.output, "stats.csv")
        scene_manager.detect_scenes(video=video_stream)
        # Each returned scene is a tuple of the (start, end) timecode.
        scene_list = scene_manager.get_scene_list()

        frame_range = []
        fps = video_stream.frame_rate

        for i, scene in enumerate(scene_list):
            print(
                'Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i+1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),))

            frame_range.append((scene[0].get_seconds(), scene[1].get_seconds()))
            
            video_stream.seek(scene[0].get_frames())
            self.save_slide(video_stream.read())

            if i == len(scene_list) - 1:
                video_stream.seek(scene[1].get_frames())
                self.save_slide(video_stream.read())
        
        stats_manager.save_to_csv(path=stats_file_path)
        return frame_range, fps

    def save_mask(self, mask_rects, img_height, img_width):
        save_path = os.path.join(self.output, "talkingHeadMask.json")
        with open(save_path, "w") as f:
            json.dump({
                "talkingHeadMaskRects": mask_rects,
                "imageSize": {
                    "height": img_height,
                    "width": img_width,
                },
            }, fp=f)

    def load_mask(self):
        th_path = os.path.join(self.output, "talkingHeadMask.json")
        mask, mask_rects = None, []

        if os.path.isfile(th_path) is False or self.use_stored_mask is False:
            acc_frame = self.detection.get_acc_frame(cv2.VideoCapture(
                self.vidpath
            ))
            mask, mask_rects = self.detection.mask_talking_head(acc_frame)
            self.save_mask(mask_rects, mask.shape[0], mask.shape[1]) 
        else:
            with open(th_path, "r") as th_file:
                th_json = json.load(fp=th_file)
                mask_rects = th_json["talkingHeadMaskRects"]
                image_size = th_json["imageSize"]["height"], th_json["imageSize"]["width"]
                mask = np.ones(image_size, np.uint8)
                for mask_rect in mask_rects:
                    for i in range(mask_rect["top"], mask_rect["bottom"] + 1):
                        for j in range(mask_rect["left"], mask_rect["right"] + 1):
                            mask[i][j] = 0
        return mask, mask_rects

    def start(self):
        self.detection.onTrigger += self.onTrigger
        self.detection.onProgress += self.onProgress

        self.start_time = time.time()

        #frame_range, fps = self.find_scenes(10.0)

        mask, mask_rects = self.load_mask()

        frame_range, fps = self.detection.start(
            cv2.VideoCapture(self.vidpath),
            mask, mask_rects
        )
        with open(os.path.join(self.output, "frameTimestamp.txt"), "w")  as f:
            for i in range(len(frame_range)) :
                f.write(str(round((frame_range[i][0]-1)/fps, 2)) + '\t' + str(round((frame_range[i][1]-1)/fps, 2)))
                f.write('\n')

        print("All done!")

main = Main(
    args['debug'],
    os.path.join(args['video'].strip()),
    os.path.join(args['output'].strip()),
    args['step-size'], args['progress-interval'],
    args["use-stored-mask"]
)

main.start()
