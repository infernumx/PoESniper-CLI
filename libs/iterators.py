from pprint import pprint

class ItemIterator():
    def __init__(self, items):
        self.items = items
        self.limit = len(self.items)
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        else:
            item = self.items[self.current]
            if not item:
                self.current += 1
                return __next__(self)
            try:
                self.current += 1
                # Already been parsed by this iterator
                if item.get('listing_id'):
                    return item
                parsed = {
                    'listing_id': item['id'], 
                    'name': item['item']['typeLine'],
                    'count': item['listing']['price']['item']['stock'],
                    'price': item['listing']['price']['exchange']['amount'],
                    'seller': item['listing']['account']['lastCharacterName']
                }

                parsed['full_cost'] = parsed['price'] * parsed['count']

                parsed['whisper'] = item['listing']['whisper'].format(
                    parsed['count'],
                    parsed['full_cost']
                )

                return parsed
            except Exception as e:
                print('ItemIterator.__next__ failed (reason: {} {})'.format(
                        type(e).__name__,
                        e
                    )
                )
                print('Item:')
                pprint(item)
                print('Items:')
                pprint(self.items)
        return None
