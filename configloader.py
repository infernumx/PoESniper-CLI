import json

with open('config.json') as f:
	config = json.loads(f.read())

colors = config['general-config']['colors']

def get_error_color():
	return colors.get('error') or {'color': 'red', 'bright': True}


def get_whisper_color():
	return colors.get('whisper') or {"color": "green", "bright": False}


def get_blocked_whisper_color():
	return colors.get('blocked-whisper') or {"color": "red", "bright": False}


def get_listing_update_color():
	return colors.get('listing-update') or {"color": "cyan", "bright": True},


def get_listing_remove_color():
	return colors.get('listing-remove') or {"color": "yellow", "bright": True}


def get_item_name_color():
	return colors.get('item-name') or {"color": "magenta", "bright": False}