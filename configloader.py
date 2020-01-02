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

colors = config['general-config']['colors']

def get_error_color():
	colors = get()['general-config']['colors']
	return colors.get('error') or {'color': 'red', 'bright': True}


def get_whisper_color():
	colors = get()['general-config']['colors']
	return colors.get('whisper') or {"color": "green", "bright": False}


def get_blocked_whisper_color():
	colors = get()['general-config']['colors']
	return colors.get('blocked-whisper') or {"color": "red", "bright": False}


def get_listing_update_color():
	colors = get()['general-config']['colors']
	return colors.get('listing-update') or {"color": "cyan", "bright": True},


def get_listing_remove_color():
	colors = get()['general-config']['colors']
	return colors.get('listing-remove') or {"color": "yellow", "bright": True}


def get_item_name_color():
	colors = get()['general-config']['colors']
	return colors.get('item-name') or {"color": "magenta", "bright": False}

def force_ding():
	return get()['general-config']['ding']

def get_league():
	return get()['general-config']['league']

def get_poesessid():
	return get()['general-config']['POESESSID']
