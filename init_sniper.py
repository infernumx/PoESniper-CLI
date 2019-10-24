from LinkWatcher import LinkWatcher
import time

watchers = []

def init(config):
	for link_config in config:
		watchers.append(LinkWatcher(**link_config))
		time.sleep(0.2)

def redisplay():
	for watcher in watchers:
		watcher.redisplay()

def stop():
	for watcher in watchers:
		watcher.stop()