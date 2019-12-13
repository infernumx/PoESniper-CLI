import requests
import json
import time
import websocket
import configloader
from threading import Thread

def POESESSID():
    return configloader.get()['general-config']['POESESSID']

class LiveSearch():
    socket_id = 0

    def __init__(self, identifier):
        LiveSearch.socket_id += 1
        self.socket_id = LiveSearch.socket_id
        self.identifier = identifier
        self.ws = websocket.WebSocketApp(
            "wss://www.pathofexile.com/api/trade/live/" \
            + configloader.get_league() + "/" + identifier,
            on_message=lambda ws, msg: self.on_message(msg),
            on_error=lambda ws, err: self.on_error(err),
            on_close=lambda ws: self.on_close(ws),
            on_open=lambda ws: self.on_open(ws),
            cookie='POESESSID=' + POESESSID()
        )
        thread = Thread(target=self.ws.run_forever)
        thread.start()

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
        print(r.json())

    def on_error(self, err):
        print(err)

    def on_open(self, ws):
        print('Websocket #{} connected'.format(self.socket_id))

    def on_close(self, ws):
        print('close')

class MultiLiveSearcher():
    def __init__(self):
        self.live_searches = []
        for item_cfg in configloader.get()['item-filters']:
            identifier = self.get_identifier(item_cfg)
            if not identifier:
                continue
            self.live_searches.append(LiveSearch(identifier))

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

MultiLiveSearcher()