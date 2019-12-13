from colorama import Fore, Back, Style
from threading import Thread
import blacklist
import os
import init_sniper
from libs import PoENinja
import math
import signal
import init_sniper
from libs import colortext
import configloader

console_thread = None


def log_cmd(cmd):
    colortext.output('>> ' + str(cmd), 'console-logging')

def __unblock(name):
    """
    Unblocks user from blacklist
    """
    blacklist.remove(name)
    log_cmd('{} removed from the blacklist'.format(name))


def __block(name):
    """
    Makes their name red in display instead of green to show potential
    pricefixers/unresponsive players
    """
    blacklist.add(name)
    log_cmd('{} added to blacklist.'.format(name))


def __view_blacklist(raw_arg=None):
    """
    View who's currently blocked on the blacklist
    """
    bl = blacklist.get()
    if bl:
        log_cmd(', '.join(s.replace('\n', '') for s in blacklist.get()))
    else:
        log_cmd('Empty.')


def __exit(raw_arg=None):
    """
    Exits the program.
    """
    init_sniper.stop()
    os._exit(0)


def __clear_blacklist(raw_arg=None):
    """
    Clears the blacklist
    """
    blacklist.clear()
    log_cmd('Blacklist cleared')


def __exalt(raw_arg=None):
    """
    Converts chaos into exalts
    """
    chaos = int(raw_arg)
    exa_price = PoENinja.GetCurrencyData(configloader.get_league()).get('Exalted Orb')
    if exa_price:
        exa_price = exa_price['chaosEquivalent']
        price = math.floor(chaos / exa_price)
        remainder = (chaos / exa_price) - price
        log_cmd(
            '{} Exalted Orb, {} Chaos Orb'.format(
                price,
                math.floor(exa_price * remainder + 0.5)
            )
        )


def __redisplay(raw_arg=None):
    """
    Re-displays the current offers all at once
    """
    init_sniper.redisplay()
    log_cmd('Redisplay finished.')


def __commands(raw_arg=None):
    """
    Displays all available commands for use
    """
    for cmd, func in commands.items():
        log_cmd('{}: {}'.format(cmd, func.__doc__.strip()))

def __reload_config(raw_arg=None):
    """
    Reloads config
    """
    configloader.load()
    log_cmd('Config reloaded')


commands = {
    'block': __block,
    'unblock': __unblock,
    'view': __view_blacklist,
    'clear': __clear_blacklist,
    'exit': __exit,
    'exalt': __exalt,
    'redisplay': __redisplay,
    'commands': __commands,
    'reload': __reload_config
}


def keyboardInterruptHandler(signal, frame):
    __exit()


signal.signal(signal.SIGINT, keyboardInterruptHandler)


def start():
    def scanner():
        while True:
            try:
                __input = input().split(' ')
                func = commands.get(__input[0])
                if func:
                    colortext.output('> Command Given: ' + __input[0], 'console-command')
                    func(' '.join(__input[1:]))
                else:
                    colortext.output('> Invalid Command.', 'console-command')
            except (KeyboardInterrupt, SystemExit, EOFError):
                __exit()
    console_thread = Thread(target=scanner)
    console_thread.start()
