import time
import numpy as np
import cv2
import imutils
import eventhook

class ChangeDetection:
    # minimum contour area (1000)
    frames = []
    minArea = 1000
    # maximum frames before firstFrame reset (3)
    maxIdle = 3
    # frame step size
    stepSize = 20
    # amount of percent between each progress event
    progressInterval = 1
    # event that fires when motion is confirmed
    onTrigger = eventhook.EventHook()
    # event that gives feedback of how far the detection is
    onProgress = eventhook.EventHook()

    TH_MARGIN = 20

    def __init__(self, stepSize, progressInterval, showDebug=False):
        self.frames = []
        self.selectedFrames = []
        self.stepSize = stepSize
        self.progressInterval = progressInterval
        self.showDebug = showDebug

    def __transform_frame(self, frame, mask):
        gray = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        gray = gray * mask
        return gray

    
    def calcThresh(self, frame, threshold=25):
        thresh = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)[1]
        return cv2.dilate(thresh, None, iterations=2)

    def detectContours(self, thresh):
        cnts = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        print("Contours", cnts[0], cnts[1])
        cnts = cnts[0]
        validCnts = []
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self.minArea:
                continue
            validCnts.append(c)
        return validCnts

    def start(self, camera, mask):
        firstFrame = None
        prevFrame = None

        # amount of contours
        contAmount = 0

        # amount of idle frames that were the same
        # used to determine if that frame should become the new firstFrame
        idleCount = 0

        # current pos in vid
        currentPosition = 0
        lastProgress = 0

        fps = int(camera.get(cv2.CAP_PROP_FPS))

        print('change detection initiated')

        totalFrames = camera.get(cv2.CAP_PROP_FRAME_COUNT) - 1

        while currentPosition < totalFrames:
            (_, frame) = camera.read()

            if frame is None:
                break

            # if currentPosition > 500:
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

            if firstFrame is None:
                firstFrame = np.zeros(gray.shape, np.uint8)

            if prevFrame is None:
                prevFrame = np.zeros(gray.shape, np.uint8)

            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = self.calcThresh(frameDelta)
            cnts = self.detectContours(thresh)

            # we have motion, possible new firstFrame?
            if len(cnts) > 0:
                prevDelta = cv2.absdiff(prevFrame, gray)
                prevThresh = self.calcThresh(prevDelta)
                
                # we have no changes from the previous frame
                if cv2.countNonZero(prevThresh) == 0:
                    idleCount += 1
                else:
                    idleCount = 0

            # we have now seen the same image for too long, reset firstImage
            if idleCount > self.maxIdle:
                firstFrame = prevFrame
                self.selectedFrames.append(len(self.frames) - 1)
                self.onTrigger.fire(original)
                self.onTrigger.fire(gray, "masked_")
                idleCount = 0

            prevFrame = gray

            progress = (currentPosition / totalFrames) * 100

            if progress - lastProgress >= self.progressInterval:
                lastProgress = progress
                self.onProgress.fire(progress, currentPosition)

            camera.set(1, min(currentPosition +
                              self.stepSize, totalFrames))

            currentPosition = camera.get(cv2.CAP_PROP_POS_FRAMES)

            if self.showDebug:
                # loop over the contours
                for c in cnts:
                    # compute the bounding box for the contour, draw it on the frame
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)

                cv2.putText(frame, "contours: " + str(contAmount),
                            (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, "idle: " + str(idleCount), (140, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, "frame: " + str(currentPosition), (10, 40),
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
        print(len(self.selectedFrames))

        frameRange = []

        for pos in self.selectedFrames :

            tmp = [ 987987987 for i in range(len(self.frames)) ]

            _g1 = self.selectedFrames[pos]['transformed_frame']

            myRange = [pos, pos]

            for k in [-1, 1] :
                cur = pos + k

                if not (0 <= cur and cur < len(self.frames)) :
                    continue

                tmp[pos] = 0

                while 0 <= cur and cur < len(self.frames) :
                    _g2 = self.__transform_frame(self.frames[cur]["transformed_frame"])

                    delta = cv2.absdiff(_g1, _g2)
                    thresh = self.calcThresh(delta)
                    cnts = self.detectContours(thresh)

                    if len(cnts) > 0 :
                        break

                    tmp[cur] = 0
                    myRange[ 0 if k == -1 else 1 ] = self.frames[cur]["curFrameCount"]

                    cur = cur + k

            frameRange.append(myRange)

        return frameRange, fps

    def getAccFrame(self, camera):
        accFrame = None
        accedFrames = 0

        prevFrame = None

        # current pos in vid
        currentPosition = 0
        lastProgress = 0

        print('talking head detection initiated')

        totalFrames = camera.get(cv2.CAP_PROP_FRAME_COUNT) - 1

        while currentPosition < totalFrames:
            (_, frame) = camera.read()

            if frame is None:
                break

            # convert grabbed frame to gray and blur
            gray = self.__transform_frame(frame, 1)

            if prevFrame is None:
                accFrame = np.zeros(gray.shape, np.float64)
                prevFrame = np.zeros(gray.shape, np.uint8)

            frameDelta = cv2.absdiff(prevFrame, gray)
            thresh = cv2.threshold(frameDelta, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            thresh_np = np.asarray(thresh).astype(np.float64)
            accFrame = accFrame + thresh_np
            accedFrames += 1

            prevFrame = gray

            progress = (currentPosition / totalFrames) * 100

            if progress - lastProgress >= self.progressInterval:
                lastProgress = progress
                self.onProgress.fire(progress, currentPosition)

            camera.set(1, min(currentPosition +
                              self.stepSize, totalFrames))

            currentPosition = camera.get(cv2.CAP_PROP_POS_FRAMES)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        camera.release()

        accFrame /= accedFrames
        accFrame_img = accFrame.astype(np.uint8)
        self.onTrigger.fire(accFrame_img, "accFrame_")
        return accFrame_img

    def mask_talking_head(self, accFrame):
        (n, m) = accFrame.shape

        mask = np.ones((n, m), np.uint8)

        accFrame_img = self.calcThresh(accFrame, 50)
        accFrame_blur = cv2.GaussianBlur(accFrame_img, (5, 5), 0)
        edges = cv2.Canny(accFrame_blur, 0, 100)

        self.onTrigger.fire(accFrame_img, "blurred_accFrame")
        self.onTrigger.fire(edges, "edges_")

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

                            if ((bottom - top + 1) * (right - left + 1) < self.minArea):
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

            for i in range(top, bottom):
                for j in range(left, right):
                    accFrame_blur[i][j] = 255
                    edges[i][j] = 0
                    mask[i][j] = 0
        return mask