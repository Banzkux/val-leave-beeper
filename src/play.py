import cv2
import os
from imageprocessing import Crop, DrawFPS, scale_image, change_aspect_ratio,\
match_template
from virtualcamerafeed import VirtualCameraFeed # Threaded video feed
from winsound import Beep
from time import time
from threading import Thread, Event
from settings import Settings
from typing import Type

class Play:
    def __init__(self, settings:Type[Settings]):
        self.settings = settings
        self.template = cv2.imread(os.path.join(
            self.settings.dirname, 'data', settings.template_name), 0)
        self.window_name = "Game feed"
        self.stream = VirtualCameraFeed(settings.device_index)
        self.frame = None
        self.event = Event()
        

    def play(self):
        self.template = scale_image(self.template, self.settings.template_scale)
        self.stream.start()
        cv2.namedWindow(self.window_name)
        previous_time = time()
        # Time when last dialog was detected last time
        # this is for the cooldown thing
        last_detection = 0
        detection_count = 0
        fps = 0
        while cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) > 0:
            # Frame rate calculations, waits if exceeding max fps
            try:
                new_time = time()
                if new_time != previous_time:
                    min_deltatime = 1 / self.settings.max_fps
                    deltatime = new_time - previous_time
                    fps = 1 / deltatime
                    if deltatime < min_deltatime:
                        fps = 1 / min_deltatime
                        self.event.wait(min_deltatime - deltatime)
            except:
                print("Attempted to divide by 0.")

            previous_time = time()
            
            new_frame = self.get_frame()
            # Frame same as previous -> go to next iteration of the loop
            if self.frame is None:
                self.frame = new_frame
            elif (self.frame == new_frame).all():
                continue
            else:
                self.frame = new_frame

            w, h = self.template.shape[::-1]
            loc = match_template(self.frame, self.template)
            # Detected, 15 sec cooldown
            if loc[0].size > 0 and last_detection + 15 < time():
                detection_count += 1
                print("Detection #{}".format(detection_count))
                last_detection = time()
                t = Thread(target=self.beep, name="SoundThread")
                t.daemon = True
                t.start()

            # Keep the original for checking if frame changed :)
            edited_frame = self.frame
            # Draw rectangle around the matched position
            for pt in zip(*loc[::-1]):
                cv2.rectangle(edited_frame, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
            
            edited_frame = DrawFPS(edited_frame, str(round(fps, 2)))
            cv2.imshow(self.window_name, edited_frame)

            k = cv2.waitKey(1)
            if k%256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                cv2.destroyWindow(self.window_name)
                break
            
        self.stream.stop()

    def get_frame(self):
        frame = Crop(self.stream.read(), self.settings.cropping)
        frame = cv2.resize(frame, (640, 480), interpolation = cv2.INTER_AREA)
        # Scaling and aspect ratio
        if self.settings.aspect_ratio[0] != 4 or self.settings.aspect_ratio[1] != 3:
            frame = change_aspect_ratio(frame, self.settings.aspect_ratio)
        if self.settings.video_scale != 1:
            frame = scale_image(frame, self.settings.video_scale)
        return frame

    # This is ran on separate thread
    def beep(self):
        Beep(880, 100)
        self.event.wait(3.5 - self.settings.capture_delay + self.settings.adjustment)
        Beep(440, 100)