import os
import logging

from files_opening import open_config_file, open_web_driver
from pages import (
    account_login,
    resume_update,
    selection_of_filtered_vacancies,
    submit_to_the_vacancy_on_the_all_pages,
)


def main():
    logging.basicConfig(
        filename=os.path.join("reports", "mylog.log"),
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    config = open_config_file()
    USERNAME = config["Account"]["username"]
    PASSWORD = config["Account"]["password"]
    LINK_TO_THE_FILTERED_LIST = config["Resume Options"][
        "link_to_the_filtered_list"
    ]
    TITLE_OF_RESUME = config["Resume Options"]["title_of_resume"]
    ADD_A_COVER_LETTER = config.getboolean(
        "Resume Options", "add_a_cover_letter")
    path_to_cover_letter = os.path.join(
        os.getcwd(), 'cover letter', f'{USERNAME.split("@")[0]}.txt')

    with open_web_driver() as web_driver:
        account_login(web_driver, USERNAME, PASSWORD)
        resume_update(web_driver)
        selection_of_filtered_vacancies(web_driver, LINK_TO_THE_FILTERED_LIST)
        submit_to_the_vacancy_on_the_all_pages(
            web_driver, TITLE_OF_RESUME, ADD_A_COVER_LETTER, path_to_cover_letter)


if __name__ == "__main__":
    main()
