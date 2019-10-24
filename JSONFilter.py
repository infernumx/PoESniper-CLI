def keep(data, params):
	ret = {}
	for param in params:
		if data.get(param) is not None:
			ret[param] = data[param]
	return ret

def delete(data, params):
	for param in params:
		if data.get(param) is not None:
			del data[param]
	return data