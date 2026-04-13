import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY="00"
client = genai.Client(api_key=GEMINI_API_KEY)

# meena152sindhu2000@gmail.com;Meena@1522000
#kalaivani888vk@gmail.com;Wqbaby0072k;45.86.54.67;12323;14a6de8916a01;aa267ffe92;leela12ravi2000@gmail.com;9444852751
GMAIL_EMAIL = "meena152sindhu2000@gmail.com"
GMAIL_PASSWORD = "Meena@1522000"
RECOVERY_EMAIL = "leela12ravi2000@gmail.com"
RECOVERY_PHONE= "9444852751"
RECOVERY_EMAIL_XPATH="//input[@id='knowledge-preregistered-email-response']"
RECOVERY_EMAIL_OPTION ="//div[@data-challengetype='12']"
INBOX_SEARCH_KEYWORD = "notifiworks OR Postalerts OR Constantupdates"



# OPENAI API KEY (STATIC)
# # Initialize client with static key
# client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------- AI CLASSIFIER -------------------
def classify_with_ai(summary: str) -> str:
    """AI decides whether to Reply or Click (50/50 logic)."""
    prompt = f"""
    You are an intelligent Gmail assistant.

    Read the email summary below and choose exactly ONE action:
    - Reply → if the email needs a response, question, or acknowledgment.
    - Click → ONLY if there is a safe, non-sensitive link 
          (examples: promo pages, newsletters, public info links).

    Sensitive link examples (do NOT click these):
    - Banking or financial pages
    - OTP / verification links
    - Password reset links
    - Account recovery links
    - Personal data or identity confirmation links

    Keep an overall 50/50 balance in your decisions.

    Email summary: "{summary}"
    """

    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={"temperature": 0.5}
    )
    decision = resp.text.strip().capitalize()

    if decision not in ["Reply", "Click"]:
        decision = random.choice(["Reply", "Click"])
    return decision

# ------------------- DRIVER SETUP -------------------
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def gmail_logout(driver):
    try:
        print("Logging out from Gmail...")

        # Direct logout URL (no tab switching, no closing)
        driver.get("https://accounts.google.com/Logout")
        time.sleep(5)

        print("Logout completed.")

    except Exception as e:
        print("Logout failed:", e)

# ------------------- MAIN FLOW -------------------
def run_gmail_ai_flow():
    driver = setup_driver()
    wait = WebDriverWait(driver, 25)

    driver.get("https://mail.google.com/")
    time.sleep(3)

    # --- LOGIN ---
    try:
        print("[Login] Logging into Gmail...")
        wait.until(EC.presence_of_element_located((By.ID, "identifierId"))).send_keys(GMAIL_EMAIL)
        driver.find_element(By.ID, "identifierNext").click()
        time.sleep(3)
        wait.until(EC.presence_of_element_located((By.NAME, "Passwd"))).send_keys(GMAIL_PASSWORD)
        driver.find_element(By.ID, "passwordNext").click()
        time.sleep(5)
        try:
            print("[Login] Handling recovery email step...")

            # Find and click recovery email option
            recovery_email_option = wait.until(
                EC.visibility_of_element_located((By.XPATH, RECOVERY_EMAIL_OPTION))
            )
            recovery_email_option.click()

            # Enter recovery email
            recovery_email_input = wait.until(
                EC.visibility_of_element_located((By.XPATH, RECOVERY_EMAIL_XPATH))
            )
            recovery_email_input.clear()
            recovery_email_input.send_keys(RECOVERY_EMAIL)
            recovery_email_input.send_keys(Keys.ENTER)

            logging.info("Recovery email entered successfully")

        except Exception:
            print("[Login] No recovery email step shown. Continuing login...")
    except Exception:
        print("[Login] Already logged in or manual step needed.")
        time.sleep(5)

    # --- SEARCH EMAILS ---
    print(f"[Search] Searching inbox for keyword: {INBOX_SEARCH_KEYWORD}")
    search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
    search_box.clear()
    search_box.send_keys(f"in:unread {INBOX_SEARCH_KEYWORD}")
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    body = driver.find_element(By.TAG_NAME, "body")

    # --- LOOP THROUGH EMAILS USING KEYBOARD SHORTCUTS ---
    for i in range(7):  # Process first 5 mails
        try:
            print(f"\n Processing Email #{i+1}")
            body.send_keys("o")  # open email
            print(" Opened current email.")
            time.sleep(6)

            # --- Extract Subject & Body ---
            try:
                subject = driver.find_element(By.CSS_SELECTOR, "h2.hP").text
            except NoSuchElementException:
                subject = "(No Subject)"

            try:
                body_text = driver.find_element(By.CSS_SELECTOR, "div.a3s").text[:400]
            except NoSuchElementException:
                body_text = ""

            summary = f"Subject: {subject}. Body: {body_text}"
            decision = classify_with_ai(summary)
            print(f" AI Decision: {decision}")

            # --- REPLY LOGIC ---
            if decision.lower() == "reply":
                try:
                    ai_reply_prompt = f"""
                    You're an automated Gmail assistant.
                    Write a short, friendly, natural reply (1–2 sentences).
                    Avoid commitments like 'I'll follow up' or 'Let's schedule'.
                    Keep it warm, polite, and casual — examples:
                    - "Thanks for the offer! It sounds interesting."
                    - "Appreciate the details — looks good."
                    - "Thanks for sharing this, sounds great."
                    Email:
                    Subject: {subject}
                    Body: {body_text}
                    """
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=ai_reply_prompt,
                        config={
                            "temperature": 0.7
                        }
                    )

                    ai_reply = response.text.strip()

                    print(f" Generated Reply: {ai_reply}")

                    reply_btn = driver.find_element(By.XPATH, "//span[text()='Reply']")
                    reply_btn.click()
                    time.sleep(2)

                    reply_box = driver.find_element(By.CSS_SELECTOR, "div.Am.Al.editable.LW-avf")

                    reply_box.send_keys(ai_reply)
                    time.sleep(2)
                    try:
                        popup_close = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//span[text()='No thanks']")
                            )
                        )
                        popup_close.click()
                        print("Closed Gmail notification popup")
                    except:
                        pass
                    send_btn = driver.find_element(By.XPATH, "//div[text()='Send']")
                    driver.execute_script("arguments[0].scrollIntoView(true);", send_btn)
                    driver.execute_script("arguments[0].click();", send_btn)
                    time.sleep(2)

                    print(" Reply sent successfully.")

                except Exception as e:
                    print(f"[Reply Error] {e}")

            # --- CLICK LOGIC ---
            elif decision.lower() == "click":
                try:
                    print(" Performing simple click action...")
                    original_window = driver.current_window_handle
                    time.sleep(2)

                    sources = driver.find_elements(By.XPATH, "//a[@data-saferedirecturl]")
                    url = None
                    excluded = [
                        "ci3.googleusercontent.com/meips/ADKq_NZTrJt",
                        "ci3.googleusercontent.com/meips/ADKq_NbOzFss3k8AEL"
                    ]

                    for src in sources:
                        try:
                            candidate = src.get_attribute("href")
                            if candidate and not any(ex in candidate for ex in excluded):
                                url = candidate
                                break
                        except Exception:
                            continue

                    if url:
                        print(f" Found link: {url}")
                        driver.execute_script("window.open(arguments[0]);", url)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(4)
                        driver.execute_script("window.scrollBy(0, 1500);")
                        print(" Link opened and scrolled successfully.")
                    else:
                        print(" No valid link found in this email.")
                except Exception as e:
                    print(f"[Click Error] {e}")
                finally:
                    try:
                        handles = driver.window_handles

                        if len(handles) > 1:
                            current = driver.current_window_handle

                            if current != original_window:
                                driver.switch_to.window(current)
                                driver.close()

                            driver.switch_to.window(original_window)

                    except Exception as e:
                        print("[Window Cleanup Error]", e)

                    print("Returned to Gmail tab.")

            # --- Move to Next Email (Keyboard Shortcut) ---
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys("j")  # go to next mail
            print(" Moved to next email.")
            time.sleep(5)

        except Exception as e:
            print(f"[Error Processing Email #{i+1}] {e}")
            body.send_keys("j")
            time.sleep(5)

    print("\n All emails processed successfully.")
    gmail_logout(driver)
    driver.quit()

# ------------------- RUN -------------------
if __name__ == "__main__":
    run_gmail_ai_flow()
