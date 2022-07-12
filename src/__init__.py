from settings import Settings
from play import Play
from utils import Menu

def main():
    s = Settings()
    menu = Menu("Select action: ")
    menu.add("Quit", lambda: menu.quit())
    menu.add("Play", lambda: Play(s).play())
    menu.add("Settings", lambda: s.menu())
    menu.use()

if __name__ == "__main__":
    main()