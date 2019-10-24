from colorama import Fore, Back, Style 
from threading import Thread
import blacklist
import os
import init_sniper
import PoENinja
import math
import init_sniper

console_thread = None

def log_cmd(cmd):
	print(Fore.RED + Style.BRIGHT + '>> ' + str(cmd) + Style.RESET_ALL)

def __blacklist(name):
	"""
	Makes their name red in display instead of green to show potential pricefixers/unresponsive players
	"""
	blacklist.add(name)
	log_cmd('{} added to blacklist.'.format(name))

def __view_blacklist(raw_arg):
	"""
	View who's currently blocked on the blacklist
	"""
	bl = blacklist.get()
	if bl:
		log_cmd(', '.join(s for s in blacklist.get()))
	else:
		log_cmd('Empty.')

def __exit(raw_arg):
	"""
	Exits the program and cleans up selenium browsers
	"""
	init_sniper.stop()
	os._exit(0)

def __clear_blacklist(raw_arg):
	"""
	Clears the blacklist
	"""
	blacklist.clear()
	log_cmd('Blacklist cleared')

def __exalt(raw_arg):
	"""
	Converts chaos into exalts
	"""
	chaos = int(raw_arg)
	exa_price = PoENinja.GetCurrencyData('Blight').get('Exalted Orb')
	if exa_price:
		exa_price = exa_price['chaosEquivalent']
		price = math.floor(chaos / exa_price)
		remainder = (chaos / exa_price) - price
		log_cmd('{} Exalted Orb, {} Chaos Orb'.format(price, math.floor(exa_price * remainder + 0.5)))

def __redisplay(raw_arg):
	"""
	Re-displays the current offers all at once
	"""
	init_sniper.redisplay()
	log_cmd('Redisplay finished.')

def __commands(raw_arg):
	"""
	Displays all available commands for use
	"""
	for cmd, func in commands.items():
		log_cmd('{}: {}'.format(cmd, func.__doc__.strip()))

commands = {
	'block': __blacklist,
	'view': __view_blacklist,
	'clear': __clear_blacklist,
	'exit': __exit,
	'exalt': __exalt,
	'redisplay': __redisplay,
	'commands': __commands
}

def start():
	def scanner():
		while True:
			__input = input().split(' ')
			func = commands.get(__input[0])
			if func:
				print(Fore.CYAN + '> Command Given: ' + __input[0] + Style.RESET_ALL)
				func(' '.join(__input[1:]))
			else:
				print(Fore.CYAN + '> Invalid Command.' + Style.RESET_ALL)
	console_thread = Thread(target=scanner)
	console_thread.start()
