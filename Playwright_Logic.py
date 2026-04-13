# ---------- IMPORTS ----------
import logging
import pytest
import random
import time
import self
from playwright.sync_api import sync_playwright, TimeoutError

# ---------- PAGE OBJECT ----------
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.email = "//input[@type='email']"
        self.next_btn = "//div[@id='identifierNext']"
        self.pass_input = "//input[@type='password']"
        self.pass_next_btn = "//div[@id='passwordNext']"
        self.RECOVERY_EMAIL = "gowatham039leela@gmail.com"
        self.RECOVERY_PHONE = "9498324129"
        self.RECOVERY_EMAIL_XPATH = "//input[@id='knowledge-preregistered-email-response']"
        self.RECOVERY_EMAIL_OPTION = "//div[@data-challengetype='12']"

    def login(self, email, password, recovery_email):
        self.page.goto("https://gmail.com")
        self.page.wait_for_selector(self.email)
        self.page.fill(self.email, email)
        self.page.click(self.next_btn)
        time.sleep(2)
        self.page.wait_for_selector(self.pass_input)
        self.page.fill(self.pass_input, password)
        self.page.click(self.pass_next_btn)
        time.sleep(5)

        # Recovery flow
        try:
            print("[Login] Handling recovery email step...")
            self.page.wait_for_selector(self.RECOVERY_EMAIL_OPTION, timeout=4000)
            self.page.click(self.RECOVERY_EMAIL_OPTION)
            self.page.wait_for_selector(self.RECOVERY_EMAIL_XPATH)
            self.page.fill(self.RECOVERY_EMAIL_XPATH, recovery_email)
            self.page.keyboard.press("Enter")
            logging.info("Recovery email entered successfully")
        except TimeoutError:
            # Recovery step not shown → silently skip
            pass
        except Exception as e:
            logging.error(f"[Login] Unexpected error during recovery step: {e}")

    def logout(self):
        try:
            print("Logging out...")
            logout_url = "https://mail.google.com/mail/logout"
            self.page.goto(logout_url)
            time.sleep(5)
            print("Logout successful!")
        except Exception as e:
            print(f"Logout failed: {e}")

# ---------- SELECT % ----------
def select_percentage(emails, pct=0.10):
    total = len(emails)
    count = int(total * pct)
    return random.sample(emails, count) if count > 0 else []

# ---------- ACTION ASSIGNMENT ----------
def assign_actions(email_list):
    total = len(email_list)
    weights = {"read": 0.10, "reply": 0.20, "click": 0.20}
    bucket = []
    for action, pct in weights.items():
        bucket.extend([action] * int(total * pct))
    remaining = total - len(bucket)
    for _ in range(remaining):
        bucket.append(random.choice(list(weights.keys())))
    random.shuffle(bucket)
    return {email_list[i]["id"]: bucket[i] for i in range(total)}
#hari0112krishna@gmail.com;Hari0112;140.228.27.87;12323;14a6de8916a01;aa267ffe92;baseballtaco256373910@gmail.com;1234567890
# ---------- PLAYWRIGHT FIXTURE ----------
@pytest.fixture()
def page():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    data = {
        "Email": "hari0112krishna@gmail.com",
        "Password": "Hari0112",
        "RECOVERY_EMAIL" : "baseballtaco256373910@gmail.com"
    }
    LoginPage(page).login(data["Email"], data["Password"], data["RECOVERY_EMAIL"])
    yield page
    context.close()
    browser.close()
    pw.stop()

#---------- TEST ----------
def test_gmail_search_with_logic(page):
    time.sleep(5)
    search_box = page.wait_for_selector("//input[@aria-label='Search mail']")
    KEYWORDS = "constantupdates OR notifiworks OR postalerts"
    QUERY = f"in:unread {KEYWORDS}"
    search_box.fill(QUERY)
    search_box.press("Enter")
    time.sleep(3)
    # Email rows
    rows = page.locator("tr.zA")
    row_count = rows.count()
    emails = []

    for idx in range(row_count):
        try:
            subject = rows.nth(idx).locator("span.bog").inner_text()
        except:
            subject = "No subject"
        emails.append({"id": idx + 1, "subject": subject})
    if not emails:
        print("no unread mails")
        return

    selected = select_percentage(emails, pct=0.10)
    print(f"\nSelected {len(selected)} of {len(emails)}\n")
    actions = assign_actions(selected)
    grouped = {"read": [], "reply": [], "click": []}

    for mail in selected:
        grouped[actions[mail["id"]]].append(mail)
    # Keyboard focus
    page.locator("body").click()
    time.sleep(1)

    # ---------- EXECUTION ----------
    for act in ["read", "reply", "click"]:

        for mail in grouped[act]:
            print(f"Processing mails -> {mail['id']} ({act})")
            # OPEN email
            page.keyboard.press("o")
            time.sleep(2)
            # ----------------- READ -----------------
            if act == "read":
                print("Read done.")
            # ----------------- REPLY -----------------
            elif act == "reply":
                try:
                    page.keyboard.press("r")
                    time.sleep(1)
                    box = page.locator("div[aria-label='Message Body']")
                    box.fill("Thanks for the informative messages and be in touch!!")
                    time.sleep(3)
                    page.keyboard.press("Control+Enter")
                    time.sleep(3)
                    print("Reply done.")
                except Exception as e:
                    print(f"Reply failed: {e}")

            # ----------------- CLICK -----------------
            elif act == "click":
                try:
                    links = page.locator("//a[@data-saferedirecturl]")
                    if links.count() > 0:
                        links.first.click()
                        time.sleep(3)
                        page.evaluate("window.scrollBy(0,1500)")
                        time.sleep(2)
                        tabs = page.context.pages
                        if len(tabs) > 1:
                            tabs[-1].close()
                            print("Click done.")
                    else:
                        print("No redirect link.")
                except Exception as e:
                    print(f"Click failed: {e}")

            # Go back with 'u'
            page.keyboard.press("u")
            time.sleep(2)
            # Next with 'j'
            page.keyboard.press("j")
            time.sleep(1)
    print("\nActions Done & Dusted successfully!!!!!!")
    LoginPage(page).logout()



