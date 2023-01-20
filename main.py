import time
import random
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
    RESPONSE_LIMIT_WARNING = r"//div[text()='В течение 24 часов можно совершить не более 200 откликов. Вы исчерпали лимит откликов, попробуйте отправить отклик позднее.']"


class Tag_Value(Enum):
    SUITABLE_VACANCIES = r'resume-recommendations__button_updateResume'


def sleep_random(min_sleep=2, max_sleep=3):
    time.sleep(round(random.uniform(min_sleep, max_sleep), 2))


def open_config_file() -> configparser.ConfigParser:
    '''Поиск и открытие файла конфигурации по умолчанию поиск в той же директории, что и скрипт main.'''
    path_to_config = os.path.join(os.getcwd(), 'config.ini')
    assert os.path.exists(path_to_config), "Не найден путь до конфига."

    config = configparser.ConfigParser()
    config.read(path_to_config, encoding="utf-8")
    return config


def check_exists_by_xpath(web_driver: webdriver.Chrome, xpath: str) -> bool:
    '''Проверка существует ли элемент по его Xpath.'''
    return len(web_driver.find_elements(By.XPATH, xpath)) > 0


def safety_get(driver: webdriver.Chrome, url: str):
    '''Безопасное открытие при котором если страница не открылась в течении n секунд, то она перезагружается.'''
    driver.set_page_load_timeout(120)

    try:
        driver.get(url)
    except TimeoutException:
        print('Перезагрузка страницы.')
        driver.refresh()


@contextmanager
def open_web_driver() -> webdriver.Chrome:
    '''
    Открытие веб драйвера и назнвачение ему опций
    (О них можно почитать по ссылке: https://peter.sh/experiments/chromium-command-line-switches/).
    '''

    options = Options()

    options.add_argument('--log-level=3')
    options.add_argument("--start-maximized")
    options.add_argument("--enable-automation")
    # options.add_argument("--headless");
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-infobars")

    web_driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    web_driver.set_page_load_timeout(120)
    web_driver.implicitly_wait(100)
    web_driver.set_script_timeout(100)

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
    '''Вход на сайт по логину и паролю.'''
    safety_get(web_driver, Link.LOGIN_PAGE.value)

    # sleep_random()
    web_driver.find_element(
        By.XPATH, XPath.BUTTON_EXPAND_LOGIN_BY_PASSWORD.value
    ).click()
    # sleep_random()
    web_driver.find_element(By.XPATH, XPath.INPUT_LOGIN.value).send_keys(LOGIN)
    # sleep_random()
    web_driver.find_element(By.XPATH, XPath.INPUT_PASSWORD.value).send_keys(
        PASSWORD
    )
    # sleep_random()
    web_driver.find_element(By.XPATH, XPath.BUTTON_LOGIN.value).click()

    sleep_random()


def resume_selection(web_driver: webdriver.Chrome, TITLE_OF_RESUME):
    '''Переход во вкладку "мои резюме", выбор одного из резюме пользователя и переход во вкладку "n подходящих вакансиий".'''
    link_my_resumes = web_driver.find_element(
        By.XPATH, XPath.LINK_TO_BUTTON_MY_RESUMES.value
    ).get_attribute('href')
    safety_get(web_driver, link_my_resumes)
    sleep_random()
    link_suitable_vacancies = (
        web_driver.find_element(
            By.CSS_SELECTOR, f"div[data-qa-title='{TITLE_OF_RESUME}']"
        )
        .find_element(
            By.CSS_SELECTOR,
            f"a[data-qa='{Tag_Value.SUITABLE_VACANCIES.value}']",
        )
        .get_attribute('href')
    )
    safety_get(web_driver, link_suitable_vacancies)
    sleep_random()


def submit_to_the_vacancy_on_the_all_pages(web_driver: webdriver.Chrome):
    '''
    Отклик на все вакансии на странице (при этом происходит переход на вакансию, а после
    переход назад, к списку вакансий) и перебор всех страниц пока сущестует кнопка "Далее".
    '''

     # Цикл остановится если большо нет кнопки "дальее" или появился баннер о превышении числа откликов за 24 часа. 
    while check_exists_by_xpath(
        web_driver, XPath.LINKS_TO_BUTTON_NEXT.value
    ) and not (
        check_exists_by_xpath(web_driver, XPath.RESPONSE_LIMIT_WARNING.value)
    ):

        list_of_elements_button_submit = web_driver.find_elements(
            By.XPATH, XPath.LINKS_TO_BUTTON_SUBMIT.value
        )

        list_of_links_to_button_submit = [
            link.get_attribute('href')
            for link in list_of_elements_button_submit
        ]

        for link_to_button_submit in list_of_links_to_button_submit:
            sleep_random()

            try:
                web_driver.get(link_to_button_submit)
            except Exception as error:
                print(error)

            sleep_random()
            web_driver.back()

        link_to_button_next = web_driver.find_element(
            By.XPATH, XPath.LINKS_TO_BUTTON_NEXT.value
        ).get_attribute('href')

        safety_get(web_driver, link_to_button_next)
        sleep_random()


def main():
    config = open_config_file()
    LOGIN = config["Account"]["login"]
    PASSWORD = config["Account"]["password"]
    TITLE_OF_RESUME = config["Resume Options"]["title_of_resume"]

    SUBMIT_LIMIT = 200
    
    with open_web_driver() as web_driver:
        login(web_driver, LOGIN, PASSWORD)
        resume_selection(web_driver, TITLE_OF_RESUME)
        submit_to_the_vacancy_on_the_all_pages(web_driver, SUBMIT_LIMIT)


if __name__ == "__main__":
    main()
