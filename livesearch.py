import requests
import blacklist
import json
import datetime
import time
import websocket
from threading import Thread, Lock
from playsound import playsound
from bs4 import BeautifulSoup
>>>>>>> Stashed changes
from configloader import config as SNIPER_CONFIG
from libs import colortext
from libs import hangul
from libs import deepnodesearcher as nodesearch
import logging


DEBUGGING = True
output_lock = Lock()
TRADE_URL = 'http://poe.trade/search/'

class MultiLiveSearch():
    def __init__(self, item_filters):
        self.url = "arerigihahabeb"
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            'ws://live.poe.trade/' + self.url,
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, err: self.on_error(ws, err),
            on_close=lambda ws: self.on_close(ws),
            on_open=lambda ws: print(ws)
        )
        self.new_id = -1
        self.ws.run_forever()

    def on_message(self, ws, msg):
        print(msg)
        payload = {'id': self.new_id}
        r = requests.post('http:/poe.trade/search/' + self.url + "/live", data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        json_data = r.json()
        self.new_id = json_data['newid']
        if 'data' in json_data:
            soup = BeautifulSoup(json_data['data'], 'html.parser')
            items = soup.find_all("tbody", { "class" : "item" })
            
            for item in items:
                print('@'+item.get('data-ign') + ' Hi, I would like to buy your ' + item.get('data-name') + ' listed for ' + item.get('data-buyout') + ' in ' + item.get('data-league')+' (stash tab \"' + item.get('data-tab')+ '\"; position: left ' + item.get('data-x')+ ', top ' +item.get('data-y') +')')

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        pass

def start():
    def init():
        MultiLiveSearch(SNIPER_CONFIG['live-searches'])
    thread = Thread(target=init)
    thread.start()
    print('Websocket initialized')
    input()

start()

#print(requests.post('http://poe.trade/search/arerigihahabeb/live', data={'id': 1166667635}, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json())