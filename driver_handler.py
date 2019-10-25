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


logger = logging.getLogger('apscheduler')
logger.setLevel(level=logging.CRITICAL)
logger.disabled = True
output_lock = Lock()
TRADE_URL = 'https://www.pathofexile.com/trade/exchange/Blight/'


def tonumber(i):
    try:
        return int(i)
    except:
        return float(i)


def ding():
    # Utilize a thread to avoid blocking while playing sound
    def play_ding():
        playsound('resources/ding.mp3')
    thread = Thread(target=play_ding)
    thread.start()


class TabHandler():
    def __init__(self, item, identifier, config):
        self.item = item
        self.config = config
        self.sold = []
        self.cache = []

        self.min_profit = config.get('min_profit')
        self.min_stock = config.get('min_stock')
        self.resale = config.get('resale')

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

        colortext.output('Loading Links', 'logging')

        self.load_links([
            item_filter['identifier']
            for item_filter in item_filters
        ])

        self.task_scheduler = BackgroundScheduler()
        self.task_scheduler.add_job(
            self.filter_links,
            'interval',
            id='scanner',
            seconds=5,
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
            self.driver.get(TRADE_URL + identifier)
            self.wait_and_scroll()

    def wait_and_scroll(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, 'per-have')
            )
        )
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(0.5)  # safety

    def filter_links(self):
        for identifier, tab_handler in self.tab_handlers.items():
            # Swap window handle to match the current tab handler
            self.driver.switch_to.window(
                self.driver.window_handles[tab_handler.handler_id]
            )

            # Refresh if we're past initialization
            if not self.init:
                self.driver.get(self.driver.current_url)
                self.wait_and_scroll()

            scanned, tmp_cache = [], []
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            for div in soup.find_all('div', class_='row exchange'):
                details = nodesearch.find_element(
                    div,
                    [
                        {'tag': 'div', 'class': 'middle details'}
                    ]
                )
                info = nodesearch.find_element(
                    div,
                    [
                        {'tag': 'div', 'class': 'right'},
                        {'tag': 'div', 'class': 'details'},
                        {'tag': 'div', 'class': 'info'}
                    ]
                )
                block = {
                    'price': 0,
                    'currency': '',
                    'stock': 0,
                    'ign': '',
                    'item_name': '',
                    'margin': 0
                }
                if details:
                    # Parse item name + price
                    price_block = nodesearch.find_element(
                        details,
                        [
                            {'tag': 'span', 'class': 'price-right'},
                            {'tag': 'div', 'class': 'price-block'}
                        ]
                    )
                    block['price'] = tonumber(price_block.contents[0].text)
                    currency_text = nodesearch.find_element(
                        price_block,
                        [
                            {'tag': 'span', 'class': 'currency-text'}
                        ]
                    )
                    block['currency'] = currency_text.text
                if info:
                    # Parse currency type + stock count
                    stock_block = nodesearch.find_element(
                        info,
                        [
                            {'tag': 'span', 'class': 'pull-left stock'}
                        ]
                    )
                    stock_type = nodesearch.find_element(
                        stock_block,
                        [
                            {'tag': 'span', 'class': 'currency-text'}
                        ]
                    )
                    block['item_name'] = stock_type.text
                    block['stock'] = int(stock_block.find('span').text)

                    # Parse IGN from contact info
                    contact_options = info.parent.find(
                        'div',
                        {'aria-label': 'Contact Options'}
                    ).contents[0]

                    block['ign'] = nodesearch.find_element(
                        contact_options,
                        [
                            {'tag': 'span', 'class': 'character-name'}
                        ]
                    ).text[5:]

                # Calculate profit margin
                block['margin'] = (
                    (tab_handler.config['resale'] - block['price']) *
                    block['stock']
                )

                min_stock = tab_handler.min_stock
                min_profit = tab_handler.min_profit

                # Filter out prices higher than required by config
                if (block['price'] > tab_handler.config['max_price'] or
                        min_stock and block['stock'] < min_stock or
                        min_profit and block['margin'] < min_profit):
                    continue

                cached = False
                # Update cache if profit margin changes
                for i, cached_block in enumerate(tab_handler.cache):
                    if cached_block['ign'] == block['ign']:
                        cached = True
                        if cached_block['margin'] == block['margin']:
                            continue

                        tab_handler.sold.append(
                            colortext.generate(
                                '{} Has updated their price for {}'.format(
                                    block['ign'],
                                    tab_handler.item
                                ),
                                'listing-update'
                            )
                        )
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
                        tab_handler.sold.append(
                            colortext.generate(
                                '{} Has sold their {}.'.format(
                                    cached_block['ign'],
                                    tab_handler.item
                                ),
                                'listing-remove'
                            )
                        )

            tab_handler.cache = new_cache or tab_handler.cache
            self.output(tab_handler, scanned)
        self.init = False

    def redisplay(self):
        for identifier, tab_handler in self.tab_handlers.items():
            self.output(tab_handler, tab_handler.cache, force_ding=False)

    def output(self, tab_handler, scanned, force_ding=True):
        global output_lock
        output_lock.acquire()
        scanned.sort(reverse=True, key=lambda v: v['margin'])
        whispers = []

        # Format whispers and determine longest whisper for ljust length
        for block in scanned:
            whisper = ('@{} Hi, I would like to buy your '
                       '{} {} for {} {} in Blight.').format(
                        block['ign'],
                        block['stock'],
                        block['item_name'],
                        block['price'] * block['stock'],
                        block['currency'],
                    )
            whispers.append((whisper, len(whisper), block))

        whispers.sort(key=len, reverse=True)
        longest_whisper = whispers and whispers[0][1] or 0

        # Output item filter separator
        if whispers or tab_handler.sold:
            colortext.output('-' * 150, 'logging')

        # Output item name & ding
        if whispers or tab_handler.sold:
            if (force_ding and
                    whispers and
                    SNIPER_CONFIG['general-config']['ding'] and
                    not self.init):
                ding()

            colortext.output(tab_handler.item.center(150), 'item-name')

            for m in tab_handler.sold:
                print(m)
            tab_handler.sold = []

        # Ouptut whispers
        for whisper, whisper_length, block in whispers:
            profit_str = 'PROFIT: ' + str(block['margin'])
            # Fix width of korean characters
            hangul_count = hangul.count_hangul(
                block['ign']
            )
            whisper =  '{} {}'.format(
                whisper.ljust(
                    145 - len(profit_str) - hangul_count
                ),
                profit_str
            )
            if blacklist.find(block['ign']):
                colortext.output(whisper, 'blocked-whisper')
            else:
                colortext.output(whisper, 'whisper')
        output_lock.release()

    def stop(self):
        self.driver.quit()
