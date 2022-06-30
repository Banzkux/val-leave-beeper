import cv2
import numpy as np
import os
import sys
from virtualcamerafeed import VirtualCameraFeed # Threaded video feed
from winsound import Beep
from time import time
from threading import Thread, Event
from imageprocessing import Crop, DrawFPS, get_grayscale, scale_image, change_aspect_ratio
from settings import Settings
from typing import Type



def detection_loop(settings:Type[Settings]):
    dirname = os.path.dirname(sys.argv[0])
    cv2.namedWindow("Game feed")
    print("Pressing escape when \"Game feed\"", 
            "window is focused quits back to main menu.")
    begin_time = time()
    templImg = cv2.imread(os.path.join(dirname, 'data', settings.template_name), 0)
    templImg = scale_image(templImg, settings.template_scale)
    stream = VirtualCameraFeed(settings.device_index)
    stream.start()
    frame = Crop(stream.read(), settings.cropping)
    if settings.aspect_ratio[0] != 4 or settings.aspect_ratio[1] != 3:
        frame = change_aspect_ratio(frame, settings.aspect_ratio)
    if settings.video_scale != 1:
        frame = scale_image(frame, settings.video_scale)
    
    event = Event()

    # Time when last dialog was detected last time
    # this is for the cooldown thing
    detected = 0
    valLeaveCount = 0
    while True:
        # Frame rate calculations, waits if exceeding max fps
        try:
            new_time = time()
            if new_time != begin_time:
                min_deltatime = 1 / settings.max_fps
                deltatime = new_time - begin_time
                fps = 1 / deltatime
                if deltatime < min_deltatime:
                    fps = 1 / min_deltatime
                    event.wait(min_deltatime - deltatime)

                begin_time = new_time
        except:
            print("Attempted to divide by 0.")

        begin_time = time()
        new_frame = Crop(stream.read(), settings.cropping)
        # Scaling and aspect ratio
        if settings.aspect_ratio[0] != 4 or settings.aspect_ratio[1] != 3:
            new_frame = change_aspect_ratio(new_frame, settings.aspect_ratio)
        if settings.video_scale != 1:
            new_frame = scale_image(new_frame, settings.video_scale)
        # Frame same as previous -> go to next iteration of the loop
        if frame is not None and (frame == new_frame).all():
            continue
        frame = new_frame
        
        # Template matching to find the last dialogue
        img_gray = get_grayscale(frame)
        w, h = templImg.shape[::-1]
        res = cv2.matchTemplate(img_gray,templImg,cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where( res >= threshold)
        # Last dialogue detected
        # 15 second cooldown to avoid multiple detections
        if loc[0].size > 0 and detected + 15 < time():
            valLeaveCount += 1
            print("Val leave #{}".format(valLeaveCount))
            detected = time()
            t = Thread(target=ValLeaveBeep, name="SoundThread", args=(event,
                        settings))
            t.daemon = True
            t.start()
            
        # Draw rectangle around the matched position
        for pt in zip(*loc[::-1]):
            cv2.rectangle(frame, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

        frame = DrawFPS(frame, str(round(fps, 2)))
        cv2.imshow("Game feed", frame)
        
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break

    stream.stop()
    cv2.destroyWindow('Game feed')

# This is ran on separate thread
def ValLeaveBeep(event, settings:Type[Settings]):
    Beep(880, 100)
    event.wait(3.5 - settings.capture_delay + settings.adjustment)
    Beep(440, 100)