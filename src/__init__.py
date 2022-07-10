import cv2
from settings import Settings
from play import Play

def main():
    s = Settings()
    
    while True:
        print("1: Play")
        print("2: Settings")
        print("0: Quit")
        try:
            selection = int(input("Select action: "))
        except:
            print("Invalid input.")
            continue
        if selection == 1:
            Play(s).play()
        elif selection == 2:
            s.menu()
        elif selection == 0:
            break
        else:
            print("Invalid input.")
        print("\n\n")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()