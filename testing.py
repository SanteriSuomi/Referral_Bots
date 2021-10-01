import pyautogui
import time
import keyboard 

# while True:
#     if keyboard.is_pressed("j"):
#         print(pyautogui.position())
#     time.sleep(0.01)

# Point(x=652, y=999)
# Point(x=170, y=45)
# Point(x=340, y=737)
# Point(x=604, y=883)
# Point(x=1128, y=52)
# Point(x=966, y=141)
# Point(x=1158, y=49)
# Point(x=994, y=336)
# Point(x=1250, y=7)

pyautogui.click(x=652, y=999)
time.sleep(3)
pyautogui.click(x=170, y=45)
time.sleep(3)
pyautogui.write("https://swee.ps/SwPhA_FNSTdkT", interval=0.15)
time.sleep(3)
pyautogui.press("enter")
time.sleep(10)
pyautogui.click(x=700, y=700)
pyautogui.scroll(-10000)
time.sleep(3)
pyautogui.click(x=340, y=737)
time.sleep(3)
email = "poltwattt2@gmail.com"
for c in email:
    keyboard.write(c)
    time.sleep(0.15)
time.sleep(3)
pyautogui.click(x=604, y=883)
time.sleep(3)
pyautogui.click(x=1129, y=53)
time.sleep(3)
pyautogui.click(x=898, y=150)
time.sleep(3)
pyautogui.click(x=1158, y=49)
time.sleep(3)
pyautogui.click(x=994, y=336)
time.sleep(3)
pyautogui.click(x=1250, y=7)
