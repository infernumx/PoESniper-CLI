import tradeapi
import time


def init():
    tradeapi.setup()

def redisplay():
    tradeapi.redisplay()


def stop():
    tradeapi.stop()
