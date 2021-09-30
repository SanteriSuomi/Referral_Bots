from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver import DesiredCapabilities

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
    "gmx.com",
]

fake_per = Faker(["en", "en_GB", "en_IE", "en_NZ", "en_TH", "en_US"])
fake_email = Faker(["en", "en_GB", "en_IE", "en_NZ", "en_TH", "en_US"])


class Details:
    def __init__(
        self,
        sw_url,  # SW url
        amount_to_complete,  # How many to complete until stopping
        has_referral,  # If there is a referral field preset
        referral_name,  # If has_referral is true, what referral to enter (your SW username)
        has_email_verification,  # If there is email verification present (asking for a 4 digit code)
        has_captcha,  # If there is a captcha question present at the start
        has_bsc_address_field,  # If there is a field asking for BSC wallet address
        bsc_address_field_id,  # If has_bsc_address is true, give here the ID of the HTML element that
        # corresponds to the field (right click in browser -> inspect -> hover over the field,
        # and you should find the id="XXXX" in the dev tools window), the reason this needs to be is because this field ID
        # can change from SW to SW
        extra_time,  # Range of extra time in seconds added after each loop to make the bot appear more legit.
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
        sw_url="https://sweepwidget.com/view/33937-643t8fwv/978f34-33937",
        amount_to_complete=2,
        has_referral=False,
        referral_name="StygeXD",
        has_email_verification=False,
        has_captcha=False,
        has_bsc_address_field=False,
        bsc_address_field_id="sw_text_input_15_1",
        extra_time=(0, 0),
    )
]


def run():
    for details in todo:
        completed = 0
        while completed < details.amount_to_complete:
            if not connect_vpn():
                continue  # Continue if something went wrong while connecting VPN
            driver = get_browser_driver(details)
            try:
                if driver is None:
                    raise TimeoutException()  # Continue if something went wrong while creating browser driver
                wait()

                if details.has_referral:
                    solve_referral(driver, details)
                if details.has_captcha:
                    solve_captcha(driver)

                username, email = get_random_user()
                solve_username(driver, username)

                if details.has_email_verification:
                    email, email_name, token = get_email_details()

                solve_email(driver, email)

                if details.has_bsc_address_field:
                    solve_bsc_address(driver, details.bsc_address_field_id)

                send_form(driver)

                if details.has_email_verification:
                    solve_email_verification(driver, token, email_name)

                # Wait for a bit to see if send was succesful, if it was, close immediately to save time
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sw_share_link"))
                )
            except (
                TimeoutException,
                NoSuchWindowException,
                UnexpectedAlertPresentException,
                StaleElementReferenceException,
            ) as _:
                write_to_log()
                reset(vpn, driver, details)
                continue
            except Exception as _:
                write_to_log()
                None
            completed += 1
            print(
                f"{driver.title}: completed {completed} out of {details.amount_to_complete}."
            )
            reset(vpn, driver, details)
    print("Finished!")


def get_random_user():
    rand = random.random()
    if rand < 0.33:
        username = fake_per.name()
    elif rand < 0.66:
        username = fake_per.first_name()
    else:
        username = fake_per.last_name()

    rand = random.random()
    if rand < 0.33:
        username = username.lower()
    elif rand < 0.66:
        username = username.capitalize()

    username_email = fake_email.first_name()
    if random.random() < 0.5:
        username_email += fake_email.last_name()
    if random.random() < 0.5:
        username_email = username_email.replace(" ", "").lower()
    else:
        username_email = username_email.replace(" ", "")

    if random.random() < 0.5:
        email = f"{username_email}{int(random.uniform(0, 100))}@{random.choice(email_domains)}"
    else:
        email = f"{username_email}@{random.choice(email_domains)}"

    return username, email


def connect_vpn():
    try:
        vpn.set_region(server=random.choice(vpn_regions))
        vpn.connect(verbose=False, timeout=30)
        while vpn.status() != "Connected":
            time.sleep(0.01)
        return True
    except Exception as _:
        write_to_log()
        return False


def get_browser_driver(details):
    shutil.rmtree(r"C:\Users\glorious\AppData\Local\Temp", ignore_errors=True)
    profile = FirefoxProfile(
        r"C:\Users\glorious\AppData\Roaming\Mozilla\Firefox\Profiles\qcdanr2x.default-release"
    )
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference("dom.disable_beforeunload", True)
    profile.update_preferences()
    driver = webdriver.Firefox(
        executable_path=r"C:\Users\glorious\geckodriver.exe",
        firefox_profile=profile,
        desired_capabilities=DesiredCapabilities.FIREFOX,
    )
    try:
        driver.get(details.sw_url)
    except Exception as _:
        write_to_log()
        return None
    return driver


def reset(vpn, driver, details):
    if driver:
        driver.close()
    vpn.disconnect()
    while vpn.status() != "Disconnected":
        time.sleep(0.01)
    time.sleep(random.randint(details.extra_time[0], details.extra_time[1]))


def wait():
    time.sleep(random.uniform(1.5, 3.5))


def type_to_element(element, str):
    for c in str:
        time.sleep(random.uniform(0.1, 0.3))
        element.send_keys(c)


def solve_referral(driver, details):
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
        type_to_element(referral_field, referral_to_input)
        wait()
    except Exception as _:
        write_to_log()
        None


def solve_captcha(driver):
    try:
        # Wait until captcha is solved
        WebDriverWait(driver, 75).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, "status"), "Solved")
        )
        driver.find_element_by_name("security_check_submit").click()
        wait()
    except Exception as _:
        write_to_log()
        None


def get_email_details():
    response_create = requests.put(url="https://www.developermail.com/api/v1/mailbox")
    result = response_create.json()
    email_name = result["result"]["name"]
    return f"{email_name}@developermail.com", email_name, result["result"]["token"]


def solve_email_verification(driver, token, email_name):
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
        type_to_element(verify_email_1, nums[0])
        type_to_element(verify_email_2, nums[1])
        type_to_element(verify_email_3, nums[2])
        type_to_element(verify_email_4, nums[3])
        wait()
        verify_email_submit = driver.find_element_by_id("verify_email_submit")
        verify_email_submit.click()
        wait()
    except Exception as _:
        write_to_log()
        None


def generate_bsc():
    address = "0x"
    for _ in range(40):
        random_number = str(random.randint(0, 9))
        random_char = random.choice(hex_chars)
        if random.random() < 0.5:
            address += random_number
        else:
            if random.random() < 0.5:
                random_char = random_char.capitalize()
            address += random_char
    return address


def solve_bsc_address(driver, bsc_address_field_id):
    try:
        bsc_field = driver.find_element_by_id(bsc_address_field_id)
        bsc_field.clear()
        type_to_element(bsc_field, generate_bsc())
        wait()
    except Exception as _:
        write_to_log()
        None


def send_form(driver):
    # Send details form
    enter_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "sw_login"))
    )
    enter_button.click()
    wait()
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        driver.switch_to.alert.dismiss()
    except Exception as _:
        write_to_log()
        None


def solve_email(driver, email):
    # Input email
    email_field = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "sw_login_email"))
    )
    email_field.clear()
    type_to_element(email_field, email)
    wait()


def solve_username(driver, username):
    # Input username
    username_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, "sw_login_name"))
    )
    username_field.clear()
    type_to_element(username_field, username)
    wait()


def write_to_log():
    with open(path, "a+") as f:
        time = dt.now().strftime("%d-%m-%Y %H:%M:%S")
        f.write(
            f"""---{time}---
        
        {traceback.format_exc()}
-------------------------
        \n"""
        )


def delete_log():
    if os.path.exists(path):
        os.remove(path)


run()