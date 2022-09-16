
import time
if __name__ == "__main__":
    # while True:
    #     print("I am not Pressed")
    #     if keyboard.is_pressed('q') or keyboard.is_pressed('enter'):
    #         print("Exit")
    #         break
    #     time.sleep(2)
    try:
        while True:
            print("I am not Pressed.")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Exit")
        pass


