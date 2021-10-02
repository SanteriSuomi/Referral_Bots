import pyautogui
import keyboard
import time

while True:
    if keyboard.is_pressed("j"):
        print(pyautogui.position())
    time.sleep(0.05)
