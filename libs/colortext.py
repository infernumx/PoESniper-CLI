from colorama import Fore, Back, Style
from configloader import config as SNIPER_CONFIG

def red(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.RED + brightness + txt + Style.RESET_ALL


def cyan(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.CYAN + brightness + txt + Style.RESET_ALL


def magenta(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.MAGENTA + brightness + txt + Style.RESET_ALL


def green(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.GREEN + brightness + txt + Style.RESET_ALL


def blue(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.BLUE + brightness + txt + Style.RESET_ALL


def yellow(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.YELLOW + brightness + txt + Style.RESET_ALL


color_table = {
    'yellow': yellow,
    'blue': blue,
    'green': green,
    'magenta': magenta,
    'cyan': cyan,
    'red': red
}

def get_config_color(msg_type):
    return SNIPER_CONFIG['general-config']['colors'][msg_type]


def get_color_func(msg_type):
    return color_table[get_config_color(msg_type)['color']]


def generate(txt, msg_type):
    color_func = get_color_func(msg_type)
    return color_func(
        txt,
        bright=get_config_color(msg_type)['bright']
    )


def output(txt, msg_type):
    color_func = get_color_func(msg_type)
    print(color_func(
            txt,
            bright=get_config_color(msg_type)['bright']
        )
    )