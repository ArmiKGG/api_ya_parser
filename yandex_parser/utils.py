from selenium import webdriver
import os
import pickle
from dotenv import load_dotenv

load_dotenv()


def prepare_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('--disable-gpu')
    options.add_argument(f'--host=http://{os.environ.get("STARTING_PAGE")}')
    driver = webdriver.Remote(
        command_executor=f'http://{os.environ.get("ROUTER")}:{os.environ.get("ROUTER_PORT")}/wd/hub', options=options)
    if os.path.exists('cookies/cookies.pkl'):
        cookies = pickle.load(open("cookies/cookies.pkl", "rb"))
        for cookie in cookies:
            print(f'cookie added {cookie}!')
            driver.add_cookie(cookie)
    return driver
