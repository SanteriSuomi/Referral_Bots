from subprocess import run
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.common.exceptions import NoSuchWindowException

from faker import Faker

import shutil
import random
import time
from piapy import PiaVpn
import requests
import re

import os
import pathlib
import traceback

from datetime import datetime as dt

import pyautogui
import keyboard
import pygetwindow

random.seed(time.time())
Faker.seed(time.time())
vpn = PiaVpn()
json_data = "application/json"
hex_chars = ["a", "b", "c", "d", "e", "f"]
path = (
    pathlib.Path().home() / "Desktop" / "bot_log.txt"
)  # Where log file will be stored


vpn_regions = [r for r in vpn.regions() if r.find("streaming") == -1]
email_domains = [
    "gmail.com",
    "outlook.com",
    "yahoo.com",
    "hotmail.com",
    "GMX.com",
]

fake_per = Faker(["en", "en_GB", "en_IE", "en_NZ", "en_TH", "en_US"])
fake_email = Faker(["en", "en_GB", "en_IE", "en_NZ", "en_TH", "en_US"])


class Details:
    def __init__(
        self,
        sw_url,  # SW url
        amount_to_complete,  # How many to complete until stopping
        has_referral=False,  # If there is a referral field preset
        referral_name="",  # If has_referral is true, what referral to enter (your SW username)
        has_email_verification=False,  # If there is email verification present (asking for a 4 digit code)
        has_captcha=False,  # If there is a captcha question present at the start
        has_bsc_address_field=False,  # If there is a field asking for BSC wallet address
        bsc_address_field_id="",  # If has_bsc_address is true, give here the ID of the HTML element that
        # corresponds to the field (right click in browser -> inspect -> hover over the field,
        # and you should find the id="XXXX" in the dev tools window), the reason this needs to be is because this field ID
        # can change from SW to SW
        extra_time=(
            0,
            0,
        ),  # Range of extra time in seconds added after each loop to make the bot appear more legit.
        # e.g (30, 60) for 30-60 second extra time. 0 for both if none
    ) -> None:
        self.sw_url = sw_url
        self.amount_to_complete = amount_to_complete
        self.has_referral = has_referral
        self.referral_name = referral_name
        self.has_email_verification = has_email_verification
        self.has_captcha = has_captcha
        self.has_bsc_address_field = has_bsc_address_field
        self.bsc_address_field_id = bsc_address_field_id
        self.extra_time = extra_time


todo = [
    Details(
        sw_url="https://sweepwidget.com/view/34435-xhbjcrqf/88y9ie-34435",
        amount_to_complete=50,
        has_referral=False,
        referral_name="StygeXD",
        has_email_verification=False,
        has_captcha=False,
        has_bsc_address_field=False,
        bsc_address_field_id="sw_text_input_5_1",
        extra_time=(0, 0),
    )
]


class Bot:
    def get_random_user(self):
        username = fake_per.name()
        rand = random.random()
        if rand < 0.2:
            username = username.lower()
        elif rand < 0.4:
            username = username.upper()

        if random.random() < 0.6:
            username_email = fake_email.name()
        else:
            username_email = fake_email.last_name() + fake_email.first_name()

        if random.random() < 0.6:
            username_email = username_email.replace(".", "").replace(" ", "").lower()
        else:
            username_email = username_email.replace(".", "").replace(" ", "")

        if random.random() < 0.5:
            email = f"{username_email}{int(random.uniform(0, 100))}@{random.choice(email_domains)}"
        else:
            email = f"{username_email}@{random.choice(email_domains)}"

        return username, email

    def connect_vpn(self):
        try:
            vpn.set_region(server=random.choice(vpn_regions))
            vpn.connect(verbose=False, timeout=30)
            while vpn.status() != "Connected":
                time.sleep(0.01)
            return True
        except Exception as _:
            # write_to_log()
            return False

    def get_browser_driver(self, details):
        shutil.rmtree(r"C:\Users\glorious\AppData\Local\Temp", ignore_errors=True)
        profile = webdriver.FirefoxProfile(
            r"C:\Users\glorious\AppData\Roaming\Mozilla\Firefox\Profiles\qcdanr2x.default-release"
        )
        profile.set_preference("dom.popup_maximum", 0)
        profile.set_preference("privacy.popups.showBrowserMessage", False)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("dom.disable_beforeunload", True)
        profile.set_preference("privacy.popups.disable_from_plugins", 3)
        profile.update_preferences()
        driver = webdriver.Firefox(
            executable_path=r"C:\Users\glorious\geckodriver.exe",
            firefox_profile=profile,
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )
        try:
            driver.get(details.sw_url)
        except Exception as _:
            # write_to_log()
            return None
        return driver

    def reset(self, vpn, driver, details):
        if driver:
            driver.close()
        vpn.disconnect()
        while vpn.status() != "Disconnected":
            time.sleep(0.01)
        time.sleep(random.randint(details.extra_time[0], details.extra_time[1]))

    def wait(self):
        time.sleep(random.uniform(1.75, 3.75))

    def type_to_element(self, element, str):
        for c in str:
            time.sleep(random.uniform(0.075, 0.25))
            element.send_keys(c)

    def generate_bsc(self):
        address = "0x"
        for _ in range(40):
            random_number = str(random.randint(0, 9))
            random_char = random.choice(hex_chars)
            if random.random() < 0.5:
                address += random_number
            else:
                if random.random() < 0.5:
                    random_char = random_char.upper()
                address += random_char
        return address

    def write_to_log(self):
        with open(path, "a+") as f:
            time = dt.now().strftime("%d-%m-%Y %H:%M:%S")
            f.write(
                f"""---{time}---

            {traceback.format_exc()}
    -------------------------
            \n"""
            )

    def delete_log(self):
        if os.path.exists(path):
            os.remove(path)


class SW(Bot):
    def run(self, details):
        completed = 0
        while completed < details.amount_to_complete:
            if not super().connect_vpn():
                continue  # Continue if something went wrong while connecting VPN
            driver = super().get_browser_driver(details)
            try:
                if driver is None:
                    raise TimeoutException()  # Continue if something went wrong while creating browser driver
                # wait()
                if details.has_referral:
                    self.solve_referral(driver, details)
                if details.has_captcha:
                    self.solve_captcha(driver)
                username, email = self.get_random_user()
                self.solve_username(driver, username)
                if details.has_email_verification:
                    email, email_name, token = self.get_email_details()
                self.solve_email(driver, email)
                if details.has_bsc_address_field:
                    self.solve_bsc_address(driver, details.bsc_address_field_id)
                self.solve_arithmetic(driver)
                if not self.send_form(driver):
                    raise TimeoutException()
                if details.has_email_verification:
                    self.solve_email_verification(driver, token, email_name)
                # Wait for a bit to see if send was succesful, if it was, close immediately to save time
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sw_share_link"))
                )
            except (
                TimeoutException,
                NoSuchWindowException,
                UnexpectedAlertPresentException,
                StaleElementReferenceException,
            ) as _:
                # write_to_log()
                super().reset(vpn, driver, details)
                continue
            except Exception as _:
                # write_to_log()
                None
            completed += 1
            print(
                f"{driver.title}: completed {completed} out of {details.amount_to_complete}."
            )
            super().reset(vpn, driver, details)
        print("Finished!")

    def solve_arithmetic(self, driver):
        try:
            skill_question = driver.find_element_by_css_selector(
                "#stq_skill_question span:first-child"
            ).text
            sq_numbers = []
            cur_num = ""
            for c in skill_question:
                if c.isdigit():
                    cur_num += c
                else:
                    if len(cur_num) > 0:
                        sq_numbers.append(int(cur_num))
                    cur_num = ""
            skill_question_answer = driver.find_element_by_id(
                "stq_skill_question_answer"
            )
            sq_answer = str(sq_numbers[0] + sq_numbers[1])
            super().type_to_element(skill_question_answer, sq_answer)
            super().wait()
        except Exception as _:
            # write_to_log()
            None

    def solve_referral(self, driver, details):
        try:
            # Check if referral field is found
            referral_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "referral_source"))
            )
            if random.random() < 0.33:
                referral_to_input = details.referral_name.lower()
            elif random.random() < 0.66:
                referral_to_input = details.referral_name.capitalize()
            else:
                referral_to_input = details.referral_name
            super().type_to_element(referral_field, referral_to_input)
            super().wait()
        except Exception as _:
            # write_to_log()
            None

    def solve_captcha(self, driver):
        try:
            # Wait until captcha is solved
            WebDriverWait(driver, 60).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, "status"), "Solved")
            )
            driver.find_element_by_name("security_check_submit").click()
            super().wait()
        except Exception as _:
            # write_to_log()
            None

    def get_email_details(self):
        response_create = requests.put(
            url="https://www.developermail.com/api/v1/mailbox"
        )
        result = response_create.json()
        email_name = result["result"]["name"]
        return f"{email_name}@developermail.com", email_name, result["result"]["token"]

    def solve_email_verification(self, driver, token, email_name):
        try:
            verify_email_1 = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "verify_email_input_1"))
            )
            verify_email_2 = driver.find_element_by_id("verify_email_input_2")
            verify_email_3 = driver.find_element_by_id("verify_email_input_3")
            verify_email_4 = driver.find_element_by_id("verify_email_input_4")
            while True:
                response_ids = requests.get(
                    url=f"https://www.developermail.com/api/v1/mailbox/{email_name}",
                    headers={
                        "accept": json_data,
                        "X-MailboxToken": token,
                    },
                )
                result = response_ids.json()["result"]
                if len(result) > 0:
                    email_id = result[0]
                    break
            email_data = f'["{email_id}"]'
            response_msg = requests.post(
                url=f"https://www.developermail.com/api/v1/mailbox/{email_name}/messages",
                headers={
                    "accept": json_data,
                    "X-MailboxToken": token,
                    "Content-Type": json_data,
                },
                data=email_data,
            )
            email_final = response_msg.json()["result"][0]["value"]
            match = re.search(string=email_final, pattern="[>][0-9]{4}[<]")
            nums = [c for c in match.group(0) if c.isalnum()]
            super().type_to_element(verify_email_1, nums[0])
            super().type_to_element(verify_email_2, nums[1])
            super().type_to_element(verify_email_3, nums[2])
            super().type_to_element(verify_email_4, nums[3])
            verify_email_submit = driver.find_element_by_id("verify_email_submit")
            verify_email_submit.click()
            super().wait()
        except Exception as _:
            # write_to_log()
            None

    def solve_bsc_address(self, driver, bsc_address_field_id):
        try:
            bsc_field = driver.find_element_by_id(bsc_address_field_id)
            bsc_field.clear()
            super().type_to_element(bsc_field, super().generate_bsc())
            super().wait()
        except Exception as _:
            # write_to_log()
            None

    def send_form(self, driver):
        # Send details form
        enter_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "sw_login"))
        )
        enter_button.click()
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            try:
                driver.switch_to.alert.dismiss()
            except Exception as _:
                None
            return False
        except Exception as _:
            # write_to_log()
            None
        return True

    def solve_email(self, driver, email):
        # Input email
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "sw_login_email"))
        )
        email_field.clear()
        super().type_to_element(email_field, email)
        super().wait()

    def solve_username(self, driver, username):
        # Input username
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "sw_login_name"))
        )
        username_field.clear()
        super().type_to_element(username_field, username)
        super().wait()


class VS(Bot):
    def run(self, details):
        completed = 0
        while completed < details.amount_to_complete:
            if not super().connect_vpn():
                continue  # Continue if something went wrong while connecting VPN
            pyautogui.click(x=652, y=999)
            time.sleep(3)
            pyautogui.click(x=170, y=45)
            time.sleep(3)
            pyautogui.write(details.sw_url, interval=0.175)
            time.sleep(1)
            pyautogui.press("enter")
            time.sleep(15)
            pyautogui.click(x=700, y=700)
            pyautogui.scroll(-10000)
            time.sleep(3)
            pyautogui.click(x=340, y=737)
            time.sleep(3)
            _, email = super().get_random_user()
            for c in email:
                keyboard.write(c)
                time.sleep(0.175)
            time.sleep(1)
            pyautogui.press("enter")
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
            super().reset(vpn, None, details)
            print(pygetwindow.getActiveWindowTitle())
            completed += 1
            print(f"Completed {completed} out of {details.amount_to_complete}.")
            time.sleep(random.randrange(details.extra_time[0], details.extra_time[1]))
        print("Finished!")


for details in todo:
    if details.sw_url.find("sweepwidget") != -1:
        bot = SW()
    elif details.sw_url.find("swee.ps") != -1:
        bot = VS()
    bot.run(details)