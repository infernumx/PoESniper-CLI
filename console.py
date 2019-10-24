from colorama import Fore, Back, Style 
from threading import Thread
import blacklist
import os
import init_sniper

console_thread = None

def log_cmd(str):
	print(Fore.RED + Style.BRIGHT + '>> ' + str + Style.RESET_ALL)

def __blacklist(name):
	blacklist.add(name)
	log_cmd('{} added to blacklist.'.format(name))

def __view_blacklist(*args):
	bl = blacklist.get()
	if bl:
		log_cmd(', '.join(s for s in blacklist.get()))
	else:
		log_cmd('Empty.')

def __exit(*args):
	init_sniper.stop()
	os._exit(0)

def __clear_blacklist(*args):
	blacklist.clear()
	log_cmd('Blacklist cleared')

commands = {
	'block': __blacklist,
	'view': __view_blacklist,
	'clear': __clear_blacklist,
	'exit': __exit
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
