import cv2
import device # Device names
import glob
import json
import numpy as np
import os
import sys
from imageprocessing import Crop, get_grayscale, scale_image, change_aspect_ratio
from virtualcamerafeed import VirtualCameraFeed # Threaded video feed
from cropping import Cropping

class Settings:
    def __init__(self):
        self.adjustment = float(0) # seconds
        self.capture_delay = float(0.333) # seconds
        self.cropping = [0, 0, 0, 0] #[x1,y1, x2, y2] = top left, bottom right
        self.device_index = int(2)
        self.max_fps = float(29.97)
        # Scale calibration variables
        self.aspect_ratio = [4, 3]
        self.template_name = "templateimagefrom4by3.png"
        self.template_scale = float(1)
        self.video_scale = float(1)

        self.resolution = [640, 480]

        self.dirname = os.path.dirname(sys.argv[0])
        try:
            self.device_list = device.getDeviceList()
        except:
            self.device_list = [
                "Failed to get device list", "Guessing works too",
            "0 is usually the built-in webcam", "Try between 0-5"
            ] * 2
        self.load()

    def crop_video(self):
        self.cropping = Cropping(self.device_index, self.resolution).done()

    # Device selection
    def device_menu(self):
        while True:
            print("\n\n")
            index = 0
            for name in self.device_list:
                print("{}: {}".format(index, name))
                index += 1
            try:
                selection = int(input("Select device: "))
            except:
                continue
            if selection in range(0, index):
                self.device_index = int(selection)
                break
            else:
                continue
        
    def menu(self):
        while True:
            print("\n\n")
            print("1: Select video device (current: {} {})".format(
                self.device_index, self.device_list[self.device_index]))
            print("2: Crop video feed (Cancelling the process = no cropping)")
            print("3: Calibrate template scale")
            print("4: Set delay between video feed vs CRT/Monitor", 
                    "(current:{} sec)".format(self.capture_delay))
            print("5: Set Valentin leave timing adjustment", 
        "(- = earlier, + = later) (current:{} sec)".format(self.adjustment))
            print("6: Set max fps (current: {})".format(self.max_fps))
            print("7: Set OBS output resolution (current: {}x{})"
                            .format(self.resolution[0], self.resolution[1]))
            print("0: Main menu")
            try:
                    selection = int(input("Select action: "))
            except:
                print("Invalid input.")
                continue
            if selection == 1:
                self.device_menu()
            elif selection == 2:
                self.crop_video()
            elif selection == 3:
                self.scale_calibration()
            elif selection == 4:
                try:
                    self.capture_delay = float(
            input("Capture delay (current: {}): ".format(self.capture_delay)))
                except:
                    print("Invalid input. Previous value kept.")
            elif selection == 5:
                try:
                    self.adjustment = float(input("Adjustment (current: {}): "
                    .format(self.adjustment)))
                    self.adjustment = np.clip(self.adjustment, -2, 2)
                except:
                    print("Invalid input. Previous value kept.")
            elif selection == 6:
                try:
                    self.max_fps = float(input("Max fps (current: {}): "
                    .format(self.max_fps)))
                    if self.max_fps <= 0:
                        self.max_fps = float(1)
                except:
                    print("Invalid input. Previous value kept.")
            elif selection == 7:
                try:
                    temp = input("Resolution (current: {}x{}):"
                    .format(self.resolution[0], self.resolution[1])).split("x")
                    if len(temp) != 2:
                        raise
                    self.resolution = [int(i) for i in temp]
                except:
                    print("Invalid input. Previous value kept.")
            elif selection == 0:
                self.save()
                break
            else:
                print("Invalid input.")

    def load(self):
        valid_keys = ["adjustment", "capture_delay",
                         "cropping", "device_index", "max_fps", "aspect_ratio",
                         "template_name", "template_scale", "video_scale",
                         "resolution"]
        try:
            with open(os.path.join(self.dirname, "settings.json"), "r") as json_file:
                data = json.load(json_file)
            for key, value in data.items():
                if key in valid_keys:
                    self.__dict__.update({key:value})
        except FileNotFoundError:
            print("Couldn't find settings.json file.",
                    "Creating default settings.json file.")
            self.save()

    def save(self):
        ignore_keys = ["device_list", "dirname"]
        with open(os.path.join(self.dirname, "settings.json"), "w") as outfile:
            dict = {}
            for key, value in self.__dict__.items():
                if key not in ignore_keys:
                    dict.update({key:value})
            json.dump(dict, outfile, indent=4)

    def scale_calibration(self):
        stream = VirtualCameraFeed(self.device_index, self.resolution)
        stream.start()
        frame = Crop(stream.read(), self.cropping)
        print("Press space once Valentin says the last line", 
            "(scale calibration window needs to be focused).")
        while True:
            frame = Crop(stream.read(), self.cropping)
            frame = cv2.resize(
                            frame, (640, 480), interpolation = cv2.INTER_AREA)
            cv2.imshow("Scale calibration window", frame)
            k = cv2.waitKey(1)
            if k == 32:
                cv2.destroyWindow("Scale calibration window")
                print("Space pressed, starting calibration...")
                break
        frame = get_grayscale(frame)

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
            print("Matching:", maxVal, "Resized to {}:{} {}"
                                        .format(aspect[0], aspect[1], t_name))
            # Scaling image in comparison
            (maxVal, scale, vscale, t_name) = self.scaling_comparison(
                                                    resized, templates, False)
            if found is None or maxVal > found[0]:
                found = (maxVal, scale, vscale, t_name, aspect)
            print("Matching:", maxVal, "Resized to {}:{} (image scaled) {}"
                                    .format(aspect[0], aspect[1], t_name))
            i += 1
            print("{} of {} done.".format(i, len(common_aspect)))

        print("Best result:", found)
        (maxVal, template_scale, video_scale, t_name, aspect) = found
        resizedFrame = change_aspect_ratio(frame, aspect)
        print("Press space to continue (Comparison frame window focused)")
        while True:
            cv2.imshow("Comparison frame", resizedFrame)
            k = cv2.waitKey(0)
            if k == 32:
                print("Space pressed, closing...")
                break
        cv2.destroyAllWindows()
        self.aspect_ratio = aspect
        self.template_name = t_name
        self.template_scale = template_scale
        self.video_scale = video_scale
        stream.stop()
    
    # Scales image or template down, matches with template and loops
    # best result is kept
    def scaling_comparison(self, image, templates, resizeTemplate):
        found = None
        for template in templates:
            (templateName, templateImage) = template
            for scale in np.linspace(0.2, 1.0, 100)[::-1]:
                #print("This is scale", scale, templateName)
                if resizeTemplate:
                    resizeble = template[1]
                else:
                    resizeble = image
                resized = scale_image(resizeble, scale)
                if resizeTemplate:
                    result = cv2.matchTemplate(
                        image, resized,cv2.TM_CCOEFF_NORMED)
                else:
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