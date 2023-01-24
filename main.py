import time
import random
import os
import logging
import pickle

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from contextlib import contextmanager
from enum import Enum
import configparser


class Link(Enum):
    LOGIN_PAGE = r"https://hh.ru/account/login"


class XPath(Enum):
    INPUT_LOGIN = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[1]/fieldset/input'
    INPUT_PASSWORD = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[2]/fieldset/input'

    BUTTON_EXPAND_LOGIN_BY_PASSWORD = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/div/form/div[4]/button[2]'
    BUTTON_LOGIN = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[4]/div/button[1]'

    LINK_TO_BUTTON_MY_RESUMES = (
        r'//*[@id="HH-React-Root"]/div/div[2]/div[1]/div/div/div/div[1]/a'
    )
    LINKS_TO_BUTTON_SUBMIT = r"//span[text()='Откликнуться']/ancestor::a"
    LINKS_TO_BUTTON_NEXT = r"//span[text()='дальше']/ancestor::a"
    LINKS_TO_BUTTON_SEARCH_FOR_SUITABLE_VACANCIES = r"//div[contains(@data-qa-title, '{}')]//a[contains(@data-qa, 'resume-recommendations__button_updateResume')]"

    RESPONSE_LIMIT_WARNING = r"//div[text()='В течение 24 часов можно совершить не более 200 откликов. Вы исчерпали лимит откликов, попробуйте отправить отклик позднее.']"
    WRONG_LOGIN_WARNING = r"//div[text()='Неправильные данные для входа. Пожалуйста, попробуйте снова.']"
    ROBOT_CHECK_WARNING = (
        r"//div[text()='Пожалуйста, подтвердите, что вы не робот']"
    )


class Tag_Value(Enum):
    SUITABLE_VACANCIES = r'resume-recommendations__button_updateResume'


class ErrorText(Enum):
    LOADING_ERROR = r'Page reload, response time passed.'
    LOGIN_FAILED = r'Incorrect username and password entered.'
    OVER_RESPONSE = (
        r'Within 24 hours, you can make no more than 200 responses.'
    )
    NO_SUITABLE_VACANCIES = r'There are no suitable vacancies for your resume.'
    INCORRECT_RESUME_TITLE = (
        r'Among your resumes, the one you specified was not found.'
    )


class InvalidUsernameOrPassword(Exception):
    pass


class ExcessResponsesAvailablePerDay(Exception):
    pass


class LackOfSuitableVacancies(Exception):
    pass


class IncorrectResumeTitle(Exception):
    pass


def sleep_random(min_sleep=2, max_sleep=3):
    time.sleep(round(random.uniform(min_sleep, max_sleep), 2))


def open_config_file() -> configparser.ConfigParser:
    '''Search and open the configuration file, by default search in the same directory as the main script.'''
    path_to_config = os.path.join(os.getcwd(), 'config.ini')

    try:
        assert os.path.exists(path_to_config)
    except AssertionError as error:
        logging.critical(
            r'In the script directory will not find the config (config.ini).'
        )
        raise FileNotFoundError(error)

    config = configparser.ConfigParser()
    config.read(path_to_config, encoding="utf-8")
    return config


def check_exists_by_xpath(web_driver: webdriver.Chrome, xpath: str) -> bool:
    '''Check if an element exists by its Xpath.'''
    return len(web_driver.find_elements(By.XPATH, xpath)) > 0


def safety_get(driver: webdriver.Chrome, url: str):
    '''Safe opening where if the page is not opened within n seconds, it is reloaded.'''
    driver.set_page_load_timeout(15)

    while True:
        try:
            driver.get(url)
            break
        except TimeoutException:
            logging.warning(ErrorText.LOADING_ERROR.value)
            driver.refresh()
            sleep_random()


@contextmanager
def open_web_driver() -> webdriver.Chrome:
    '''
    Opening the web driver and assigning options to it
    (You can read about them at the link: https://peter.sh/experiments/chromium-command-line-switches/).
    '''

    options = Options()

    options.add_argument('--log-level=3')

    # options.add_argument("--headless")
    options.add_argument('--disable-gpu')

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    )
    options.add_argument("--start-maximized")
    options.add_argument("--enable-automation")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-3d-apis")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--mute-audio')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--no-zygote')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-breakpad')

    web_driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    try:
        yield web_driver
        web_driver.close()
        sleep_random()
        web_driver.quit()

    finally:
        web_driver.close()
        sleep_random()
        web_driver.quit()


def account_login(web_driver: webdriver.Chrome, LOGIN: str, PASSWORD: str):
    '''
    Sign in to your account in one of the following ways:
     1. If cookies are downloaded then by them.
     2. If cookies are not downloaded, then by login and password, then cookies are downloaded.

    When logging in, it is important that the account name and password are entered correctly,
    since even with saved cookies they will not be found, because part of the path to them is the account name.
    '''
    safety_get(web_driver, Link.LOGIN_PAGE.value)
    sleep_random()

    path_to_cookie = os.path.join(
        os.getcwd(), 'cookies', f'{LOGIN}_cookie.pkl'
    )

    def login_and_password_login():
        '''Login to the site with login and password.'''

        web_driver.find_element(
            By.XPATH, XPath.BUTTON_EXPAND_LOGIN_BY_PASSWORD.value
        ).click()
        sleep_random(0.1, 0.3)

        web_driver.find_element(By.XPATH, XPath.INPUT_LOGIN.value).send_keys(
            LOGIN
        )
        sleep_random(0.1, 0.3)

        web_driver.find_element(
            By.XPATH, XPath.INPUT_PASSWORD.value
        ).send_keys(PASSWORD)
        sleep_random(0.1, 0.3)

        web_driver.find_element(By.XPATH, XPath.BUTTON_LOGIN.value).click()
        sleep_random(3, 4)

        # Check for incorrectly entered login and password.
        try:
            assert not check_exists_by_xpath(
                web_driver, XPath.WRONG_LOGIN_WARNING.value
            ) and not check_exists_by_xpath(
                web_driver, XPath.ROBOT_CHECK_WARNING.value
            ), ErrorText.LOGIN_FAILED.value
        except AssertionError as error:
            logging.critical(ErrorText.LOGIN_FAILED.value)
            raise InvalidUsernameOrPassword(error)

        # Cookie save.
        sleep_random(0.1, 0.3)
        web_driver.find_element(
            By.XPATH, XPath.LINK_TO_BUTTON_MY_RESUMES.value
        ).click()
        sleep_random()
        pickle.dump(web_driver.get_cookies(), open(path_to_cookie, "wb"))
        sleep_random()

    def cookie_login():
        '''Logging in with a cookie.'''
        for cookie in pickle.load(open(path_to_cookie, "rb")):
            web_driver.add_cookie(cookie)

    try:
        cookie_login()
        web_driver.refresh()
    except FileNotFoundError:
        login_and_password_login()

    sleep_random()


def resume_selection(web_driver: webdriver.Chrome, TITLE_OF_RESUME):
    '''Select one of the user's resumes and go to the "n matching jobs" tab.'''
    link_to_button_my_resume = web_driver.find_element(
        By.XPATH, XPath.LINK_TO_BUTTON_MY_RESUMES.value
    ).get_attribute('href')
    safety_get(web_driver, link_to_button_my_resume)

    sleep_random()

    try:
        assert check_exists_by_xpath(
            web_driver,
            XPath.LINKS_TO_BUTTON_SEARCH_FOR_SUITABLE_VACANCIES.value.format(
                TITLE_OF_RESUME
            ),
        ), ErrorText.INCORRECT_RESUME_TITLE.value
    except AssertionError as error:
        logging.critical(ErrorText.INCORRECT_RESUME_TITLE.value)
        raise IncorrectResumeTitle(error)

    link_suitable_vacancies = web_driver.find_element(
        By.XPATH,
        XPath.LINKS_TO_BUTTON_SEARCH_FOR_SUITABLE_VACANCIES.value.format(
            TITLE_OF_RESUME
        ),
    ).get_attribute('href')

    safety_get(web_driver, link_suitable_vacancies)
    sleep_random()


def submit_to_the_vacancy_on_the_all_pages(
    web_driver: webdriver.Chrome,
):
    '''Respond to all "suitable jobs" for a certain one (maximum 200 per day).'''

    def submit_to_the_vacancy_on_the_page():
        '''Response to all vacancies on the page.'''
        list_of_elements_button_submit = web_driver.find_elements(
            By.XPATH, XPath.LINKS_TO_BUTTON_SUBMIT.value
        )

        list_of_links_to_button_submit = [
            link.get_attribute('href')
            for link in list_of_elements_button_submit
        ]

        try:
            assert (
                len(list_of_elements_button_submit) != 0
            ), ErrorText.NO_SUITABLE_VACANCIES.value
        except AssertionError as error:
            logging.critical(ErrorText.NO_SUITABLE_VACANCIES.value)
            raise LackOfSuitableVacancies(error)

        for link_to_button_submit in list_of_links_to_button_submit:
            sleep_random()

            try:
                safety_get(web_driver, link_to_button_submit)
            except Exception as error:
                logging.warning(
                    f"When responding to a vacancy, the following error: {error}"
                )

            sleep_random()
            try:
                assert not check_exists_by_xpath(
                    web_driver, XPath.RESPONSE_LIMIT_WARNING.value
                ), ErrorText.OVER_RESPONSE.value
            except AssertionError as error:
                logging.critical(ErrorText.OVER_RESPONSE.value)
                raise ExcessResponsesAvailablePerDay(error)

    # The cycle will stop if there is no more "next" button or a banner about exceeding the number of responses in 24 hours.
    while check_exists_by_xpath(web_driver, XPath.LINKS_TO_BUTTON_NEXT.value):
        submit_to_the_vacancy_on_the_page()

        link_to_button_next = web_driver.find_element(
            By.XPATH, XPath.LINKS_TO_BUTTON_NEXT.value
        ).get_attribute('href')

        try:
            safety_get(web_driver, link_to_button_next)
        except Exception as error:
            logging.warning(
                f"When going to the next page, the following error occurs: {error}"
            )

        sleep_random()


def main():
    logging.basicConfig(
        filename="mylog.log",
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    config = open_config_file()
    LOGIN = config["Account"]["login"]
    PASSWORD = config["Account"]["password"]
    TITLE_OF_RESUME = config["Resume Options"]["title_of_resume"]

    with open_web_driver() as web_driver:
        account_login(web_driver, LOGIN, PASSWORD)
        resume_selection(web_driver, TITLE_OF_RESUME)
        submit_to_the_vacancy_on_the_all_pages(web_driver)


if __name__ == "__main__":
    main()
