import console
import init_sniper

config = [
	{
		'identifier': 'BlnrowS8', # Sanctified Fossil,
		'config': {
			'max_price': 24,
			'resale': 32,
		},
		'interval': 15
	},
	{
		'identifier': 'mwjqKaS6', # Jagged Fossil,
		'config': {
			'max_price': 1,
			'resale': 4,
			'min_profit': 2
		},
		'interval': 15
	},
	{
		'identifier': 'O3k9W0IE', # Enchanted Fossil
		'config': {
			'max_price': 9,
			'resale': 14
		},
		'interval': 15
	}
]

init_sniper.init(config)

console.start()