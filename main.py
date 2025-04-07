import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class HeyloAutomator:
    BASE_URL = "https://www.heylo.com"
    MIDNIGHT_RUNNERS_ID = "85c6b042-62cd-47f3-a439-1dd9417f4246"
    EVENT_TITLES = {
        "montmartre": "Thursday - Montmartre Stairs Challenge",
        "bootcamp": "Tuesday Bootcamp Run",
    }
    EVENT_CONTAINER_CLASS = "css-175oi2r"
    EVENT_TITLE_CLASS = ".r-8akbws.r-krxsd3"

    def __init__(
        self,
        local_username: str,
        chrome_user_profile: str = "Default",
    ) -> None:
        print(
            f"Initializing HeyloAutomator with {local_username=} and {chrome_user_profile=}..."
        )
        self.login_url = f"{self.BASE_URL}/login"
        self.events_url = f"{self.BASE_URL}/events/{self.MIDNIGHT_RUNNERS_ID}"
        self.driver = self._setup_driver(
            user_data_dir=f"/Users/{local_username}/Library/Application Support/Google/Chrome/",
            user_profile=chrome_user_profile,
        )

    def _setup_driver(self, user_data_dir: str, user_profile: str) -> WebDriver:
        """Set up the Chrome WebDriver with user data directory and profile"""
        print("Setting up Chrome WebDriver...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"profile-directory={user_profile}")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )

    def login(self, initial_wait: int = 2) -> None:
        """Log into Heylo"""
        self.driver.get(self.login_url)
        time.sleep(initial_wait)
        if self.login_url not in self.driver.current_url:
            print("Already logged in!")
            return

        input("Please log in manually and press Enter when done...")
        while self.login_url in self.driver.current_url:
            time.sleep(1)

    def find_event(self, title: str) -> str | None:
        """Find the event card by its title and return its ID"""
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        upcoming_header = soup.find(
            "div",
            string=lambda x: x in ["Upcoming events", "Événements à venir"],
        )
        if not upcoming_header:
            print("Couldn't find upcoming events section")
            return None

        events_container = upcoming_header.find_parent(
            "div", class_=self.EVENT_CONTAINER_CLASS
        )
        if not events_container:
            return None

        event_cards = events_container.find_all_next(
            attrs={"data-testid": lambda x: x and x.startswith("event-card--")}
        )

        for card in event_cards:
            title_elem = card.select_one(self.EVENT_TITLE_CLASS)
            if title_elem and title in title_elem.text:
                print(f"Event found: {title_elem.text}")
                return card["data-testid"].split("--")[1]
        return None

    def register_for_event(self, event_url: str) -> None:
        """Register for the event by clicking the registration button"""
        print(f"Registering for event: {event_url}")
        while True:
            try:
                self.driver.get(event_url)
                self._perform_registration_clicks()
                print("Successfully registered for the event!")
                break
            except TimeoutException:
                print("Registration button not found or not clickable")
                print("Retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                raise

    def _perform_registration_clicks(self) -> None:
        """Click the registration buttons"""
        print("Performing registration clicks...")
        for en_key, fr_key in [
            ("Register", "S'inscrire"),
            ("Continue", "Continuer"),
            ("Skip", "Passer"),
        ]:
            button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"""//div[contains(text(), "{en_key}") or contains(text(), "{fr_key}")]""",
                    )
                )
            )
            button.click()
            print(f"Clicked '{en_key}' button")

    def register(self, event_type: str) -> None:
        """Register for the specified event type"""
        print(f"Registering for event type: {event_type}")
        while True:
            try:
                print("Checking for event publication...")
                time.sleep(1)
                print(".", end="", flush=True)
                
                self.driver.get(self.events_url)
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '[data-testid^="event-card--"]')
                    )
                )

                if event_id := self.find_event(self.EVENT_TITLES[event_type]):
                    print("Event found! Attempting to register...")
                    self.register_for_event(f"{self.events_url}/-{event_id}")
                    input("Registration complete! Press Enter or Ctrl+C to exit...")
                    return

            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Heylo event registration automation")
    parser.add_argument(
        "event_type",
        choices=list(HeyloAutomator.EVENT_TITLES.keys()),
        help="Type of event to register for",
    )

    args = parser.parse_args()

    automator = HeyloAutomator(local_username="daniel")
    automator.login()
    automator.register(args.event_type)


if __name__ == "__main__":
    main()
