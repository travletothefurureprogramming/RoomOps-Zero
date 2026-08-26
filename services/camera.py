import cv2
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)

class MotionDetector:
    def __init__(self):
        self.last_motion_time = 0
        self.motion_detected = False

    def _check_motion_sync(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print(" Camera index 0 could not be opened!")
            return False

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        ret1, frame1 = cap.read()
        time.sleep(0.1) 
        ret2, frame2 = cap.read()
        cap.release()

        if not ret1 or not ret2 or frame1 is None or frame2 is None:
            return False

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

        delta = cv2.absdiff(gray1, gray2)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_count = cv2.countNonZero(thresh)

        print(f"DEBUG: Motion pixel count = {motion_count}") 

        if motion_count > 800:
            cv2.imwrite("static/last_motion.jpg", frame2)
            self.last_motion_time = time.time()
            self.motion_detected = True
            return True

        self.motion_detected = False
        return False

    async def detect_motion(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self._check_motion_sync)

motion_detector = MotionDetector()