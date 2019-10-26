import requests
import blacklist
import json
import datetime
import time
<<<<<<< Updated upstream
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
=======
import websocket
from threading import Thread, Lock
from playsound import playsound
from bs4 import BeautifulSoup
>>>>>>> Stashed changes
from configloader import config as SNIPER_CONFIG
from libs import colortext
from libs import hangul
from libs import deepnodesearcher as nodesearch
import logging


DEBUGGING = True

<<<<<<< Updated upstream
logger = logging.getLogger('apscheduler')
if not DEBUGGING:
    logger.setLevel(level=logging.CRITICAL)
    logger.disabled = True
=======
>>>>>>> Stashed changes
output_lock = Lock()
TRADE_URL = 'http://poe.trade/search/'


<<<<<<< Updated upstream
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
=======
class MultiLiveSearch():
    def __init__(self, item_filters):
        self.url = "arerigihahabeb"
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            'ws://live.poe.trade/' + self.url,
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, err: self.on_error(ws, err),
            on_close=lambda ws: self.on_close(ws),
            on_open=lambda ws: print(ws)
        )
        self.new_id = -1
        self.ws.run_forever()

    def on_message(self, ws, msg):
        print(msg)
        payload = {'id': self.new_id}
        r = requests.post('http:/poe.trade/search/' + self.url + "/live", data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        json_data = r.json()
        self.new_id = json_data['newid']
        if 'data' in json_data:
            soup = BeautifulSoup(json_data['data'], 'html.parser')
            items = soup.find_all("tbody", { "class" : "item" })
            
            for item in items:
                print('@'+item.get('data-ign') + ' Hi, I would like to buy your ' + item.get('data-name') + ' listed for ' + item.get('data-buyout') + ' in ' + item.get('data-league')+' (stash tab \"' + item.get('data-tab')+ '\"; position: left ' + item.get('data-x')+ ', top ' +item.get('data-y') +')')

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        pass

def start():
    def init():
        MultiLiveSearch(SNIPER_CONFIG['live-searches'])
    thread = Thread(target=init)
    thread.start()
    print('Websocket initialized')
    input()

start()

#print(requests.post('http://poe.trade/search/arerigihahabeb/live', data={'id': 1166667635}, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json())
>>>>>>> Stashed changes
