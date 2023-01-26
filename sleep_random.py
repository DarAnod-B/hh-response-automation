import time
import random


def sleep_random(min_sleep=2, max_sleep=3):
    time.sleep(round(random.uniform(min_sleep, max_sleep), 2))
