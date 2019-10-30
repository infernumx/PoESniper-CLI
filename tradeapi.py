import requests
import json
import logging
import datetime
import time
import configloader
import blacklist
from libs import colortext
from libs.iterators import ItemIterator
from libs import hangul
from pprint import pprint
from apscheduler.schedulers.background import BlockingScheduler
from ratelimiter import RateLimiter
from threading import Lock, Thread

DEBUGGING = False

logger = logging.getLogger('apscheduler')
if not DEBUGGING:
    logger.setLevel(level=logging.CRITICAL)
    logger.disabled = True

rate_limiter = RateLimiter(max_calls=12, period=6)
output_lock = Lock()


def api_request(payload):
    # Return all ids listed from API
    id_request = requests.post(
        'https://www.pathofexile.com/api/trade/exchange/Blight',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    response_json = id_request.json()
    if not response_json.get('result'):
        return (response_json, -1)
    return (response_json['result'], response_json['id'])


def api_fetch(ids, search_id):
    # Fetch listings with generated id list, limited to 20
    query_url = 'https://www.pathofexile.com/api/trade/fetch/' \
                '{}?query={}&exchange'
    listings_request = requests.get(query_url.format(
            ids,
            search_id
        )
    )
    try:
        return listings_request.json()['result']
    except:
        print(ids, len(ids))
        print(search_id)
    return []


class ListingRetriever():
    def __init__(self, item_config):
        self.item_config = item_config
        self.cache = []

        self.RESULT_LIMIT = 40

        self.payload = {
            'exchange': {
                'status': {'option': 'online'},
                'have': ['chaos'],
                'want': [],
                'minimum': item_config.get('minimum_stock') or 1
            }
        }

        item_name = item_config['item'].lower().replace(' ', '-')
        item_name = item_name.replace("'", '')

        self.payload['exchange']['want'].append(item_name)

    def scheduler_task(self):
        with rate_limiter:
            self.refresh()

    def generate_id_str(self, results):
        if self.cache:
            id_list = [
                x for x in results if not x in set(
                    y['listing_id'] for y in self.cache
                )
            ][:20]
        else:
            id_list = results[:20]
        return (','.join(id_list), id_list)

    def refresh(self):
        # Search for new offers
        current_ids = []
        items = []
        for i in range(int(self.RESULT_LIMIT / 20)):
            # Request id list
            results, search_id = api_request(self.payload)
            if type(results) is dict and results.get('error'):
                print(results['error']['message'])
                return

            # Save all ids for comparison
            for result_id in results:
                current_ids.append(result_id)

            # ids[0] = string, ids[1] = list
            ids = self.generate_id_str(results)
            if len(ids[1]) == 0:
                continue

            tmp_items = api_fetch(ids[0], search_id)
            for item in ItemIterator(tmp_items):
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
                self.cache.append(item)
                items.append(item)

        self.output(items)

        # Remove old offers
        sold_items = [
            x for x in self.cache if not x['listing_id'] in current_ids
        ]
        for item in sold_items:
            colortext.output(
                '{} has sold their {} {}'.format(
                    item['seller'],
                    item['count'],
                    item['name']
                ),
                'listing-remove'
            )
        self.cache = [
            x for x in self.cache if x['listing_id'] in current_ids
        ]

    @staticmethod
    def ding():
        # Utilize a thread to avoid blocking while playing sound
        def play_ding():
            playsound('resources/ding.mp3')
        thread = Thread(target=play_ding)
        thread.start()

    def redisplay(self):
        self.output(self.cache, redisplay=True)

    def output(self, items, redisplay=False):
        global output_lock
        with output_lock:
            # Filter out items that don't match config specifications
            to_whisper = []
            for item in items:
                to_whisper.append((item, item['profit']))

            to_whisper.sort(key=lambda x: x[1], reverse=True)

            # Add separator for new offers
            if to_whisper:
                # Send ding sound for new offers
                if not redisplay and configloader.force_ding():
                    self.ding()
                colortext.output('-' * 150, 'logging')
                colortext.output(
                    self.item_config['item'].center(150),
                    'item-name'
                )

            for item, profit in to_whisper:
                profit_str = 'PROFIT: ' + str(profit)
                whisper = item['whisper']
                hangul_count = hangul.count_hangul(whisper)
                whisper = '{} {}'.format(
                    whisper.ljust(
                        145 - len(profit_str) - hangul_count
                    ),
                    profit_str
                )
                if (blacklist.find(item['seller']) and
                        blacklist.should_display(block['ign'])):
                    colortext.output(whisper, 'blocked-whisper')
                else:
                    colortext.output(whisper, 'whisper')


retrievers = []
scheduler = None
stop_refreshes = False

def run_refreshes():
    if stop_refreshes:
        scheduler.remove_job('scheduler_task')
        return

    for retriever in retrievers:
        retriever.refresh()

def setup(clear=False):
    global retrievers, scheduler
    if clear:
        retrievers = []

    for item_config in configloader.get()['item-filters']:
        retrievers.append(ListingRetriever(item_config))

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_refreshes,
        'interval',
        id='scheduler_task',
        seconds=5,
        next_run_time=datetime.datetime.now()
    )
    scheduler.start()


def redisplay():
    for retriever in retrievers:
        retriever.redisplay()


def stop():
    global stop_refreshes
    stop_refreshes = True
