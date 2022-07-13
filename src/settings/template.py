from utils import Menu
from functools import partial

class Template_Menu:
    def __init__(self, settings):
        from .settings import Settings
        self.s: Settings = settings

    def menu(self):
        i = self.s.current_template
        menu = Menu("Select action: ", self.s.save)
        menu.add("Back to settings", menu.quit)
        menu.add(
            "Select template (current: {}, timer: {} sec, cooldown: {} sec)",
            self.select, lambda: self.s.templates[i].name,
            lambda: self.s.templates[i].timer,
            lambda: self.s.templates[i].cooldown)
        menu.add("Calibrate current template", self.scale_calibration)
        menu.add("Modify current template", self.s.templates[i].template_menu)
        menu.add("Create new template", self.create)
        menu.add("Delete a template", self.delete)
        menu.use()

    def select(self):
        menu = Menu("Select template: ", looping=False)
        menu.add("Back to template menu", menu.quit)
        template: Template
        for i, template in enumerate(self.s.templates):
            menu.add(template.name, partial(self.set_current_template, i))
        menu.use()

    def create(self):
        self.s.templates.append(Template())
    
    def delete(self):
        menu = Menu("Delete template: ", looping=False)
        menu.add("Back to template menu", menu.quit)
        template: Template
        for i, template in enumerate(self.s.templates):
            menu.add(template.name, partial(self.template_delete, i))
        menu.use()

    def template_delete(self, index):
        t = self.s.templates[index]
        answer = input("Delete \"{}\" timer: {} sec (y/n)?: "
            .format(t.name, t.timer))
        if answer.lower() != "y":
            print("Deletion cancelled.")
            return
        self.s.templates.pop(index)
        if index < self.s.current_template:
            self.s.current_template -= 1
        elif index == self.s.current_template:
            self.s.current_template = 0

    def set_current_template(self, index):
        self.s.current_template = index

    def scale_calibration(self):
        from .scale_calibration import Calibration
        i = self.s.current_template
        self.s.templates[i].set_calibration(*Calibration(self.s).done())

class Template:
    def __init__(self, name = None, aspect_ratio = [4, 3], file_name = "",
        scale = float(1), video_scale = float(1), timer = float(1),
        cooldown = float(15)):
        self.name = name # Folder in data folder will be named after this

        # Calibration results, template images from self.name folder
        self.aspect_ratio = aspect_ratio
        self.file_name = file_name
        self.scale = scale
        self.video_scale = video_scale

        self.timer = timer # seconds
        self.cooldown = cooldown

        if name is None:
            self.input()

    def set_calibration(self, aspect_ratio, file_name, scale, video_scale):
        self.aspect_ratio = aspect_ratio
        self.file_name = file_name
        self.scale = scale
        self.video_scale = video_scale

    def input(self):
        self.input_name()
        self.input_timer()
        self.input_cooldown()
        return self
        
    def template_menu(self):
        menu = Menu("Select option to modify: ")
        menu.add("Save template", menu.quit)
        menu.add("Template name ({})", self.input_name,
            lambda: self.name)
        menu.add("Timer ({} sec)", self.input_timer,
            lambda: self.timer)
        menu.add("Cooldown ({} sec)", self.input_cooldown,
        lambda: self.cooldown)
        menu.use()

    def input_name(self):
        self.name = input("Template name: ")

    def input_timer(self):
        while True:
            try:
                timer = float(input("Timer length (seconds): "))
                if timer < 0:
                    raise
                self.timer = timer
                break
            except:
                print("Invalid input.")
    def input_cooldown(self):
        while True:
            try:
                cooldown = float(input("Cooldown length (seconds): "))
                if cooldown < 0:
                    raise
                self.cooldown = cooldown
                break
            except:
                print("Invalid input.")