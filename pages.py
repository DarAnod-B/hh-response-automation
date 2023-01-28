import os
import logging
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By

from enumeration_collection import Link, XPath, ErrorText
from user_exceptions import (
    InvalidUsernameOrPassword,
    ExcessResponsesAvailablePerDay,
    NoSuitableVacancies,
    PageNotFound,
)
from sleep_random import sleep_random
from safe_on_page_tools import check_exists_by_xpath, safety_get


def account_login(web_driver: webdriver.Chrome, USERNAME: str, PASSWORD: str):
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
        os.getcwd(), 'cookies', f'{USERNAME}_cookie.pkl'
    )
    def resume_update():
        update_resume_buttons = web_driver.find_elements(By.XPATH, XPath.UPDATE_RESUME_BUTTONS.value)
        for button in update_resume_buttons:
            button.click()
            sleep_random()
     
    def login_and_password_login():
        '''Login to the site with login and password.'''

        web_driver.find_element(
            By.XPATH, XPath.BUTTON_EXPAND_LOGIN_BY_PASSWORD.value
        ).click()
        sleep_random(0.1, 0.3)

        web_driver.find_element(By.XPATH, XPath.INPUT_LOGIN.value).send_keys(
            USERNAME
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
            ), ErrorText.INVALID_USERNAME_OR_PASSWORD.value
        except AssertionError as error:
            logging.critical(ErrorText.INVALID_USERNAME_OR_PASSWORD.value)
            raise InvalidUsernameOrPassword(error)

        # Cookie save.
        sleep_random(0.1, 0.3)
        web_driver.find_element(
            By.XPATH, XPath.LINK_TO_BUTTON_MY_RESUMES.value
        ).click()
        sleep_random()
        resume_update()
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




def selection_of_filtered_vacancies(
    web_driver: webdriver.Chrome, LINK_TO_THE_FILTERED_LIST
):
    '''
    The selection of vacancies filtered by the link, the link is received
    by the user himself in hh after he has entered all the filtering parameters.
    '''

    safety_get(web_driver, LINK_TO_THE_FILTERED_LIST)

    sleep_random()

    # Checking the availability of the selected vacancy
    try:
        assert not check_exists_by_xpath(
            web_driver,
            XPath.ERROR_404_WARNING.value,
        ), ErrorText.PAGE_NOT_FOUND.value
    except AssertionError as error:
        logging.critical(ErrorText.PAGE_NOT_FOUND.value)
        raise PageNotFound(error)


def submit_to_the_vacancy_on_the_all_pages(
    web_driver: webdriver.Chrome, TITLE_OF_RESUME
):
    '''Respond to all "suitable jobs" for a certain one (maximum 200 per day).'''

    def choosing_a_resume_for_a_response():
        '''
        If the user has several resumes, then when responding to a vacancy, a selection
        window will appear, this function will mark what the user has chosen.
        '''
        
        element_button_selecting = web_driver.find_element(
            By.XPATH,
            XPath.SELECTING_A_RESUME_TO_RESPONSE.value.format(
                TITLE_OF_RESUME
            )
        )
        
        # This command indirectly moves the button to the correct position, in other words, a successful crutch.
        web_driver.execute_script("arguments[0].setAttribute('class','')", element_button_selecting)
        element_button_selecting.click()

        sleep_random()

        web_driver.find_element(
            By.XPATH,
            XPath.BUTTON_SUBMIT.value
        ).click()



    def submit_to_the_vacancy_on_the_page():
        '''Response to all vacancies on the page.'''
        list_of_elements_button_submit = web_driver.find_elements(
            By.XPATH, XPath.LINKS_TO_BUTTON_SUBMIT.value
        )

        list_of_links_to_button_submit = [
            link.get_attribute('href')
            for link in list_of_elements_button_submit
        ]

        # Checking availability on the vacancies page.
        try:
            assert (
                len(list_of_elements_button_submit) != 0
            ), ErrorText.NO_SUITABLE_VACANCIES.value
        except AssertionError as error:
            logging.critical(ErrorText.NO_SUITABLE_VACANCIES.value)
            raise NoSuitableVacancies(error)

        for link_to_button_submit in list_of_links_to_button_submit:
            sleep_random()

            try:
                safety_get(web_driver, link_to_button_submit)
            except Exception as error:
                logging.warning(
                    f"When responding to a vacancy, the following error: {error}"
                )

            sleep_random()

            # A selection of resume to respond to a vacancy.
            if check_exists_by_xpath(
                web_driver, XPath.RESUME_FOR_RESPONSE_WINDOW.value
            ):
                choosing_a_resume_for_a_response()

            sleep_random()
            # Checking for a banner about exceeding the number of responses in 24 hours
            try:
                assert not check_exists_by_xpath(
                    web_driver, XPath.RESPONSE_LIMIT_WARNING.value
                ), ErrorText.EXCESS_RESPONSES_AVAILABLE_PER_DAY.value
            except AssertionError as error:
                logging.critical(
                    ErrorText.EXCESS_RESPONSES_AVAILABLE_PER_DAY.value
                )
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
