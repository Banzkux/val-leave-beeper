from settings import Settings
from play import Play
from utils import Menu

def main():
    s = Settings()
    menu = Menu("Select action: ")
    menu.add("Quit", menu.quit)
    menu.add("Play", Play(s).play)
    menu.add("Settings", s.menu)
    menu.use()

if __name__ == "__main__":
    main()