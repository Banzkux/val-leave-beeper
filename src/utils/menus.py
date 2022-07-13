class Menu:
    def __init__(self, input_text, post_selection = None, looping = True):
        self.active = True
        self.entries: list[Menu_Entry] = []
        self.input_text: str = input_text
        self.post_selection = post_selection
        self.looping = looping

    def add(self, text, func = None, *args):
        self.entries.append(Menu_Entry(text, func, args))

    def quit(self):
        self.active = False

    def show(self):
        print("\n")
        # Starts printing from 1, entry 0 prints last
        entry: Menu_Entry
        for i in range(1, len(self.entries)):
            entry = self.entries[i]
            print("{}: {}".format(i, entry.get_text()))

        print("{}: {}".format(0, self.entries[0].get_text()))

    def use(self):
        selection: int = 1
        while self.active:
            self.show()
            try:
                selection = int(input(self.input_text))
            except:
                continue
            if selection not in range(len(self.entries)):
                print("Invalid input.")
                continue
            self.entries[selection].selected()
            if self.post_selection and selection != 0:
                self.post_selection()
            
            if not self.looping:
                break
        

class Menu_Entry:
    def __init__(self, text, func, text_args):
        self.text: str = text
        self.func = func
        self.text_args = text_args
    
    def get_text(self):
        text = self.text
        args = []
        for arg in self.text_args:
            try:
                args.append(arg())
            except:
                args.append("Unavailable")
        text = text.format(*args)
        return text

    def selected(self):
        return self.func()