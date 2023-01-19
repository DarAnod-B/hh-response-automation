import time
import random
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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


class Tag_Value(Enum):
    SUITABLE_VACANCIES = r'resume-recommendations__button_updateResume'


def open_config_file() -> configparser.ConfigParser:
    path_to_config = os.path.join(os.getcwd(), 'config.ini')
    assert os.path.exists(path_to_config), "Не найден путь до конфига."

    config = configparser.ConfigParser()
    config.read(path_to_config, encoding="utf-8")
    return config


def safety_get(driver: webdriver.Chrome, url: str):
    driver.set_page_load_timeout(7)
    try:
        driver.get(url)

    except TimeoutException:
        print('page refresh')
        driver.refresh()


def sleep_random():
    time.sleep(round(random.uniform(1, 2), 2))


@contextmanager
def open_web_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()

    options.add_argument('log-level=3')
    web_driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), chrome_options=options
    )

    try:
        yield web_driver
        web_driver.close()
        sleep_random()
        web_driver.quit()

    except Exception as error:
        web_driver.close()
        sleep_random()
        web_driver.quit()
        raise Exception(error)


def login(web_driver: webdriver.Chrome, LOGIN: str, PASSWORD: str):
    safety_get(web_driver, Link.LOGIN_PAGE.value)

    sleep_random()
    web_driver.find_element(
        By.XPATH, XPath.BUTTON_EXPAND_LOGIN_BY_PASSWORD.value
    ).click()
    sleep_random()
    web_driver.find_element(By.XPATH, XPath.INPUT_LOGIN.value).send_keys(LOGIN)
    sleep_random()
    web_driver.find_element(By.XPATH, XPath.INPUT_PASSWORD.value).send_keys(
        PASSWORD
    )
    sleep_random()
    web_driver.find_element(By.XPATH, XPath.BUTTON_LOGIN.value).click()
    sleep_random()


def resume_selection(web_driver: webdriver.Chrome):
    link_my_resumes = web_driver.find_element(
        By.XPATH, XPath.LINK_TO_BUTTON_MY_RESUMES.value
    ).get_attribute('href')
    safety_get(web_driver, link_my_resumes)
    sleep_random()


def go_to_the_list_of_vacancies(web_driver: webdriver.Chrome, TITLE_OF_RESUME):
    link_suitable_vacancies = (
        web_driver.find_element(
            By.CSS_SELECTOR, f"div[data-qa-title='{TITLE_OF_RESUME}']")
        .find_element(By.CSS_SELECTOR, f"a[data-qa='{Tag_Value.SUITABLE_VACANCIES.value}']")
        .get_attribute('href')
    )
    safety_get(web_driver, link_suitable_vacancies)
    sleep_random()


def apply_for_job(web_driver: webdriver.Chrome):
    time.sleep(2)

    list_of_links_to_button_submit = web_driver.find_elements(
        By.XPATH, XPath.LINKS_TO_BUTTON_SUBMIT.value)

    list_of_links_to_button_submit = [link.get_attribute('href') for link in list_of_links_to_button_submit]
 
    for link_to_button_submit in list_of_links_to_button_submit:

        web_driver.get(link_to_button_submit)

        sleep_random()
        web_driver.back()
        sleep_random()


def main():
    config = open_config_file()
    LOGIN = config["Account"]["login"]
    PASSWORD = config["Account"]["password"]

    TITLE_OF_RESUME = config["Resume Options"]["title_of_resume"]

    with open_web_driver() as web_driver:
        login(web_driver, LOGIN, PASSWORD)
        resume_selection(web_driver)
        go_to_the_list_of_vacancies(web_driver, TITLE_OF_RESUME)
        apply_for_job(web_driver)


if __name__ == "__main__":
    main()
