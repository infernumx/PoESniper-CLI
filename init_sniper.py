from driver_handler import DriverHandler
import time


watchers = []
driver = None


def init(config):
    global driver
    driver = DriverHandler(config)


def redisplay():
    driver.redisplay()


def stop():
    driver.stop()
