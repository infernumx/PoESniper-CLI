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
from libs import colortext
from libs import hangul
from libs import deepnodesearcher as nodesearch
import logging


DEBUGGING = True

logger = logging.getLogger('apscheduler')
if not DEBUGGING:
    logger.setLevel(level=logging.CRITICAL)
    logger.disabled = True
output_lock = Lock()
TRADE_URL = 'http://poe.trade/search/'


class TabHandler():
    def __init__(self, item, identifier, config):
        self.item = item
        self.config = config
        self.sold = []
        self.cache = []

        self.resale = config.get('resale')

    def set_handler_id(self, handler_id):
        self.handler_id = handler_id


class LiveSearchHandler():
    def __init__(self, item_filters):
        self.tab_handlers = {}

        options = webdriver.ChromeOptions()
        options.add_argument('--unlimited-storage')
        options.add_argument('--disable-gpu')
        if not DEBUGGING:
            options.add_argument('--headless')
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(
            executable_path='./resources/chromedriver.exe',
            options=options,
            service_args=['--webdriver-loglevel=ERROR']
        )

        for item_filter in item_filters:
            key = item_filter['identifier']
            self.tab_handlers[key] = TabHandler(**item_filter)

        self.load_links([
            item_filter['identifier']
            for item_filter in item_filters
        ])

        self.task_scheduler = BackgroundScheduler()
        self.task_scheduler.add_job(
            self.filter_links,
            'interval',
            id='scanner',
            seconds=3,
            next_run_time=datetime.datetime.now()
        )
        self.task_scheduler.start()

    def load_links(self, identifiers):
        begin = True  # Utilize the first tab instead of opening a new one
        for identifier in identifiers:
            # Create new tab and set link
            if not begin:
                self.driver.execute_script('window.open("");')
                handle_id = len(self.driver.window_handles)-1
                self.tab_handlers[identifier].set_handler_id(handle_id)
                self.driver.switch_to.window(
                    self.driver.window_handles[handle_id]
                )
            else:
                self.tab_handlers[identifier].set_handler_id(0)
                begin = False
            self.driver.get(TRADE_URL + identifier + '/live')

    def filter_links(self):
        for identifier, tab_handler in self.tab_handlers.items():
            # Swap window handle to match the current tab handler
            self.driver.switch_to.window(
                self.driver.window_handles[tab_handler.handler_id]
            )

            scanned, tmp_cache = [], []

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            for results in soup.find_all('table', class_='search-results'):
                item_name = results.find(
                    'td',
                    class_='item-cell'
                ).h5.a.text.strip()
                print(item_name)
                proplist = results.find('ul', class_='proplist')
                print(proplist)


LiveSearchHandler(SNIPER_CONFIG['live-searches'])

input()