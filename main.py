import argparse
import time
from typing import Final

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Constants
USERNAME: Final = "daniel"
BASE_URL: Final = "https://www.heylo.com"
LOGIN_URL: Final = f"{BASE_URL}/login"
EVENTS_URL: Final = f"{BASE_URL}/events/85c6b042-62cd-47f3-a439-1dd9417f4246"
CHROME_USER_DATA_DIR: Final = (
    f"/Users/{USERNAME}/Library/Application Support/Google/Chrome/"
)
CHROME_PROFILE: Final = "Default"


def setup_driver() -> WebDriver:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
    chrome_options.add_argument(f"profile-directory={CHROME_PROFILE}")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )


def wait_for_login(driver: WebDriver) -> None:
    if LOGIN_URL not in driver.current_url:
        input("Press Enter to start registration (you're already logged in)...")
        return
    input("Please log in manually and press Enter when done...")
    while LOGIN_URL in driver.current_url:
        time.sleep(1)


def register_for_event(driver: WebDriver, event_url: str) -> None:
    driver.get(event_url)
    try:
        # Click the register button
        register_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(text(), \"S'inscrire\") or contains(text(), 'Register')]",
                )
            )
        )
        register_button.click()

        # Click the continue button
        continue_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(text(), 'Continue') or contains(text(), 'Continuer')]",
                )
            )
        )
        continue_button.click()

        # Click the skip button
        skip_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(text(), 'Skip') or contains(text(), 'Passer')]",
                )
            )
        )
        skip_button.click()

        print("Successfully registered for the event!")
        print("Keeping window open. Press Ctrl+C to exit...")
    except TimeoutException:
        print("Registration button not found or not clickable")
        input("Press Enter to try registering again...")


def find_montmartre_event(soup: BeautifulSoup) -> str | None:
    return find_event(
        soup, title="Thursday - Montmartre Stairs Challenge", weekday=("jeu.", "Thu")
    )


def find_bootcamp_event(soup: BeautifulSoup) -> str | None:
    return find_event(soup, title="Tuesday Bootcamp Run", weekday=("mar.", "Tue"))


def find_event(soup: BeautifulSoup, title: str, weekday: tuple[str, str]) -> str | None:
    event_cards = soup.select('[data-testid^="event-card--"]')
    for card in event_cards:
        title_elem = card.select_one(".r-8akbws.r-krxsd3")
        date_elem = card.select_one(".r-3s2u2q.r-1iln25a")

        if not (title_elem and date_elem):
            continue

        if title in title_elem.text and any(day in date_elem.text for day in weekday):
            return card["data-testid"].split("--")[1]
    return None


def get_event(find_event_func: callable) -> None:
    driver = setup_driver()
    driver.get(LOGIN_URL)
    wait_for_login(driver)

    while True:
        try:
            driver.get(EVENTS_URL)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-testid^="event-card--"]')
                )
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            if event_id := find_event_func(soup):
                register_for_event(driver, f"{EVENTS_URL}/-{event_id}")
                while True:
                    time.sleep(60)  # Keep the window open indefinitely

            print("No upcoming event found")
            input("Press Enter to try again...")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            input("Press Enter to try again...")


def main():
    parser = argparse.ArgumentParser(description="Heylo event registration automation")
    parser.add_argument(
        "event_type",
        choices=["montmartre", "bootcamp"],
        help="Type of event to register for",
    )

    args = parser.parse_args()

    event_finders = {
        "montmartre": find_montmartre_event,
        "bootcamp": find_bootcamp_event,
    }

    get_event(event_finders[args.event_type])


if __name__ == "__main__":
    main()
