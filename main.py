import time
import random
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from webdriver_manager.chrome import ChromeDriverManager
from contextlib import contextmanager
from enum import Enum
import configparser


class Link(Enum):
    LOGIN_PAGE = "https://hh.ru/account/login"


class XPath(Enum):
    INPUT_LOGIN = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[1]/fieldset/input'
    INPUT_PASSWORD = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[2]/fieldset/input'
    BUTTON_EXPAND_LOGIN_BY_PASSWORD = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/div/form/div[4]/button[2]'
    BUTTON_LOGIN = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[4]/div/button[1]/span'

def open_config_file():
    config = configparser.ConfigParser()
    path_to_config  = os.path.join(os.getcwd(), 'config.ini')
    assert os.path.exists(path_to_config), "Не найден путь до конфига."
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
    web_driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()))

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


def login(web_driver: webdriver.Chrome):
    safety_get(web_driver, Link.LOGIN_PAGE.value)

    sleep_random()
    web_driver.find_element_by_xpath(
        XPath.BUTTON_EXPAND_LOGIN_BY_PASSWORD.value).click()
    sleep_random()
    web_driver.find_element_by_xpath(XPath.INPUT_LOGIN.value).send_keys(email)
    sleep_random()
    web_driver.find_element_by_xpath(
        XPath.INPUT_PASSWORD.value).send_keys(password)
    sleep_random()
    web_driver.find_element_by_xpath(XPath.BUTTON_LOGIN.value).click()


def main():
    config = open_config_file()
    STORAGE_FOLDER = config["parameter"]["STORAGE_FOLDER"]

    with open_web_driver() as web_driver:
        login(web_driver)


if __name__ == "__main__":
    main()
