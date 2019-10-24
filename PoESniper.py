import console
import init_sniper
import json

with open('config.json') as f:
	config = json.loads(f.read())

init_sniper.init(config)

console.start()