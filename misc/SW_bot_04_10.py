###
### Author Santeri Suomi (boughtthetopkms on telegram), this is WORK IN PROGRESS
###

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.common.exceptions import NoSuchWindowException

from faker import Faker
from piapy import PiaVpn

import shutil
import random
import time
import requests
import re
import pyautogui
import keyboard
import pathlib

random.seed(time.time())
Faker.seed(time.time())
vpn = PiaVpn()
json_data = "application/json"
hex_chars = ["a", "b", "c", "d", "e", "f"]
log_path = (
    pathlib.Path().home() / "Desktop" / "bot_log.txt"
)  # Where log file will be stored (if enabled)
executable_path = r"C:\Users\glorious\geckodriver.exe"  # Path to web driver
profile_path = r"C:\Users\glorious\AppData\Roaming\Mozilla\Firefox\Profiles\qcdanr2x.default-release"  # Path to firefox profile
temp_path = r"C:\Users\glorious\AppData\Local\Temp"  # Path to temporary files folder. Needs to be cleansed from time to time because otherwise it gets too big


vpn_regions = [r for r in vpn.regions() if r.find("streaming") == -1]
email_domains = [
    "gmail.com",
    "outlook.com",
    "yahoo.com",
    "hotmail.com",
    "gmx.com",
]

fake_per = Faker(["en", "en_GB", "en_IE", "en_NZ", "en_TH", "en_US"])
fake_email = Faker(["en", "en_GB", "en_IE", "en_NZ", "en_TH", "en_US"])


class Details:
    def __init__(
        self,
        sw_url,  # URL of contest
        amount_to_complete,  # How entries to complete until stopping
        has_referral=False,  # If there is a referral field preset
        referral_name="",  # If has_referral is true, what referral to enter (your sweep widget username)
        has_email_verification=False,  # If there is email verification present (asking for a 4 digit code)
        has_captcha=False,  # If there is a captcha present at the start
        has_bsc_address_field=False,  # If there is a field asking for BSC wallet address
        bsc_address_field_id="",  # If has_bsc_address_field is True, give here the ID of the HTML element that
        # corresponds to the field (right click in browser -> inspect -> hover over the field,
        # and you should find the id="XXXX" in the dev tools window), the reason this needs to be is because this field ID
        # changes ID depending on sweep widget, and I haven't had time to code a search for it
    ) -> None:
        self.sw_url = sw_url
        self.amount_to_complete = amount_to_complete
        self.has_referral = has_referral
        self.referral_name = referral_name
        self.has_email_verification = has_email_verification
        self.has_captcha = has_captcha
        self.has_bsc_address_field = has_bsc_address_field
        self.bsc_address_field_id = bsc_address_field_id


######## This where you input details about contest you want to do. See above for meanings
todo = [
    Details(
        sw_url="https://sweepwidget.com/view/33937-643t8fwv/978f34-33937",
        amount_to_complete=50,
        has_referral=False,
        referral_name="StygeXD",
        has_email_verification=False,
        has_captcha=False,
        has_bsc_address_field=False,
        bsc_address_field_id="sw_text_input_5_1",
    )
]


class Bot:  # Base class for all bots
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

        if random.random() < 0.8:
            username_email = username_email.lower()
        username_email = "".join(c for c in username_email if c.isalpha())

        if random.random() < 0.5:
            email = f"{username_email}{int(random.uniform(0, 100))}@{random.choice(email_domains)}"
        else:
            email = f"{username_email}@{random.choice(email_domains)}"

        return username, email

    def connect_vpn(self):
        try:
            vpn.set_region(server=random.choice(vpn_regions))
            vpn.connect(verbose=False, timeout=20)
            while vpn.status() != "Connected":
                time.sleep(0.01)
            return True
        except Exception as _:
            return False

    def get_browser_driver(self):
        shutil.rmtree(temp_path, ignore_errors=True)
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities["marionette"] = True
        PROXY = "localhost:3128"
        firefox_capabilities["proxy"] = {
            "proxyType": "MANUAL",
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
        }
        profile = webdriver.FirefoxProfile(profile_path)
        driver = webdriver.Firefox(
            executable_path=executable_path,
            firefox_profile=profile,
            desired_capabilities=firefox_capabilities,
        )
        driver.set_page_load_timeout(20)
        return driver

    def reset(self, vpn):
        pyautogui.click(x=1147, y=68)  # Clean cache
        time.sleep(1)
        pyautogui.click(x=997, y=157)
        time.sleep(1)
        pyautogui.click(x=1221, y=69)  # New user agent
        time.sleep(1)
        pyautogui.click(x=1065, y=348)
        vpn.disconnect()
        while vpn.status() != "Disconnected":
            time.sleep(0.01)

    def wait(self):
        time.sleep(random.uniform(1, 2.5))

    def type_to_element(self, element, str):
        for c in str:
            time.sleep(random.uniform(0.05, 0.2))
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

    # def get_proxy():
    #     url = "https://sweepwidget.com"
    #     proxy_host = "proxy.zyte.com"
    #     proxy_port = "8011"
    #     proxy_auth = (
    #         "3995ae73115447459aaa4c7a68068f23:"  # Make sure to include ':' at the end
    #     )
    #     proxies = {
    #         "https": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
    #         "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
    #     }
    #     result = requests.get(url, proxies=proxies, verify=False)


class SW(Bot):  # Sweep Widget
    def run(self, details):
        completed = 0
        driver = super().get_browser_driver()
        while completed < details.amount_to_complete:
            if not super().connect_vpn():
                continue
            try:
                self.wait()
                driver.get(details.sw_url)
                self.wait()
            except Exception as _:
                continue
            try:
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
                self.wait()

                if details.has_email_verification:
                    self.solve_email_verification(driver, token, email_name)

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sw_share_link"))
                )
            except (
                TimeoutException,
                NoSuchWindowException,
                UnexpectedAlertPresentException,
                StaleElementReferenceException,
            ) as _:
                super().reset(vpn)
                continue
            except Exception as _:
                None
            completed += 1
            print(
                f"{driver.title}: completed {completed} out of {details.amount_to_complete}."
            )
            super().reset(vpn)
        print("Finished!")

    def solve_referral(self, driver, details):
        referral_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "referral_source"))
        )
        if random.random() < 0.33:
            referral_to_input = details.referral_name.lower()
        elif random.random() < 0.66:
            referral_to_input = details.referral_name.capitalize()
        else:
            referral_to_input = details.referral_name
        super().type_to_element(referral_field, referral_to_input)
        self.wait()

    def solve_captcha(self, driver):
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "status"), "Solved")
        )
        driver.find_element_by_name("security_check_submit").click()
        self.wait()

    def solve_username(self, driver, username):
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "sw__login_name"))
        )
        username_field.clear()
        super().type_to_element(username_field, username)
        self.wait()

    def solve_email(self, driver, email):
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "sw__login_email"))
        )
        email_field.clear()
        super().type_to_element(email_field, email)
        self.wait()

    def solve_arithmetic(self, driver):
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
        skill_question_answer = driver.find_element_by_id("stq_skill_question_answer")
        sq_answer = str(sq_numbers[0] + sq_numbers[1])
        super().type_to_element(skill_question_answer, sq_answer)
        self.wait()

    def get_email_details(self):
        response_create = requests.put(
            url="https://www.developermail.com/api/v1/mailbox"
        )
        result = response_create.json()
        email_name = result["result"]["name"]
        return f"{email_name}@developermail.com", email_name, result["result"]["token"]

    def solve_bsc_address(self, driver, bsc_address_field_id):
        bsc_field = driver.find_element_by_id(bsc_address_field_id)
        bsc_field.clear()
        super().type_to_element(bsc_field, super().generate_bsc())
        self.wait()

    def send_form(self, driver):
        enter_button = WebDriverWait(driver, 10).until(
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
            None
        return True

    def solve_email_verification(self, driver, token, email_name):
        verify_email_1 = WebDriverWait(driver, 10).until(
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
        self.wait()


# https://stackoverflow.com/questions/52394408/how-to-use-chrome-profile-in-selenium-webdriver-python-3
class VS(
    Bot
):  # ViralSweep, THIS DOES NOT WORK FOR ALL VIRAL SWEEPS. WILL NEED TO TUNE THE CODE ACCORDINGLY, BECAUSE SELENIUM DOES NOT WORK FOR VIRALSWEEP BECAUSE OF FUCKING CLOUDFLARE. Also, this is very work in progress.
    def run(self, details):
        completed = 0
        while completed < details.amount_to_complete:
            self.open(details)

            pyautogui.click(x=340, y=737)  # Click email field
            _, email = super().get_random_user()
            for c in email:
                keyboard.write(c)  # Write email to email field
                time.sleep(0.175)
            time.sleep(1)
            pyautogui.press("enter")  # Submit details

            self.close()
            super().reset(vpn)
            completed += 1
            print(f"Completed {completed} out of {details.amount_to_complete}.")
        print("Finished!")

    def open(self, details):
        pyautogui.click(x=652, y=999)  # Open chrome
        time.sleep(3)
        pyautogui.click(x=170, y=45)  # Click navigation bar
        time.sleep(3)
        pyautogui.write(details.sw_url, interval=0.175)  # Write URL to navigation bar
        time.sleep(1)
        pyautogui.press("enter")  # Go to URL
        time.sleep(15)  # Wait for cloudflare to pass
        pyautogui.click(
            x=700, y=700
        )  # Click somewhere on the page to make sure chrome is the foreground window
        pyautogui.scroll(-10000)  # Scroll down
        time.sleep(2)

    def close(self):
        pyautogui.click(x=1129, y=53)  # Click clear browsing data extension
        time.sleep(3)
        pyautogui.click(x=898, y=150)  # Clear browsing data
        time.sleep(3)
        pyautogui.click(x=1158, y=49)  # Click random user agent extension
        time.sleep(3)
        pyautogui.click(x=994, y=336)  # New user agent
        time.sleep(3)
        pyautogui.click(x=1250, y=7)  # Close chrome
        time.sleep(2)


class Gleam(Bot):
    def run(self, details):
        completed = 0
        while completed < details.amount_to_complete:
            if not super().connect_vpn():
                continue
            driver = self.get_browser_driver(details)
            # pyautogui.click(x=652, y=999)  # Open chrome
            # time.sleep(3)
            # pyautogui.click(x=170, y=45)  # Click navigation bar
            # time.sleep(3)
            # pyautogui.write(
            #     details.sw_url, interval=0.175
            # )  # Write URL to navigation bar
            # time.sleep(1)
            # pyautogui.press("enter")  # Go to URL
            time.sleep(10)

            # Point(x=642, y=534) # Click login using email
            pyautogui.click(x=642, y=534)
            time.sleep(3)

            # Point(x=589, y=538) # Full Name
            pyautogui.click(x=589, y=538)
            username, email = super().get_random_user()
            for c in username:
                keyboard.write(c)  # Write username
                time.sleep(0.175)
            time.sleep(3)

            # Point(x=577, y=584) # Email
            pyautogui.click(x=577, y=584)
            for c in email:
                keyboard.write(c)  # Write email to email field
                time.sleep(0.175)
            time.sleep(3)

            # Point(x=545, y=630) # Month
            pyautogui.click(x=545, y=630)
            month = str(random.randint(1, 12))
            for c in month:
                keyboard.write(c)
                time.sleep(0.175)
            time.sleep(3)

            # Point(x=603, y=634) # Day
            pyautogui.click(x=603, y=634)
            day = str(random.randint(1, 30))
            for c in day:
                keyboard.write(c)
                time.sleep(0.175)
            time.sleep(3)

            # Point(x=708, y=627) # Year
            pyautogui.click(x=708, y=627)
            day = str(random.randint(1970, 2000))
            for c in day:
                keyboard.write(c)
                time.sleep(0.175)
            time.sleep(3)

            # Point(x=593, y=699) # Wallet
            pyautogui.click(x=593, y=699)
            address = super().generate_bsc()
            for c in address:
                keyboard.write(c)
                time.sleep(0.175)
            time.sleep(3)

            # Point(x=630, y=833) # Save
            pyautogui.click(x=630, y=833)
            time.sleep(3)

            # Point(x=881, y=738) # Press Telegram
            pyautogui.click(x=881, y=738)
            time.sleep(3)

            # Point(x=656, y=807) # Join
            pyautogui.click(x=656, y=807)
            time.sleep(3)

            # Point(x=87, y=11) # Main Window
            pyautogui.click(x=87, y=11)
            time.sleep(3)

            # Point(x=632, y=875) # Continue
            pyautogui.click(x=632, y=875)
            time.sleep(120)
            driver.find_element_by_class_name("button-submit button").click()
            # # Point(x=516, y=417) # Continue
            #             pyautogui.click(x=516, y=417)
            #             time.sleep(20)

            pyautogui.click(x=1129, y=53)  # Click clear browsing data extension
            time.sleep(3)
            pyautogui.click(x=898, y=150)  # Clear browsing data
            time.sleep(3)
            pyautogui.click(x=1158, y=49)  # Click random user agent extension
            time.sleep(3)
            pyautogui.click(x=994, y=336)  # New user agent
            time.sleep(3)
            pyautogui.click(x=1250, y=7)  # Close chrome
            super().reset(vpn, None, details)
            completed += 1
            print(f"Completed {completed} out of {details.amount_to_complete}.")
            if (
                details.extra_time
                and details.extra_time[0] > 0
                and details.extra_time[1] > 0
            ):
                time.sleep(
                    random.randrange(details.extra_time[0], details.extra_time[1])
                )
        print("Finished!")

    def get_browser_driver(self, details):
        shutil.rmtree(temp_path, ignore_errors=True)
        options = webdriver.ChromeOptions()
        options.add_argument(
            r"user-data-dir=C:\Users\glorious\AppData\Local\Google\Chrome\User Data"
        )
        options.add_argument("disable-infobars")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(
            executable_path=r"C:\chromedriver.exe", chrome_options=options
        )
        try:
            driver.get(details.sw_url)
        except Exception as _:
            # write_to_log()
            return None
        return driver


for details in todo:
    if details.sw_url.find("sweepwidget") != -1 or details.sw_url.find("share-w") != -1:
        bot = SW()
    elif details.sw_url.find("swee.ps") != -1:
        bot = VS()
    elif details.sw_url.find("wn.nr") != -1:
        bot = Gleam()
    bot.run(details)
