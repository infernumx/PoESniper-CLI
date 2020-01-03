import requests
import ssl
import json
import configloader
from threading import Thread
from libs.iterators import ItemIterator
from PoESniperGUI import GUI
from poesocket import PoESocket, PoEConnections

gui = None

class LiveSearch():
    def __init__(self, identifier, item_config):
        self.item_config = item_config
        self.identifier = identifier


    def start(self):
        self.socket = PoESocket(
            configloader.get_league(),
            self.identifier,
            configloader.get_poesessid(),
            on_message=self.on_message,
            on_connected=self.on_connected,
            on_disconnected=self.on_disconnected
        )

    def stop(self):
        self.socket.close_connection()

    def on_connected(self, socket):
        gui.update_element(
            key='_WEBSOCKET_CONNECTIONS_',
            value='Websockets Connected: {}'.format(
                PoEConnections.status_update()
            )
        )

    def on_disconnected(self, socket):
        gui.update_element(
            key='_WEBSOCKET_CONNECTIONS_',
            value='Websockets Connected: {}'.format(
                PoEConnections.status_update()
            )
        )

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
        items = [r.json()['result'][0]]

        for item in ItemIterator(items):
            if (self.item_config.get('max_price') and 
                    item['price'] > self.item_config['max_price']):
                continue

            if (self.item_config.get('min_stock') and
                    item['count'] < self.item_config['min_stock']):
                continue
            
            profit = (
                (self.item_config['resale'] * item['count']) -
                item['full_cost']
            )

            item['profit'] = profit

            if (self.item_config.get('min_profit') and
                    profit < self.item_config['min_profit']):
                continue

            gui.add_item(item)

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
            live_search = LiveSearch(identifier, item_cfg)
            self.live_searches.append(live_search)
            thread = Thread(target=live_search.start)
            thread.daemon = True
            thread.start()

    def stop(self):
        for live_search in self.live_searches:
            live_search.stop()

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
