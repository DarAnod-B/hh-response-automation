import os
import logging
from contextlib import contextmanager
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from sleep_random import sleep_random


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

    config = configparser.ConfigParser(interpolation=None)
    config.read(path_to_config, encoding="utf-8")
    return config


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
    finally:
        web_driver.close()
        web_driver.quit()
