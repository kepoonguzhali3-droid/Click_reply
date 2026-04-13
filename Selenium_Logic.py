# ---------- IMPORTS ----------
import logging

import pytest
import random
import time
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait


# ---------- PAGE OBJECT ----------
class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.email = "//input[@type='email']"
        self.next_btn = "//div[@id='identifierNext']"
        self.pass_input = "//input[@type='password']"
        self.pass_next_btn = "//div[@id='passwordNext']"
        self.RECOVERY_EMAIL = "gowatham039leela@gmail.com"
        self.RECOVERY_PHONE = "9498324129"
        self.RECOVERY_EMAIL_XPATH = "//input[@id='knowledge-preregistered-email-response']"
        self.RECOVERY_EMAIL_OPTION = "//div[@data-challengetype='12']"


    def login(self, email, password, recovery_email):

        self.driver.get("https://gmail.com")

        wait = WebDriverWait(self.driver, 20)

        wait.until(
            EC.visibility_of_element_located((By.XPATH, self.email))
        ).send_keys(email)

        self.driver.find_element(By.XPATH, self.next_btn).click()
        time.sleep(2)

        wait.until(
            EC.visibility_of_element_located((By.XPATH, self.pass_input))
        ).send_keys(password)

        self.driver.find_element(By.XPATH, self.pass_next_btn).click()
        time.sleep(5)

        try:
            print("[Login] Handling recovery email step...")

            # Try to click the recovery email option
            recovery_email_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.RECOVERY_EMAIL_OPTION))
            )
            recovery_email_option.click()

            # Enter recovery email
            recovery_email_input = wait.until(
                EC.visibility_of_element_located((By.XPATH, self.RECOVERY_EMAIL_XPATH))
            )
            recovery_email_input.clear()
            recovery_email_input.send_keys(recovery_email)
            recovery_email_input.send_keys(Keys.ENTER)

            logging.info("Recovery email entered successfully")

        except TimeoutException:
            # Recovery step not shown → silently skip
            pass

        except Exception as e:
            # Only log unexpected errors
            logging.error(f"[Login] Unexpected error during recovery step: {e}")




# ---------- SELECT % ----------
def select_percentage(emails, pct=0.10):
    total = len(emails)
    count = int(total * pct)
    return random.sample(emails, count) if count > 0 else []


# ---------- ACTION ASSIGNMENT ----------
def assign_actions(email_list):
    total = len(email_list)

    weights = {
        "read": 0.10,
        "reply": 0.20,
        "click": 0.20
    }

    bucket = []

    # Base distribution
    for action, pct in weights.items():
        bucket.extend([action] * int(total * pct))

    # Remaining → random
    remaining = total - len(bucket)
    for _ in range(remaining):
        bucket.append(random.choice(list(weights.keys())))

    random.shuffle(bucket)
    return {email_list[i]["id"]: bucket[i] for i in range(total)}


# ---------- SELENIUM FIXTURE ----------
@pytest.fixture()
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
#linmeza845@gmail.com;Sywyjrhpgvq;94.131.68.100;12323;14a6de8916a01;aa267ffe92;truonganhpod232@gmail.com;9498324195
    data = {
        "Email": "linmeza845@gmail.com",
        "Password": "Sywyjrhpgvq",
        "RECOVERY_EMAIL" : "truonganhpod232@gmail.com"
    }
    LoginPage(driver).login(data["Email"], data["Password"], data["RECOVERY_EMAIL"])

    yield driver
    driver.quit()


# ---------- TEST ----------
def test_gmail_search_with_logic(driver):

    wait = WebDriverWait(driver, 25)

    # Search box
    search = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//input[@aria-label='Search mail']"))
    )
    time.sleep(3)

    KEYWORDS = "constantupdates OR notifiworks OR postalerts"
    QUERY = f"is:unread {KEYWORDS}"

    search.send_keys(QUERY)
    search.send_keys(Keys.ENTER)

    time.sleep(3)

    # Email rows
    email_rows = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.zA"))
    )

    emails = []
    for idx, row in enumerate(email_rows, start=1):
        try:
            subject = row.find_element(By.CSS_SELECTOR, "span.bog").text
        except:
            subject = "No subject"

        emails.append({"id": idx, "subject": subject})

    if not emails:
        print("no unread mails")
        return

    selected = select_percentage(emails, pct=0.10)
    print(f"\nSelected {len(selected)} of {len(emails)}\n")

    actions = assign_actions(selected)

    # Grouping
    grouped = {"read": [], "reply": [], "click": []}

    for mail in selected:
        grouped[actions[mail["id"]]].append(mail)

    # Body element for shortcut keys
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    time.sleep(1)

    # ---------- EXECUTION ----------
    for act in ["read", "reply", "click"]:
        for mail in grouped[act]:

            print(f"Processing mails -> {mail['id']} ({act})")

            # OPEN email using 'o'
            body.send_keys("o")
            time.sleep(2)

            # ----------------- READ -----------------
            if act == "read":
                print("Read done.")

            # ----------------- REPLY -----------------
            elif act == "reply":
                print("Replying...")
                try:
                    body.send_keys("r")
                    time.sleep(1)

                    box = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Message Body']"))
                    )
                    box.send_keys("Thanks for the informative messages and be in touch!!")

                    # Send using Ctrl + Enter
                    time.sleep(5)
                    body.send_keys(Keys.CONTROL, Keys.ENTER)
                    time.sleep(5)

                except Exception as e:
                    print(f"Reply failed: {e}")

            # ----------------- CLICK -----------------
            elif act == "click":
                print("Clicking link...")
                try:
                    links = driver.find_elements(By.XPATH, "//a[@data-saferedirecturl]")

                    if len(links) > 0:
                        links[0].click()
                        time.sleep(3)
                        tabs = driver.window_handles
                        driver.switch_to.window(tabs[-1])
                        driver.execute_script("window.scrollBy(0,1500)")
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(tabs[0])
                    else:
                        print("No redirect link.")

                except Exception as e:
                    print(f"Click failed: {e}")

            # Go back with 'u'
            body.send_keys("u")
            time.sleep(2)

            # Next with 'j'
            body.send_keys("j")
            time.sleep(1)
    print("\nActions Done & Dusted successfully!!!!!!")
    # --- LOGOUT USING LOGOUT URL ---
    try:
        logout_url = "https://mail.google.com/mail/logout"  # <-- Use your actual logout URL here
        driver.get(logout_url)
        time.sleep(2)
        print("Logged out successfully!")
    except Exception as e:
        print(f"Logout failed: {e}")
