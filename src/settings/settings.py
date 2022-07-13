import device # Device names
import json
import os
import sys
from settings.cropping import Cropping
from utils import Menu
from .template import Template, Template_Menu
class Settings:
    def __init__(self):
        self.capture_delay = float(0.333) # seconds
        self.cropping = [0, 0, 0, 0] #[x1,y1, x2, y2] = top left, bottom right
        self.device_index = int(2)
        self.max_fps = float(29.97)

        self.templates: list[Template] = []
        self.current_template: int = 0

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
        menu = Menu("Select action: ", post_selection=self.save)
        menu.add("Main menu", menu.quit)
        menu.add("Select video device (current: {} {})", self.device_menu,
        lambda: self.device_index, lambda: self.device_list[self.device_index])

        menu.add("Crop video feed", self.crop_video)
        menu.add("Set delay between video feed vs CRT/Monitor (current: {} " +
        "sec)", self.capture_delay_input, lambda: self.capture_delay)
        menu.add("Set max fps (current {})", self.max_fps_input,
                    lambda: self.max_fps)
        menu.add("Templates menu", Template_Menu(self).menu)
        menu.use()

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
        # Deserializes templates
        for i in range(len(self.templates)):
            self.templates[i] = Template(**self.templates[i])

    def save(self):
        valid_keys = self.get_valid_keys()
        # Serializes templates
        temp = self.templates.copy()
        for i, template in enumerate(self.templates):
            self.templates[i] = template.__dict__
        
        with open(os.path.join(self.dirname, "settings.json"), "w") as outfile:
            dict = {}
            for key, value in self.__dict__.items():
                if key not in valid_keys:
                    continue
                dict.update({key:value})
            json.dump(dict, outfile, indent=4)
        
        self.templates = temp
    
    # Creates list of keys that will be saved/loaded
    def get_valid_keys(self):
        ignore_keys = ["device_list", "dirname"]
        valid_keys = []
        for key, value in self.__dict__.items():
            if key not in ignore_keys:
                valid_keys.append(key)
        return valid_keys

    def capture_delay_input(self):
        try:
            self.capture_delay = float(
    input("Capture delay (current: {}): ".format(self.capture_delay)))
        except:
            print("Invalid input. Previous value kept.")
    
    def max_fps_input(self):
        try:
            self.max_fps = float(input("Max fps (current: {}): "
            .format(self.max_fps)))
            if self.max_fps <= 0:
                self.max_fps = float(1)
        except:
            print("Invalid input. Previous value kept.")