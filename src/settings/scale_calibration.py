import cv2
import glob
import numpy as np
import os
import sys
from utils.imageprocessing import Crop, get_grayscale, scale_image, change_aspect_ratio
from utils import VirtualCameraFeed # Threaded video feed
from settings import Settings
from typing import Type

class Calibration:
    def __init__(self, s:Type[Settings]):
        self.s = s
        self.settings = (s.aspect_ratio, s.template_name, s.template_scale,
                             s.video_scale)
        frame = self.frame()

        if len(frame) == 0:
            print("No frame selected. Quitting calibration...")
            return

        result = self.compare(frame)
        (maxVal, t_scale, v_scale, t_name, aspect) = result

        if maxVal < 0.8:
            print("Make sure that the comparison frame",
                        "has the template image visible.")
            print("Result was too poor. Anything below 0.8 won't work at all.",
                    "For best performance result of 0.9+ is needed.")
        
        self.preview(frame, aspect)

        # Result good enough, keep the settings
        if maxVal > 0.8:
            self.settings = (aspect, t_name, t_scale, v_scale)

    def frame(self):
        stream = VirtualCameraFeed(self.s.device_index)
        stream.start()
        frame = Crop(stream.read(), self.s.cropping)
        print("Press space once your template image is on screen", 
            "(scale calibration window needs to be focused).")
        
        window_name = "Scale calibration window"
        cv2.namedWindow(window_name)
        selected_frame = []
        while cv2.getWindowProperty(window_name , cv2.WND_PROP_VISIBLE) > 0:
            frame = Crop(stream.read(), self.s.cropping)
            frame = cv2.resize(
                            frame, (640, 480), interpolation = cv2.INTER_AREA)
            cv2.imshow(window_name, frame)
            k = cv2.waitKey(1)
            if k == 32:
                selected_frame = get_grayscale(frame)
                cv2.destroyWindow(window_name)
                print("Space pressed, starting calibration...")
                break
        
        stream.stop()
        return selected_frame

    def compare(self, frame):
        dirname = os.path.dirname(sys.argv[0])

        # Adds all templateimages from data folder
        templates = []
        for file in glob.glob(os.path.join(
                                        dirname, 'data/templateimage*.png')):
            templates.append((os.path.basename(file), cv2.imread(file, 0)))

        # Test aspect ratios
        common_aspect = [(4, 3), (16, 9), (5, 4), (16, 10), (3, 2)]
        found = None
        print("{} of {} done.".format(0, len(common_aspect)))
        i = 0
        for aspect in common_aspect:
            resized = change_aspect_ratio(frame, aspect)
            # Scaling template in comparison
            (maxVal, scale, vscale, t_name) = self.scaling_comparison(
                                                    resized, templates, True)
            if found is None or maxVal > found[0]:
                found = (maxVal, scale, vscale, t_name, aspect)
            # Scaling image in comparison
            (maxVal, scale, vscale, t_name) = self.scaling_comparison(
                                                    resized, templates, False)
            if found is None or maxVal > found[0]:
                found = (maxVal, scale, vscale, t_name, aspect)
            i += 1
            print("{} of {} done.".format(i, len(common_aspect)))

        print("Best result:", found)
        return found
        
    def preview(self, frame, aspect):
        resizedFrame = change_aspect_ratio(frame, aspect)
        window_name = "Comparison frame"
        cv2.namedWindow(window_name)
        while cv2.getWindowProperty(window_name , cv2.WND_PROP_VISIBLE) > 0:
            cv2.imshow(window_name, resizedFrame)
            k = cv2.waitKey(0)
            if k != -1:
                cv2.destroyWindow(window_name)
                break
        
    # Scales image or template down, matches with template and loops
    # best result is kept
    def scaling_comparison(self, image, templates, resizeTemplate):
        found = None
        for template in templates:
            (templateName, templateImage) = template
            for scale in np.linspace(0.2, 1.0, 100)[::-1]:
                if resizeTemplate:
                    resizeble = template[1]
                else:
                    resizeble = image
                resized = scale_image(resizeble, scale)
                if resizeTemplate:
                    result = cv2.matchTemplate(
                        image, resized,cv2.TM_CCOEFF_NORMED)
                else:
                    # Makes sure the template image isn't bigger than the video
                    if resized.shape[0] < templateImage.shape[0] or \
                        resized.shape[1] < templateImage.shape[1]:
                        break
                    result = cv2.matchTemplate(
                        resized, templateImage,cv2.TM_CCOEFF_NORMED)
                
                (_, maxVal, _, _) = cv2.minMaxLoc(result)
                if found is None or maxVal > found[0]:
                    if resizeTemplate:
                        found = (maxVal, scale, float(1), templateName)
                    else:
                        found = (maxVal, float(1), scale, templateName)
        return found

    def done(self):
        return self.settings