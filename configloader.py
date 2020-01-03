import json

config = None

def load():
	global config
	with open('config.json') as f:
		config = json.loads(f.read())

load()

def get():
	global config
	return config

def force_ding():
	return get()['general-config']['ding']

def get_league():
	return get()['general-config']['league']

def get_poesessid():
	return get()['general-config']['POESESSID']
