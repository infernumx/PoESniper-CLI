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

output_lock = Lock()

def tonumber(i):
	try:
		return int(i)
	except:
		return float(i)

hangul_ranges = (
    [0xAC00, 0xD7A4],  # Hangul Syllables (AC00–D7A3)
    [0x1100, 0x1200],  # Hangul Jamo (1100–11FF)
    [0x3130, 0x3190],  # Hangul Compatibility Jamo (3130-318F)
    [0xA960, 0xA980],  # Hangul Jamo Extended-A (A960-A97F)
    [0xD7B0, 0xD800],  # Hangul Jamo Extended-B (D7B0-D7FF)
)

def is_hangul(ch):
	val = ord(ch)
	for r in hangul_ranges:
		if val >= r[0] and val <= r[1]:
			return True
	return False

def count_hangul(string):
	count = 0
	for ch in string:
		if is_hangul(ch):
			count += 1
	return count

links = 0
counter = 0

class LinkWatcher():
	def __init__(self, item, identifier, config, interval=15):
		self.init = True
		self.link = 'https://www.pathofexile.com/trade/exchange/Blight/' + identifier
		self.item = item
		self.config = config
		self.interval = interval
		self.driver = None
		self.sold = []
		self.cache = []

		self.start()

	def start(self):
		self.task_scheduler = BackgroundScheduler()
		self.task_scheduler.add_job(self.scan, 'interval', id='scanner', seconds=self.interval, next_run_time=datetime.datetime.now())
		self.task_scheduler.start()

	def stop(self):
		self.driver.quit()

	def scan(self):
		try:
			if self.driver is None:
				options = webdriver.ChromeOptions()
				options.add_argument('--unlimited-storage')
				options.add_argument('--disable-gpu') 
				options.add_argument('--headless') 
				options.add_argument('--log-level=3')
				self.driver = webdriver.Chrome(executable_path='./resources/chromedriver.exe', options=options, service_args=['--webdriver-loglevel=ERROR'])
			else:
				self.driver.execute_script("location.reload(true);")
			self.driver.delete_all_cookies()
			self.driver.get(self.link)
			WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'per-have')))
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(0.5) # safety
			soup = BeautifulSoup(self.driver.page_source, 'html.parser')
		except Exception as e:
			print('Exception occurred, this is normal if you sent a keyboard interrupt or SIGINT to the program.'.format(type(e).__name__, e))
			return

		scanned, tmp_cache = [], []

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

			block['margin'] = (self.config['resale'] - block['price']) * block['stock']

			if (block['price'] > self.config['max_price'] or
				self.config.get('min_stock') and block['stock'] < self.config['min_stock'] or
				self.config.get('min_profit') and block['margin'] < self.config['min_profit']):
				continue

			cached = False
			# Update cache if profit margin changes
			for i, cached_block in enumerate(self.cache):
				if cached_block['ign'] == block['ign']:
					cached = True
					if cached_block['margin'] != block['margin']:
						self.sold.append(Fore.CYAN + Style.BRIGHT + block['ign'] + ' Has updated their price for ' + self.item)
						self.cache[i] = block
						scanned.append(block)
						break

			# Insert into the cache if they're not cached already
			if not cached:
				self.cache.append(block)
				scanned.append(block)

			tmp_cache.append(block)

		# Delete from cache if they were not scanned, aka item was sold
		new_cache = []
		if tmp_cache:
			for i, cached_block in enumerate(self.cache):
				found = False
				for block in tmp_cache:
					if block['ign'] == cached_block['ign']:
						new_cache.append(block)
						found = True
						break

				if not found:
					self.sold.append(Fore.YELLOW + Style.BRIGHT + '{} Has sold their {}.'.format(cached_block['ign'], self.item) + Style.RESET_ALL)

		self.cache = new_cache or self.cache

		self.output(scanned)

	def redisplay(self):
		self.output(self.cache, force_ding=False)

	def output(self, scanned, force_ding=True):
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
		if counter <= 0 and whispers or self.sold:
			counter = links
			print(Fore.RED + '-' * 150 + Style.RESET_ALL)

		if whispers or self.sold:
			if self.init:
				# don't play sound if initializing
				self.init = False
			elif force_ding and whispers and SNIPER_CONFIG['general-config']['ding']:
				def ding():
					playsound('resources/ding.mp3')
				thread = Thread(target=ding)
				thread.start()
			print(Fore.MAGENTA + self.item.center(150) + Style.RESET_ALL)
			for m in self.sold:
				print(m)
			self.sold = []

		for whisper, whisper_length, block in whispers:
			fore = blacklist.find(block['ign']) and Fore.RED or Fore.GREEN
			profit_str = 'PROFIT: ' + str(block['margin'])
			print(fore + whisper.ljust(145 - len(profit_str) - count_hangul(block['ign'])) + profit_str + Style.RESET_ALL)
		output_lock.release()