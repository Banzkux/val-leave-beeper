import device # Device names
import json
import numpy as np
import os
import sys
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
        self.cropping = Cropping(self.device_index, self.cropping).done()

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
            try:
                print("1: Select video device (current: {} {})".format(
                    self.device_index, self.device_list[self.device_index]))
            except:
                print("1: Select video device (current: {} {})".format(
                    self.device_index, "Unavailable"))
            print("2: Crop video feed")
            print("3: Calibrate template scale")
            print("4: Set delay between video feed vs CRT/Monitor", 
                    "(current:{} sec)".format(self.capture_delay))
            print("5: Set Valentin leave timing adjustment", 
        "(current:{} sec)".format(self.adjustment))
            print("6: Set max fps (current: {})".format(self.max_fps))
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
                    self.adjustment = float(input("Adjustment (- = earlier, " +
                        "+ = later) (current: {}): ".format(self.adjustment)))
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
            elif selection == 0:
                break
            else:
                print("Invalid input.")
            # Save between selections
            if selection in range(1, 7):
                self.save()

    def load(self):
        valid_keys = self.get_valid_keys()
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
        valid_keys = self.get_valid_keys()
        with open(os.path.join(self.dirname, "settings.json"), "w") as outfile:
            dict = {}
            for key, value in self.__dict__.items():
                if key in valid_keys:
                    dict.update({key:value})
            json.dump(dict, outfile, indent=4)
    
    # Creates list of keys that will be saved/loaded
    def get_valid_keys(self):
        ignore_keys = ["device_list", "dirname"]
        valid_keys = []
        for key, value in self.__dict__.items():
            if key not in ignore_keys:
                valid_keys.append(key)
        return valid_keys

    def scale_calibration(self):
        from scale_calibration import Calibration
        (self.aspect_ratio, self.template_name, self.template_scale,
                 self.video_scale) = Calibration(self).done()