import requests
import blacklist
import json
import datetime
import time
from threading import Thread, Lock
from playsound import playsound
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from colorama import Fore, Back, Style
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from configloader import config as SNIPER_CONFIG

TRADE_URL = 'https://www.pathofexile.com/trade/exchange/Blight/'


class TabHandler():
    def __init__(self, item, identifier, config):
        self.item = item
        self.config = config
        self.sold = []
        self.cache = []


class DriverHandler():
    def __init__(self, item_filters):
        self.handles = {}

        options = webdriver.ChromeOptions()
        options.add_argument('--unlimited-storage')
        options.add_argument('--disable-gpu')
        #options.add_argument('--headless')
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(
            executable_path='./resources/chromedriver.exe',
            options=options,
            service_args=['--webdriver-loglevel=ERROR']
        )

        self.load_links([
            item_filter['identifier']
            for item_filter in item_filters
        ])

    def load_links(self, identifiers):
        begin = True  # utilize the first tab instead of opening a new one
        for identifier in identifiers:
            if not begin:
                self.driver.execute_script('window.open("");')
                handle_id = len(self.driver.window_handles)-1
                self.handles[identifier] = handle_id
                self.driver.switch_to.window(
                    self.driver.window_handles[handle_id]
                )
            else:
                self.handles[identifier] = 0
                begin = False
            self.driver.get(TRADE_URL + identifier)

    def filter_links(self):
        pass

DriverHandler(SNIPER_CONFIG['item-filters'])

input()
