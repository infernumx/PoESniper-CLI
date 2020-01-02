import requests
import ssl
import json
import configloader
import blacklist
from threading import Thread
from libs.iterators import ItemIterator
from PoESniperGUI import GUI
import websocket

gui = None

class LiveSearch():
    socket_id = 0

    def __init__(self, identifier, item_config):
        LiveSearch.socket_id += 1

        self.item_config = item_config
        self.socket_id = LiveSearch.socket_id
        self.identifier = identifier

        self.open_websocket()

    def open_websocket(self):
        websocket.enableTrace(True)

        league = configloader.get_league()

        # Get __cfduid for cookies
        session = requests.Session()
        session.get('https://www.pathofexile.com/')
        __cfduid = session.cookies.get_dict()['__cfduid']

        self.ws = websocket.WebSocketApp(
            "wss://www.pathofexile.com/api/trade/live/{}/{}".format(
                configloader.get_league(),
                self.identifier
            ),
            on_message=lambda ws, msg: self.on_message(msg),
            on_error=lambda ws, err: self.on_error(ws, err),
            on_close=lambda ws, code, reason: self.on_close(ws, code, reason),
            cookie='__cfduid={}; POESESSID={}'.format(
                __cfduid,
                configloader.get_poesessid()
            ),
            header=[
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                "AppleWebKit/537.36 (KHTML, like Gecko)"
                "Chrome/79.0.3945.88 Safari/537.36",

                "Accept: */*"
            ]
        )

        self.ws.on_open = lambda ws: self.on_open(ws)

        thread = Thread(target=self.ws.run_forever, kwargs={
            'origin': "https://www.pathofexile.com"
        })

        thread.setDaemon(True)
        thread.start()

    def parse_msg(self, items):
        for item in ItemIterator(items):
            if (self.item_config.get('max_price') and 
                    item['price'] > self.item_config['max_price']):
                continue
            
            profit = (
                (self.item_config['resale'] * item['count']) -
                item['full_cost']
            )

            item['profit'] = profit

            if (self.item_config.get('min_profit') and
                    profit < self.item_config['min_profit']):
                continue

            if (blacklist.find(item['seller']) and
                    blacklist.should_display(item['seller'])):
                gui.add_item(item)
            else:
                gui.add_item(item)

    def on_message(self, msg):
        msg = json.loads(msg)
        query_url = 'https://www.pathofexile.com/api/trade/fetch/' \
                    '{}?query={}&exchange'
        r = requests.get(
            query_url.format(
                ','.join(msg['new']),
                self.identifier
            )
        )

        self.parse_msg(r.json()['result'])

    def on_error(self, ws, err):
        print('Websocket #{} error: '.format(self.socket_id, err))

    def on_open(self, ws):
        print('Websocket #{} connected'.format(self.socket_id))

    def on_close(self, ws, code, reason):
        print('Websocket #{} closed [Code {}] | Reason: "{}"'.format(
            self.socket_id,
            code,
            reason
        ))
        self.open_websocket()

class MultiLiveSearcher():
    def __init__(self):
        self.live_searches = []

    def start(self, _gui):
        global gui
        gui = _gui
        for item_cfg in configloader.get()['item-filters']:
            identifier = self.get_identifier(item_cfg)
            if not identifier:
                continue
            self.live_searches.append(LiveSearch(identifier, item_cfg))

    @staticmethod
    def get_identifier(item_config):
        payload = {
            "query": {
                "status": {
                    "option": "online"
                },
                "type": item_config.get('item'),
                "stats": [
                    {
                        "type": "and",
                        "filters": []
                    }
                ],
                "filters": {
                    "trade_filters": {
                        "filters": {
                            "price": {
                                "option": "chaos"
                            }
                        }
                    }
                }
            },
            "sort": {
                "price": "asc"
            }
        }
        # Return all ids listed from API
        id_request = requests.post(
            'https://www.pathofexile.com/api/trade/search/' \
            + configloader.get_league(),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        response_json = id_request.json()
        if response_json.get('error'):
            if response_json['error']['code'] == 2:
                payload['query']['type'] = None
                payload['query']['name'] = item_config.get('item')
                id_request = requests.post(
                    'https://www.pathofexile.com/api/trade/search/' \
                    + configloader.get_league(),
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(payload)
                )
                response_json = id_request.json()
        return response_json.get('id')

def setup():
    GUI(MultiLiveSearcher())

setup()