import requests
import json
from libs.JSONFilter import keep, delete

def GetChangeId():
	r = requests.get('https://poe.ninja/api/Data/GetStats')
	return json.loads(r.text)['next_change_id']

def GetFragmentData(league):
	r = requests.get('http://poe.ninja/api/Data/GetFragmentOverview?league={}'.format(league))
	if r and r.status_code == 200:
		j = json.loads(r.text)
		if j:
			data = {}
			for c in j['lines']:
				data[c['currencyTypeName']] = keep(c, ['chaosEquivalent'])
			return data

	return {}

def GetCurrencyData(league):
	r = requests.get('https://poe.ninja/api/Data/GetCurrencyOverview?league={}'.format(league))
	if r and r.status_code == 200:
		j = json.loads(r.text)
		if j:
			data = {}
			for c in j['lines']:
				data[c['currencyTypeName']] = keep(c, ['chaosEquivalent'])
			return data

	return {}

def GetMapData(league):
	r = requests.get('https://poe.ninja/api/Data/GetMapOverview?league={}'.format(league))
	if r and r.status_code == 200:
		j = json.loads(r.text)
		full_maps = {'Elder': [], 'Shaped': [], 'Normal': []}
		for map_x in j['lines']:
			map_type = map_x['baseType']
			filtered_map = {
				'chaos': map_x['chaosValue'],
				'exalt': map_x['exaltedValue'],
				'tier': map_x['mapTier'],
				'name': map_type,
			}
			if map_type.find('Elder') != -1:
				full_maps['Elder'].append(filtered_map)
			elif map_type.find('Shaped') != -1:
				full_maps['Shaped'].append(filtered_map)
			else:
				full_maps['Normal'].append(filtered_map)
		return full_maps

	return {}