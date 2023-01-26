from enum import Enum


class Link(Enum):
    LOGIN_PAGE = r"https://hh.ru/account/login"


class XPath(Enum):
    INPUT_LOGIN = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[1]/fieldset/input'
    INPUT_PASSWORD = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[2]/fieldset/input'

    BUTTON_EXPAND_LOGIN_BY_PASSWORD = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/div/form/div[4]/button[2]'
    BUTTON_LOGIN = r'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div[2]/form/div[4]/div/button[1]'
    BUTTON_SUBMIT = r"//span[text()='Откликнуться']/ancestor::button"

    LINK_TO_BUTTON_MY_RESUMES = r'//*[@id="HH-React-Root"]/div/div[2]/div[1]/div/div/div/div[1]/a'
    
    LINKS_TO_BUTTON_SUBMIT = r"//span[text()='Откликнуться']/ancestor::a"
    LINKS_TO_BUTTON_NEXT = r"//span[text()='дальше']/ancestor::a"
    LINKS_TO_BUTTON_SEARCH_FOR_SUITABLE_VACANCIES = r"//div[contains(@data-qa-title, '{}')]//a[contains(@data-qa, 'resume-recommendations__button_updateResume')]"

    RESPONSE_LIMIT_WARNING = r"//div[text()='В течение 24 часов можно совершить не более 200 откликов. Вы исчерпали лимит откликов, попробуйте отправить отклик позднее.']"
    WRONG_LOGIN_WARNING = r"//div[text()='Неправильные данные для входа. Пожалуйста, попробуйте снова.']"
    ROBOT_CHECK_WARNING = r"//div[text()='Пожалуйста, подтвердите, что вы не робот']"
    ERROR_404_WARNING = r"//div[@class = 'error']//h1[text()  = 'Ошибка 404']"

    RESUME_FOR_RESPONSE_WINDOW = r"//div[text()='Резюме для отклика']"
    SELECTING_A_RESUME_TO_RESPONSE = r"//span[text()='{}']/preceding-sibling::input"


class ErrorText(Enum):
    LOADING_ERROR = r'Page reload, response time passed.'
    INVALID_USERNAME_OR_PASSWORD = r'Incorrect username and password entered.'
    EXCESS_RESPONSES_AVAILABLE_PER_DAY = (
        r'Within 24 hours, you can make no more than 200 responses.'
    )
    NO_SUITABLE_VACANCIES = r'There are no suitable vacancies for your resume.'
    INCORRECT_RESUME_TITLE = (
        r'Among your resumes, the one you specified was not found.'
    )
    PAGE_NOT_FOUND = r'Page not found (error 404) check the link with filters (LINK_TO_THE_FILTERED_LIST) and the username you entered.'
    

