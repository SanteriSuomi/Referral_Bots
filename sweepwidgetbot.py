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

from faker import Faker
from faker.providers import user_agent

import shutil
import random
import time
from piapy import PiaVpn
import requests
import re

random.seed(time.time())
Faker.seed(time.time())
vpn = PiaVpn()


def get_usable_regions(vpn):
    return [r for r in vpn.regions() if r.find("streaming") == -1]


vpn_regions = get_usable_regions(vpn)
email_domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "icloud.com"]

fake_ua = Faker()
fake_ua.add_provider(user_agent)
fake_per = Faker(["en", "en_GB", "en_IE", "en_NZ", "en_TH", "en_US"])
fake_email = Faker(["en", "en_GB", "en_IE", "en_NZ", "en_TH", "en_US"])


def get_random_user():
    if random.random() < 0.5:
        username = fake_per.name()
    else:
        username = fake_per.first_name()
    if random.random() < 0.5:
        username = username.lower()

    username_email = fake_email.first_name()
    if random.random() < 0.5:
        username_email += fake_email.first_name()
    username_email = username_email.replace(" ", "").lower()
    if random.random() < 0.5:
        email = f"{username_email}{int(random.uniform(0, 1001))}@{random.choice(email_domains)}"
    else:
        email = f"{username_email}@{random.choice(email_domains)}"

    return username, email


def connect_vpn():
    vpn.set_region(server=random.choice(vpn_regions))
    vpn.connect(verbose=False, timeout=30)
    while vpn.status() != "Connected":
        time.sleep(0.01)
    return vpn


def get_driver(details):
    shutil.rmtree(r"C:\Users\glorious\AppData\Local\Temp", ignore_errors=True)
    profile = FirefoxProfile(
        r"C:\Users\glorious\AppData\Roaming\Mozilla\Firefox\Profiles\qcdanr2x.default-release"
    )
    driver = webdriver.Firefox(
        executable_path=r"C:\Users\glorious\geckodriver.exe", firefox_profile=profile
    )
    try:
        driver.get(details.url)
    except Exception as _:
        return None
    return driver


def reset(vpn, driver):
    driver.close()
    vpn.disconnect()
    while vpn.status() != "Disconnected":
        time.sleep(0.01)


def wait():
    time.sleep(random.uniform(2, 4))


def type_to_element(element, str):
    for c in str:
        time.sleep(random.uniform(0.05, 0.25))
        element.send_keys(c)


class Details:
    def __init__(self, ref, url, to_complete, is_email) -> None:
        self.ref = ref
        self.url = url
        self.to_complete = to_complete
        self.is_email = is_email  # Does this sweepwidget contain an email verification?


todo = [
    Details(
        "StygeXD",
        "https://share-w.in/2fdwku-31709",
        10,
        False,
    )
]


def run():
    for details in todo:
        completed = 0
        while completed < details.to_complete:
            connect_vpn()
            driver = get_driver(details)
            if driver is None:
                continue
            try:
                if not details.is_email:
                    try:
                        # Check if referral field is found
                        referral_field = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.NAME, "referral_source"))
                        )
                        if random.random() < 0.33:
                            referral_to_input = details.ref.lower()
                        elif random.random() < 0.66:
                            referral_to_input = details.ref.capitalize()
                        else:
                            referral_to_input = details.ref
                        type_to_element(referral_field, referral_to_input)
                        wait()
                    except Exception as _:
                        None
                    try:
                        # Wait until captcha is solved
                        WebDriverWait(driver, 60).until(
                            EC.text_to_be_present_in_element(
                                (By.CLASS_NAME, "status"), "Solved"
                            )
                        )
                        driver.find_element_by_name("security_check_submit").click()
                        wait()
                    except Exception as _:
                        None

                # Input username
                username, email = get_random_user()
                username_field = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "sw_login_name"))
                )
                username_field.clear()
                type_to_element(username_field, username)
                wait()

                if details.is_email:
                    response_create = requests.put(
                        url="https://www.developermail.com/api/v1/mailbox"
                    )
                    result = response_create.json()
                    email_name = result["result"]["name"]
                    token = result["result"]["token"]
                    email = f"{email_name}@developermail.com"

                # Input email
                email_field = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "sw_login_email"))
                )
                email_field.clear()
                type_to_element(email_field, email)
                wait()

                # Send form
                enter_button = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "sw_login"))
                )
                enter_button.click()
                wait()

                if details.is_email:
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
                                "accept": "application/json",
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
                            "accept": "application/json",
                            "X-MailboxToken": token,
                            "Content-Type": "application/json",
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
                    verify_email_submit = driver.find_element_by_id(
                        "verify_email_submit"
                    )
                    verify_email_submit.click()

                # Wait for a bit to see if send was succesful
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sw_share_link"))
                )
            except (
                TimeoutException,
                NoSuchWindowException,
                UnexpectedAlertPresentException,
                StaleElementReferenceException,
            ) as _:
                reset(vpn, driver)
                continue
            except Exception as e:
                print(f"{type(e).__name__}: {e}")
                None
            completed += 1
            print(
                f"{driver.title}: completed {completed} out of {details.to_complete}."
            )
            reset(vpn, driver)
    print("Finished!")


run()