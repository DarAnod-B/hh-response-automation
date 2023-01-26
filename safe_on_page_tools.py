import logging

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from enumeration_collection import ErrorText
from sleep_random import sleep_random


def check_exists_by_xpath(web_driver: webdriver.Chrome, xpath: str) -> bool:
    '''Check if an element exists by its Xpath.'''
    return len(web_driver.find_elements(By.XPATH, xpath)) > 0


def safety_get(driver: webdriver.Chrome, url: str):
    '''Safe opening where if the page is not opened within n seconds, it is reloaded.'''
    driver.set_page_load_timeout(120)

    while True:
        try:
            driver.get(url)
            break
        except TimeoutException:
            logging.warning(ErrorText.LOADING_ERROR.value)
            driver.refresh()
            sleep_random()
