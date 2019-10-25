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
import logging

logger = logging.getLogger('apscheduler')
logger.setLevel(level=logging.CRITICAL)
logger.disabled = True

output_lock = Lock()

def tonumber(i):
    try:
        return int(i)
    except:
        return float(i)

links = 0
counter = 0
TRADE_URL = 'https://www.pathofexile.com/trade/exchange/Blight/'

class TabHandler():
    def __init__(self, item, identifier, config, interval=15):
        self.item = item
        self.config = config
        self.sold = []
        self.cache = []
    
    def set_handler_id(self, handler_id):
        self.handler_id = handler_id


class DriverHandler():
    def __init__(self, item_filters):
        self.tab_handlers = {}
        self.handles = {}

        self.init = True

        options = webdriver.ChromeOptions()
        options.add_argument('--unlimited-storage')
        options.add_argument('--disable-gpu')
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

        print(colortext.red('Loading links'))

        self.load_links([
            item_filter['identifier']
            for item_filter in item_filters
        ])

        self.task_scheduler = BackgroundScheduler()
        self.task_scheduler.add_job(self.filter_links, 'interval', id='scanner', seconds=15, next_run_time=datetime.datetime.now())
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
            self.driver.get(TRADE_URL + identifier)

    def filter_links(self):
        for identifier, tab_handler in self.tab_handlers.items():
            self.driver.switch_to.window(
                self.driver.window_handles[tab_handler.handler_id]
            )


            if not self.init:
                self.driver.get(self.driver.current_url)
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'per-have')))
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)  # safety


            scanned, tmp_cache = [], []

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            for div in soup.find_all('div', class_='row exchange'):
                details = div.find('div', class_='middle details')
                info = div.find('div', class_='right').find('div', class_='details').find('div', class_='info')
                block = {
                    'price': 0,
                    'currency': '',
                    'stock': 0,
                    'ign': '',
                    'item_name': '',
                    'margin': 0
                }
                if details:
                    price_block = details.find('span', class_='price-right').find('div', class_='price-block')
                    block['price'] = tonumber(price_block.contents[0].text)
                    block['currency'] = price_block.find('span', class_='currency-text').text
                if info:
                    block['item_name'] = info.find('span', class_='pull-left stock').find('span', class_='currency-text').text
                    block['stock'] = int(info.find('span', class_='pull-left stock').find('span').text)
                    block['ign'] = info.parent.find('div', {'aria-label': 'Contact Options'}).contents[0].find('span', class_='character-name').text[5:]

                block['margin'] = (tab_handler.config['resale'] - block['price']) * block['stock']

                if (block['price'] > tab_handler.config['max_price'] or
                    tab_handler.config.get('min_stock') and block['stock'] < tab_handler.config['min_stock'] or
                    tab_handler.config.get('min_profit') and block['margin'] < tab_handler.config['min_profit']):
                    continue

                cached = False
                # Update cache if profit margin changes
                for i, cached_block in enumerate(tab_handler.cache):
                    if cached_block['ign'] == block['ign']:
                        cached = True
                        if cached_block['margin'] != block['margin']:
                            tab_handler.sold.append(Fore.CYAN + Style.BRIGHT + block['ign'] + ' Has updated their price for ' + tab_handler.item)
                            tab_handler.cache[i] = block
                            scanned.append(block)
                            break

                # Insert into the cache if they're not cached already
                if not cached:
                    tab_handler.cache.append(block)
                    scanned.append(block)

                tmp_cache.append(block)

            # Delete from cache if they were not scanned, aka item was sold
            new_cache = []
            if tmp_cache:
                for i, cached_block in enumerate(tab_handler.cache):
                    found = False
                    for block in tmp_cache:
                        if block['ign'] == cached_block['ign']:
                            new_cache.append(block)
                            found = True
                            break

                    if not found:
                        tab_handler.sold.append(Fore.YELLOW + Style.BRIGHT + '{} Has sold their {}.'.format(cached_block['ign'], tab_handler.item) + Style.RESET_ALL)

            tab_handler.cache = new_cache or tab_handler.cache

            self.output(tab_handler, scanned)
        self.init = False

    def redisplay(self):
        for identifier, tab_handler in self.tab_handlers.items():
            self.output(tab_handler, tab_handler.cache, force_ding=False)


    def output(self, tab_handler, scanned, force_ding=True):
        global output_lock
        output_lock.acquire()
        global links, counter
        scanned.sort(reverse=True, key=lambda v : v['margin'])
        whispers = []

        for block in scanned:
            whisper = '@{} Hi, I would like to buy your {} {} for {} {} in Blight.'.format(
                        block['ign'],
                        block['stock'],
                        block['item_name'],
                        block['price'] * block['stock'],
                        block['currency'],
                    )
            whispers.append((whisper, len(whisper), block))
        
        whispers.sort(key=len, reverse=True)
        longest_whisper = whispers and whispers[0][1] or 0

        counter -= 1
        if counter <= 0 and whispers or tab_handler.sold:
            counter = links
            print(Fore.RED + '-' * 150 + Style.RESET_ALL)

        if whispers or tab_handler.sold:
            if force_ding and whispers and SNIPER_CONFIG['general-config']['ding'] and not self.init:
                def ding():
                    playsound('resources/ding.mp3')
                thread = Thread(target=ding)
                thread.start()
            print(Fore.MAGENTA + tab_handler.item.center(150) + Style.RESET_ALL)
            for m in tab_handler.sold:
                print(m)
            tab_handler.sold = []

        for whisper, whisper_length, block in whispers:
            fore = blacklist.find(block['ign']) and Fore.RED or Fore.GREEN
            profit_str = 'PROFIT: ' + str(block['margin'])
            print(fore + whisper.ljust(145 - len(profit_str) - hangul.count_hangul(block['ign'])) + profit_str + Style.RESET_ALL)
        output_lock.release()

    def stop(self):
        self.driver.quit()