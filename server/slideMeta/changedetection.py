import time
import numpy as np
import cv2
import imutils
import eventhook

class ChangeDetection:
    # minimum contour area (1000)
    min_area = 1000
    # maximum frames before firstFrame reset (3)
    max_idle = 3
    # frame step size
    step_size = 20
    # amount of percent between each progress event
    progress_interval = 1
    # event that fires when motion is confirmed
    onTrigger = eventhook.EventHook()
    # event that gives feedback of how far the detection is
    onProgress = eventhook.EventHook()

    TH_MARGIN = 20

    def __init__(self, step_size, progress_interval, show_debug=False):
        self.frames = []
        self.selected_frames = []
        self.step_size = step_size
        self.progress_interval = progress_interval
        self.show_debug = show_debug

    def __transform_frame(self, frame, mask):
        gray = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        gray = gray * mask
        return gray

    
    def __calc_thresh(self, frame, threshold=25):
        thresh = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)[1]
        return cv2.dilate(thresh, None, iterations=2)

    def __detect_contours(self, thresh):
        cnts = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        #print("Contours", cnts[0], cnts[1])
        cnts = cnts[0]
        valid_cnts = []
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self.min_area:
                continue
            valid_cnts.append(c)
        return valid_cnts

    def start(self, camera, mask, mask_rects):
        prev_slide_frame = None
        prev_frame = None

        # amount of contours
        cnts_cnt = 0

        # amount of idle frames that were the same
        # used to determine if that frame should become the new prev_slide_frame
        idle_cnt = 0

        # current pos in vid
        cur_frame = 0
        last_progress = 0

        fps = int(camera.get(cv2.CAP_PROP_FPS))

        print('change detection initiated')

        total_frames = camera.get(cv2.CAP_PROP_FRAME_COUNT) - 1

        while cur_frame < total_frames:
            (_, frame) = camera.read()

            if frame is None:
                break

            # if cur_frame > 450:
            #     break

            # frame = frame[:, 640:1280]
            # if chi2019:
            #     frame = frame[:, 0:640]

            original = frame.copy()

            # convert grabbed frame to gray and blur
            gray = self.__transform_frame(frame, mask)

            self.frames.append({
                "frame": original,
                "curFrameCount": camera.get(cv2.CAP_PROP_POS_FRAMES),
                "index": len(self.frames) - 1,
                "transformed_frame": gray,
            })

            if prev_slide_frame is None:
                prev_slide_frame = np.zeros(gray.shape, np.uint8)

            if prev_frame is None:
                prev_frame = np.zeros(gray.shape, np.uint8)

            frame_delta = cv2.absdiff(prev_slide_frame, gray)
            thresh = self.__calc_thresh(frame_delta)
            cnts = self.__detect_contours(thresh)

            # we have motion, possible new prev_slide_frame?
            if len(cnts) > 0:
                prev_delta = cv2.absdiff(prev_frame, gray)
                prev_thresh = self.__calc_thresh(prev_delta)
                
                # we have no changes from the previous frame
                if cv2.countNonZero(prev_thresh) == 0:
                    idle_cnt += 1
                else:
                    idle_cnt = 0

            # we have now seen the same image for too long, reset prev_slide_frame
            if idle_cnt > self.max_idle:
                prev_slide_frame = prev_frame
                self.selected_frames.append(len(self.frames) - 1)

                y_magn = original.shape[0] / gray.shape[0]
                x_magn = original.shape[1] / gray.shape[1]

                for mask_rect in mask_rects:
                    x1 = int((mask_rect["left"]) * x_magn)
                    y1 = int(mask_rect["top"] * y_magn)
                    x2 = int((mask_rect["right"] + 1) * x_magn)
                    y2 = int((mask_rect["bottom"] + 1) * y_magn)

                    cv2.rectangle(original, (x1, y1), (x2, y2),
                                  (0, 255, 0), 2)
                self.onTrigger.fire(original)
                idle_cnt = 0

            prev_frame = gray

            progress = (cur_frame / total_frames) * 100

            if progress - last_progress >= self.progress_interval:
                last_progress = progress
                self.onProgress.fire(progress, cur_frame)

            camera.set(1, min(cur_frame +
                              self.step_size, total_frames))

            cur_frame = camera.get(cv2.CAP_PROP_POS_FRAMES)

            if self.show_debug:
                # loop over the contours
                for c in cnts:
                    # compute the bounding box for the contour, draw it on the frame
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)

                cv2.putText(frame, "contours: " + str(cnts_cnt),
                            (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, "idle: " + str(idle_cnt), (140, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, "frame: " + str(cur_frame), (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # self.onTrigger.fire(frame, "Frame")
                # self.onTrigger.fire(frameDelta, "Delta")
                # self.onTrigger.fire(thresh, "Threshold")

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

        camera.release()
        cv2.destroyAllWindows()

        print(len(self.frames))
        print(len(self.selected_frames))

        frame_range = []

        for pos in self.selected_frames :
            _g1 = self.frames[pos]['transformed_frame']

            cur_range = [self.frames[pos]["curFrameCount"], self.frames[pos]["curFrameCount"]]

            for k in [-1, 1] :
                cur = pos + k
                if not (0 <= cur and cur < len(self.frames)):
                    continue
                while 0 <= cur and cur < len(self.frames):
                    _g2 = self.frames[cur]["transformed_frame"]

                    delta = cv2.absdiff(_g1, _g2)
                    thresh = self.__calc_thresh(delta)
                    cnts = self.__detect_contours(thresh)

                    if len(cnts) > 0 :
                        break

                    cur_range[ 0 if k == -1 else 1 ] = self.frames[cur]["curFrameCount"]
                    cur = cur + k
            frame_range.append(cur_range)

        return frame_range, fps

    def get_acc_frame(self, camera):
        acc_frame = None
        acc_frames_cnt = 0

        prev_frame = None

        # current pos in vid
        cur_frame = 0
        last_progress = 0

        print('talking head detection initiated')

        total_frames = camera.get(cv2.CAP_PROP_FRAME_COUNT) - 1

        while cur_frame < total_frames:
            (_, frame) = camera.read()

            if frame is None:
                break

            # if cur_frame > 450:
            #     break

            # convert grabbed frame to gray and blur
            gray = self.__transform_frame(frame, 1)

            if prev_frame is None:
                acc_frame = np.zeros(gray.shape, np.float64)
                prev_frame = np.zeros(gray.shape, np.uint8)

            prev_delta = cv2.absdiff(prev_frame, gray)
            thresh = cv2.threshold(prev_delta, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            thresh_np = np.asarray(thresh).astype(np.float64)
            acc_frame = acc_frame + thresh_np
            acc_frames_cnt += 1

            prev_frame = gray

            progress = (cur_frame / total_frames) * 100
            if progress - last_progress >= self.progress_interval:
                last_progress = progress
                self.onProgress.fire(progress, cur_frame)

            camera.set(1, min(cur_frame +
                              self.step_size, total_frames))

            cur_frame = camera.get(cv2.CAP_PROP_POS_FRAMES)

        camera.release()
        if acc_frames_cnt == 0:
            print("No frames", cur_frame, total_frames)
            return None
        acc_frame /= acc_frames_cnt
        acc_frame_img = acc_frame.astype(np.uint8)
        self.onTrigger.fire(acc_frame_img, "acc_frame_")
        return acc_frame_img

    def mask_talking_head(self, acc_frame):
        (n, m) = acc_frame.shape

        mask = np.ones((n, m), np.uint8)

        mask_rects = []

        thresh = self.__calc_thresh(acc_frame, 50)
        blur_thresh = cv2.GaussianBlur(thresh, (5, 5), 0)
        edges = cv2.Canny(blur_thresh, 0, 100)

        self.onTrigger.fire(blur_thresh, "blur_thresh_acc_frame_")
        self.onTrigger.fire(edges, "edges_acc_frame_")

        while True:
            dp = [[0 for j in range(m)] for i in range(n)]
            for i in range(n):
                for j in range(m):
                    if i > 0:
                        dp[i][j] += dp[i-1][j]
                    if j > 0:
                        dp[i][j] += dp[i][j-1]
                    if i > 0 and j > 0:
                        dp[i][j] -= dp[i-1][j-1]
                    dp[i][j] += int(edges[i][j])
            px_max_sum = 0
            boundary_i = 0
            boundary_j = 0
            side_i = 0
            side_j = 0

            for i in range(n - 1):
                for j in range(m - 1):
                    for bi in range(2):
                        for bj in range(2):
                            top = bi * (i + 1)
                            bottom = (1 - bi) * (i + 1) + (bi * n) - 1
                            left = bj * (j + 1)
                            right = (1 - bj) * (j + 1) + (bj * m) - 1

                            px_sum = dp[bottom][right]
                            if top > 0:
                                px_sum -= dp[top - 1][right]
                            if left > 0:
                                px_sum -= dp[bottom][left - 1]
                            if top > 0 and left > 0:
                                px_sum += dp[top - 1][left - 1]

                            px_sum /= (bottom - top + 1) * (right - left + 1)

                            if ((bottom - top + 1) * (right - left + 1) < self.min_area):
                                continue

                            if px_sum > px_max_sum:
                                px_max_sum = px_sum
                                boundary_i = i
                                boundary_j = j
                                side_i = bi
                                side_j = bj

            if px_max_sum < 1:
                break

            top = max(side_i * (boundary_i + 1) - self.TH_MARGIN, 0)
            bottom = min((1 - side_i) * (boundary_i + 1) + (side_i * n) + self.TH_MARGIN, n)
            left = max(side_j * (boundary_j + 1) - self.TH_MARGIN, 0)
            right = min((1 - side_j) * (boundary_j + 1) + (side_j * m) + self.TH_MARGIN, m) 

            mask_rects.append({
                "top": top,
                "bottom": bottom - 1,
                "left": left,
                "right": right - 1,
            })

            for i in range(top, bottom):
                for j in range(left, right):
                    blur_thresh[i][j] = 255
                    edges[i][j] = 0
                    mask[i][j] = 0
        return mask, mask_rects