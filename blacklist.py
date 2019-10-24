import os

blacklist = []

if not os.path.exists('blacklist.txt'):
	with open('blacklist.txt', 'w') as f:
		pass
else:
	with open('blacklist.txt') as f:
		for line in f:
			blacklist.append(line)

def get():
	global blacklist
	return blacklist

def clear():
	global blacklist
	blacklist = []
	with open('blacklist.txt', 'w+') as f:
		pass

def find(name):
	global blacklist
	for _name in blacklist:
		if _name == name:
			return True
	return False

def add(name, do_save=True):
	global blacklist
	blacklist.append(name)
	if do_save:
		save()

def save():
	global blacklist
	with open('blacklist.txt', 'w+') as f:
		f.write('\n'.join(name for name in blacklist))