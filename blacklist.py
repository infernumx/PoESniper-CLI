import os
from libs import colortext
import configloader

blacklist = []

if not os.path.exists('blacklist.txt'):
    with open('blacklist.txt', 'w', encoding='utf-8') as f:
        pass
else:
    with open('blacklist.txt', 'r', encoding='utf-8') as f:
        for line in f:
            blacklist.append(line.strip())


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
    blacklist.append(name.strip())
    if do_save:
        save()

def remove(name, do_save=True):
    global blacklist
    try:
        blacklist.remove(name)
    except:
        print(colortext.red('Could not find ' + name + ' in blacklist.'))
    if do_save:
        save()

def save():
    global blacklist
    with open('blacklist.txt', 'w+', encoding='utf-8') as f:
        f.write('\n'.join(name for name in blacklist))


def should_display(ign):
    if find(ign):
        return configloader.get()['general-config']['display-blocked']
    return True
