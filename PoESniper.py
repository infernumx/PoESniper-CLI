import console
import init_sniper
from configloader import config as SNIPER_CONFIG


init_sniper.init(SNIPER_CONFIG['item-filters'])

console.start()
